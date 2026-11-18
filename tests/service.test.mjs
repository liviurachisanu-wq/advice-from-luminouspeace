import assert from 'node:assert/strict';
import {createCipheriv,randomBytes} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {resolveRequest} from '../service/worker.mjs';
const worker = {fetch: resolveRequest};

const text = [
  'tone.familiar=Notebook',
  'tone.reflective=Paperweight',
  'tone.playful=Kite',
  'order.category=alpha,beta,gamma',
  'label.category.alpha=First choice',
  'label.category.beta=Middle choice',
  'label.category.gamma=Last choice',
  'order.origin=north,east,west',
  'label.origin.north=North choice',
  'label.origin.east=East choice',
  'label.origin.west=West choice',
].join('\r\n');

function seal(clear = text) {
  const header = Buffer.from('4c50524601010000', 'hex');
  const key = randomBytes(32);
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  cipher.setAAD(header);
  const ciphertext = Buffer.concat([cipher.update(clear, 'utf8'), cipher.final()]);
  const packet = Buffer.concat([header, iv, cipher.getAuthTag(), ciphertext]);
  return {REFLEX_KEY:key.toString('base64'), REFLEX_ENVELOPE:packet.toString('base64')};
}

const base = {command:'ask him', extensive:true, dim:'tone', selector:'familiar'};
const env = seal();
function request(body = base, options = {}) {
  return new Request('https://unit.invalid/resolve', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body),
    ...options,
  });
}

test('requires both gates before reading any private configuration', async () => {
  for (const extra of [
    {command:undefined}, {extensive:undefined}, {extensive:false}, {extensive:'true'},
    {command:'ask liviu', extensive:true}, {command:'He told me to ask him'},
    {command:'“ask him”'}, {command:'ask him!'}, {command:'ask him\nwhat else?'}, {command:42},
  ]) {
    let accessed = false;
    const result = await worker.fetch(request({...base,...extra}), new Proxy({},{
      get() { accessed=true; throw new Error('Unexpected access'); },
    }));
    assert.equal(accessed,false);
    assert.equal(result.status,403);
    assert.deepEqual(await result.json(), {error:'Unavailable'});
    assert.equal(result.headers.get('Cache-Control'),'no-store');
  }
});

test('supports all tone cues, trims the command and ignores its case', async () => {
  for (const [selector,expected] of [['familiar','Notebook'],['reflective','Paperweight'],['playful','Kite']]) {
    const result=await worker.fetch(request({...base,command:'   AsK HiM  ',selector}),env);
    assert.equal(result.status,200);
    assert.deepEqual(await result.json(),{choice:expected});
    assert.equal(result.headers.get('Cache-Control'),'no-store');
  }
});

test('both download URLs serve the current edition under its new filename', async () => {
  const source = await readFile(new URL('../service/worker.mjs', import.meta.url), 'utf8');
  const archive = Buffer.from('UEsFBgAAAAAAAAAAAAAAAAAAAAAAAA==', 'base64');
  const bundled = source.replace('__ASK_HIM_SKILL_ZIP__', archive.toString('base64'));
  const {default: site} = await import('data:text/javascript;base64,' + Buffer.from(bundled).toString('base64'));
  const baseUrl = 'https://unit.invalid/';
  const filename = 'advice-from-luminouspeace-ask-him.zip';
  const oldFilename = 'advice-from-luminouspeace-ask-liviu.zip';
  const page = await site.fetch(new Request(baseUrl), {});
  const html = await page.text();
  assert.ok(html.includes(`href="/${filename}"`));
  assert.ok(!html.includes(oldFilename));
  assert.ok(html.includes('“him” means LuminousPeace'));
  for (const path of [filename, oldFilename]) {
    for (const method of ['GET', 'HEAD']) {
      const response = await site.fetch(new Request(baseUrl + path, {method}), {});
      assert.equal(response.status, 200);
      assert.equal(response.headers.get('Content-Disposition'), `attachment; filename="${filename}"`);
      assert.equal(response.headers.get('Content-Type'), 'application/zip');
      assert.equal(Number(response.headers.get('Content-Length')), archive.length);
      assert.deepEqual(Buffer.from(await response.arrayBuffer()), method === 'GET' ? archive : Buffer.alloc(0));
    }
  }
});

