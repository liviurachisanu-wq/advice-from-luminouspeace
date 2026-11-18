const HEADER = Uint8Array.of(0x4c, 0x50, 0x52, 0x46, 1, 1, 0, 0);
const PREFIX_SIZE = HEADER.length + 12 + 16;
const MAX_PLAINTEXT = 65_536;
const MAX_BODY = 2_048;
const ID = /^[a-z0-9_-]{1,48}$/;
const TONES = new Set(['familiar', 'reflective', 'playful']);
const FIELDS = new Set(['command', 'extensive', 'dim', 'selector', 'floor']);
const UTF8 = new TextDecoder('utf-8', { fatal: true });

function respond(status, body) {
  return Response.json(body, {
    status,
    headers: { 'Cache-Control': 'no-store', 'X-Content-Type-Options': 'nosniff' },
  });
}

function unavailable(status) {
  return respond(status, { error: 'Unavailable' });
}

async function parseRequest(request) {
  if (!request.body || Number(request.headers.get('Content-Length')) > MAX_BODY) {
    throw new Error('Body unavailable');
  }
  const reader = request.body.getReader();
  const buffer = new Uint8Array(MAX_BODY);
  let length = 0;
  try {
    while (true) {
      const chunk = await reader.read();
      if (chunk.done) break;
      if (length + chunk.value.length > MAX_BODY) {
        await reader.cancel();
        throw new Error('Body too large');
      }
      buffer.set(chunk.value, length);
      length += chunk.value.length;
    }
    return JSON.parse(UTF8.decode(buffer.subarray(0, length)));
  } finally {
    reader.releaseLock();
  }
}

function idList(value) {
  if (typeof value !== 'string' || value.length === 0 || value.length > 1024) return null;
  const ids = value.split(',').map(id => id.trim());
  if (ids.length > 32 || new Set(ids).size !== ids.length || !ids.every(id => ID.test(id))) return null;
  return ids;
}

function validSelector({ dim, selector, floor }) {
  if (floor !== undefined && (typeof floor !== 'string' || (floor !== '' && !ID.test(floor)))) {
    return false;
  }
  if (dim === 'tone') return TONES.has(selector) && !floor;
  return (dim === 'category' || dim === 'origin') && idList(selector) !== null;
}

function decodeBase64(value, maxBytes) {
  if (typeof value !== 'string' || value.length > Math.ceil(maxBytes / 3) * 4) {
    throw new Error('Invalid encoding');
  }
  const binary = atob(value);
  if (binary.length > maxBytes) throw new Error('Data too long');
  return Uint8Array.from(binary, character => character.charCodeAt(0));
}

function parseRecord(text) {
  if (/[\u0000-\u0009\u000b\u000c\u000e-\u001f\u007f]|\r(?!\n)/u.test(text)) {
    throw new Error('Invalid character in record');
  }
  const fields = new Map();
  for (const line of text.split(/\r?\n/)) {
    if (!line) continue;
    const equals = line.indexOf('=');
    if (equals < 1) throw new Error('Invalid record');
    const field = line.slice(0, equals);
    if (fields.has(field)) throw new Error('Duplicate field');
    fields.set(field, line.slice(equals + 1));
  }
  return fields;
}

async function readRecord(env) {
  const packet = decodeBase64(env.REFLEX_ENVELOPE, PREFIX_SIZE + MAX_PLAINTEXT);
  if (packet.length <= PREFIX_SIZE || !HEADER.every((byte, i) => packet[i] === byte)) {
    throw new Error('Invalid envelope');
  }
  const rawKey = decodeBase64(env.REFLEX_KEY, 32);
  let key;
  try {
    if (rawKey.length !== 32) throw new Error('Invalid key length');
    key = await crypto.subtle.importKey('raw', rawKey, 'AES-GCM', false, ['decrypt']);
  } finally {
    rawKey.fill(0);
  }
  const sealed = new Uint8Array(packet.length - HEADER.length - 12);
  sealed.set(packet.subarray(PREFIX_SIZE));
  sealed.set(packet.subarray(PREFIX_SIZE - 16, PREFIX_SIZE), sealed.length - 16);
  const plaintext = new Uint8Array(await crypto.subtle.decrypt({
    name: 'AES-GCM',
    iv: packet.subarray(HEADER.length, HEADER.length + 12),
    additionalData: HEADER,
    tagLength: 128,
  }, key, sealed));
  try {
    return parseRecord(UTF8.decode(plaintext));
  } finally {
    plaintext.fill(0);
  }
}