test('ranks available choices in private order, honors inclusive and missing floors', async () => {
  for (const [dim,selector,floor,expected] of [
    ['category','gamma, beta, alpha',undefined,'First choice'],
    ['category','beta,gamma','beta','Middle choice'],
    ['category','alpha,gamma','beta','Last choice'],
    ['origin','east,north','east','East choice'],
    ['origin','west',undefined,'West choice'],
    ['origin','north','east',null],
    ['category','delta',undefined,null],
    ['category','alpha,delta',undefined,null],
    ['category','alpha,beta','invalid',null],
  ]) {
    const result=await worker.fetch(request({...base,dim,selector,floor}),env);
    assert.equal(result.status,expected ? 200 : 404);
    assert.deepEqual(await result.json(),expected ? {choice:expected} : {error:'Unavailable'});
  }
});

test('rejects unknown parameters, dimensions and malformed selectors before decryption', async () => {
  for (const extra of [
    {transcript:'example'}, {dim:'other'}, {selector:'all'}, {floor:'alpha'},
    {dim:'category',selector:'a,,b'}, {dim:'category',selector:''},
    {dim:'category',selector:'a, a'},
    {dim:'origin',selector:['east']}, {dim:'origin',selector:'east',floor:'bad.id'},
    {dim:'category',selector:Array(34).fill('x').join(',')},
  ]) {
    const result=await worker.fetch(request({...base,...extra}), {});
    assert.equal(result.status,400);
    assert.deepEqual(await result.json(),{error:'Unavailable'});
  }
});

test('rejects excessive bodies, invalid JSON, methods, and paths', async () => {
  for (const payload of [' '.repeat(2_050), 'not json']) {
    const result=await worker.fetch(request(base,{body:payload}), {});
    assert.equal(result.status,400);
  }
  assert.equal((await worker.fetch(new Request('https://unit.invalid/resolve'), {})).status,405);
  assert.equal((await worker.fetch(new Request('https://unit.invalid/'), {})).status,404);
  assert.equal((await worker.fetch(request(base,{headers:{'Content-Type':'text/plain'}}), {})).status,415);
  const tooLarge=await worker.fetch(request(base,{headers:{'Content-Type':'application/json','Content-Length':'999999'}}),{});
  assert.equal(tooLarge.status,400);
});

test('rejects absent, corrupted, or unauthenticated configuration without revealing its contents', async () => {
  const invalidHeader=Buffer.from(env.REFLEX_ENVELOPE,'base64'); invalidHeader[3]^=1;
  const invalidTag=Buffer.from(env.REFLEX_ENVELOPE,'base64'); invalidTag[20]^=1;
  const invalidData=Buffer.from(env.REFLEX_ENVELOPE,'base64'); invalidData[36]^=1;
  for (const config of [
    {}, {...env,REFLEX_KEY:randomBytes(32).toString('base64')},
    {...env,REFLEX_KEY:randomBytes(16).toString('base64')},
    ...[invalidHeader,invalidTag,invalidData].map(data=>({...env,REFLEX_ENVELOPE:data.toString('base64')})),
    {...env,REFLEX_ENVELOPE:'*'}, {...env,REFLEX_ENVELOPE:'A'.repeat(90_000)},
    seal('tone.familiar=one\ntone.familiar=two'), seal('tone.familiar=broken\rrecord'),
    seal('# invalid record\ntone.familiar=sample'), seal('tone.familiar=sample\0'),
  ]) {
    const result=await worker.fetch(request(),config);
    assert.equal(result.status,503);
    assert.deepEqual(await result.json(),{error:'Unavailable'});
  }
});

test('interoperable record preserves UTF-8 labels and accepts all bounded ID characters', async () => {
  assert.equal(worker.fetch, resolveRequest);
  const synthetic = seal('\uFEFForder.category=-red,42_accent\nlabel.category.42_accent= Élan = blue ');
  const result = await resolveRequest(request({...base, dim:'category', selector:'42_accent', floor:'-red'}), synthetic);
  assert.equal(result.status, 200);
  assert.deepEqual(await result.json(), {choice:' Élan = blue '});
});