function selectChoice(record, {dim, selector, floor}) {
  let label;
  if (dim === 'tone') {
    label = record.get('tone.' + selector);
  } else {
    const order = idList(record.get('order.' + dim));
    if (!order) return null;
    const from = floor ? order.indexOf(floor) : 0;
    if (from < 0) return null;
    const candidates = new Set(idList(selector));
    if ([...candidates].some(id => !order.includes(id))) return null;
    const match = order.slice(from).find(id => candidates.has(id));
    if (match === undefined) return null;
    label = record.get('label.' + dim + '.' + match);
  }
  return label && label.length <= 128 && !/[\u0000-\u001f\u007f]/u.test(label) ? label : null;
}

export async function resolveRequest(request, env) {
  if (new URL(request.url).pathname !== '/resolve') return unavailable(404);
  if (request.method !== 'POST') return unavailable(405);
  if (request.headers.get('Content-Type')?.split(';')[0].trim().toLowerCase() !== 'application/json') {
    return unavailable(415);
  }
  let input;
  try {
    input = await parseRequest(request);
  } catch {
    return unavailable(400);
  }
  if (!input || Array.isArray(input) || typeof input !== 'object' ||
      typeof input.command !== 'string' || input.command.trim().toLowerCase() !== 'ask him' ||
      input.extensive !== true) {
    return unavailable(403);
  }
  if (Object.keys(input).some(field => !FIELDS.has(field)) || !validSelector(input)) {
    return unavailable(400);
  }
  try {
    const choice = selectChoice(await readRecord(env), input);
    return choice === null ? unavailable(404) : respond(200, {choice});
  } catch {
    return unavailable(503);
  }
}

// Build markers are replaced with the exact bytes of the downloadable edition.
const skillZip = '__ASK_HIM_SKILL_ZIP__';
const sealedPreferences = '__ASK_HIM_SEALED_PREFERENCES__';
const downloadName = 'advice-from-luminouspeace-ask-him.zip';
const downloadPath = '/' + downloadName;
const previousDownloadPath = '/advice-from-luminouspeace-ask-liviu.zip';
const landing = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Ask Him · Advice from LuminousPeace</title>
<style>html{font:18px/1.6 system-ui,sans-serif;color:#153b36;background:#f5f4ee}body{max-width:36rem;margin:12vh auto;padding:0 1.5rem}h1{font:normal clamp(3rem,10vw,5rem)/1 Georgia,serif;letter-spacing:-.05em;margin:.35em 0}p{margin:1.3em 0}a{display:inline-block;border-radius:.35em;background:#174b40;color:white;padding:.65em 1.05em;text-underline-offset:.2em}a:focus-visible{outline:3px solid #97672c;outline-offset:4px}small{color:#435b55}</style>
</head><body><main><small>Advice from LuminousPeace</small><h1>Ask Him</h1><p>After you’ve worked through a subject together, say <strong>“ask him”</strong> to request a pick inspired by LuminousPeace. Here, “him” means LuminousPeace.</p><p>Your assistant judges familiarity from this chat. For a supported choice, it sends a short lookup and receives one answer. The skill keeps the conversation in your chat.</p><p><a href="${downloadPath}" download>Download the skill</a></p><small>Ask Him edition of v0.7.2 · The optional lookup requires a host that allows HTTPS requests.</small></main></body></html>`;

export default {
  async fetch(request, env) {
    const path = new URL(request.url).pathname;
    if (path === '/resolve') {
      return resolveRequest(request, {get REFLEX_KEY() { return env.REFLEX_KEY; }, REFLEX_ENVELOPE: sealedPreferences});
    }
    if (path !== '/' && path !== downloadPath && path !== previousDownloadPath) return unavailable(404);
    if (request.method !== 'GET' && request.method !== 'HEAD') return unavailable(405);
    if (path === '/') {
      return new Response(request.method === 'HEAD' ? null : landing, {headers:{
        'Content-Type':'text/html; charset=utf-8',
        'Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'",
        'Referrer-Policy':'no-referrer',
        'X-Content-Type-Options':'nosniff',
      }});
    }
    const bytes = decodeBase64(skillZip, 512 * 1024);
    return new Response(request.method === 'HEAD' ? null : bytes, {headers:{
      'Content-Type':'application/zip',
      'Content-Disposition':`attachment; filename="${downloadName}"`,
      'Content-Length':String(bytes.byteLength),
      'Cache-Control':'no-cache',
      'X-Content-Type-Options':'nosniff',
    }});
  },
};
