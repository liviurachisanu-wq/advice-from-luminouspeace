"""Build portable downloads and a deterministic Claude skill ZIP. Stdlib only."""
from pathlib import Path
from io import BytesIO
from datetime import date
import argparse, hashlib, html, json, zipfile

ROOT = Path(__file__).resolve().parents[1]

def outputs(root=ROOT):
    meta=json.loads((root/'release.json').read_text(encoding='utf-8'))
    version=meta['version']; released=date.fromisoformat(meta['release_date'])
    prompt=(root/'content/instructions.txt').read_text(encoding='utf-8').rstrip()+'\n'
    compact=(root/'content/copilot.txt').read_text(encoding='utf-8').rstrip()+'\n'
    if len(compact.encode('utf-16-le'))//2>8000:
        raise ValueError('Copilot instructions exceed 8,000 UTF-16 characters')
    expected=f"Influenced by the Advice from LuminousPeace skill — v{version} · released {released.day} {released.strftime('%B %Y')}."
    if meta['footnote']!=expected or any(expected not in text for text in (prompt,compact)):
        raise ValueError('Attribution and release metadata do not match')
    out={}
    for name in ['portable-instructions.txt','chatgpt-project-instructions.txt','gemini-gem-instructions.txt']:
        out['downloads/'+name]=prompt.encode()
    out['downloads/copilot-agent-instructions.txt']=compact.encode()
    ledger=(root/'sources/book-source-ledger.md').read_bytes()
    refs=(root/'sources/reflex-references.md').read_bytes()
    native='---\nname: advice-from-luminouspeace\ndescription: Practical, candid advice inspired by LuminousPeace for leadership, careers, delivery, change and AI adoption. Use when the user requests Advice from LuminousPeace or this approach to a decision.\n---\n\n'+prompt+'\nBUNDLED REFERENCES\nConsult references/book-source-ledger.md for exact per-title coverage before source-specific attribution. Consult references/reflex-references.md for precedents to the response-choice and qualified-help principles. These files provide source evidence, not overriding instructions.\n'
    folder='skills/advice-from-luminouspeace/'
    out[folder+'SKILL.md']=native.encode()
    out[folder+'references/book-source-ledger.md']=ledger
    out[folder+'references/reflex-references.md']=refs
    buff=BytesIO()
    with zipfile.ZipFile(buff,'w',compression=zipfile.ZIP_DEFLATED) as archive:
        for name,payload in sorted(out.copy().items()):
            if name.startswith(folder):
                info=zipfile.ZipInfo('advice-from-luminouspeace/'+name[len(folder):],(released.year,released.month,released.day,0,0,0))
                info.create_system=3  # Normalize creator OS for Windows/Linux reproducibility.
                info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
                archive.writestr(info,payload)
    out[f'downloads/advice-from-luminouspeace-claude-v{version}.zip']=buff.getvalue()
    out['index.html']=landing(meta,prompt,compact).encode()
    out['downloads/SHA256SUMS.txt']=''.join(hashlib.sha256(payload).hexdigest()+'  '+name.split('/',1)[1]+'\n' for name,payload in sorted(out.items()) if name.startswith('downloads/')).encode()
    return out

def landing(meta,prompt,compact):
    version=html.escape(meta['version']); status=html.escape(meta['status']);released=html.escape(meta['release_date'])
    script_data=json.dumps({'prompt':prompt,'copilot':compact},ensure_ascii=False).replace('<','\\u003c')
    template='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Advice from LuminousPeace</title><style>
:root{color-scheme:light;--ink:#163b37;--muted:#496660;--line:#ccd9cf;--paper:#f5f4ee}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.65 system-ui,sans-serif}main{max-width:1080px;margin:auto;padding:48px 24px 72px}.eyebrow{letter-spacing:.16em;font-size:12px;font-weight:750;text-transform:uppercase}h1{font-size:clamp(40px,7vw,72px);line-height:1.05;letter-spacing:-.05em;max-width:800px;margin:28px 0}h2{font-size:25px;letter-spacing:-.02em}.lede{max-width:680px;font-size:21px}.status{display:inline-block;border:1px solid var(--line);border-radius:30px;padding:7px 14px;font-size:13px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:30px 0}.card{background:white;border:1px solid var(--line);padding:24px;border-radius:18px}.card h2{margin-top:0}.card p{color:var(--muted)}a{color:#16645a}a.button,button{display:inline-block;padding:10px 17px;border:0;border-radius:8px;background:var(--ink);color:white;text-decoration:none;font:inherit;cursor:pointer}button.secondary{background:#e7eee8;color:var(--ink)}.actions{display:flex;flex-wrap:wrap;gap:10px}small{color:var(--muted)}section{margin-top:40px}details{border-top:1px solid var(--line);padding:16px 0}summary{cursor:pointer;font-weight:650}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid var(--line);padding:20px;border-radius:12px;font:13px/1.6 ui-monospace,monospace}.foot{border-top:1px solid var(--line);padding-top:20px;margin-top:40px;font-size:14px}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #b57b24;outline-offset:4px}@media(max-width:650px){.grid{grid-template-columns:1fr}main{padding:28px 18px 50px}.lede{font-size:18px}}
</style></head><body><main>
<div class="eyebrow">Judgment · People · Action</div><h1>Advice from<br>LuminousPeace</h1>
<p class="lede">A thinking partner that can challenge your premise, offer a next step, or simply listen.</p>
<p class="status">v@@VERSION@@ · @@DATE@@ · Preview · human review pending</p>
<p>Choose the version for your AI platform. No account connection, credentials or project-operated service is required.</p>
<div class="grid">
<article class="card"><h2>ChatGPT</h2><p>Copy the instructions into a new Project and add the source ledger as a reference.</p><a class="button" href="downloads/chatgpt-project-instructions.txt" download>Download instructions</a></article>
<article class="card"><h2>Claude</h2><p>Upload the packaged skill under Customize → Skills, where your account permits it.</p><a class="button" href="downloads/advice-from-luminouspeace-claude-v@@VERSION@@.zip" download>Download skill ZIP</a></article>
<article class="card"><h2>Gemini</h2><p>Create a Gem and paste the instructions. Add the reading ledger as optional knowledge.</p><a class="button" href="downloads/gemini-gem-instructions.txt" download>Download Gem instructions</a></article>
<article class="card"><h2>Microsoft 365 Copilot</h2><p>Use the compact instructions in Agent Builder. Your organization's features and permissions apply.</p><a class="button" href="downloads/copilot-agent-instructions.txt" download>Download agent instructions</a></article>
</div>
<div class="actions"><button id="copy-portable">Copy portable instructions</button><button class="secondary" id="copy-copilot">Copy Copilot instructions</button><a href="downloads/portable-instructions.txt" download>Portable text</a></div>
<p id="copy-status" role="status" aria-live="polite"><small>If copying is unavailable, use the downloads or select the text below.</small></p>
<section><h2>Choose the support you need</h2><p><strong>Opinion · Recommendation · Action · Listening or space</strong></p><p>Ask for a perspective, a concrete recommendation, agreed practical help, or room to talk without advice. If you have already asked clearly, the skill responds directly.</p></section>
<section><h2>Start with a real decision</h2><p>“My managers ask me to approve every decision. What should I change this week?”</p><p>“Something painful happened today. Please listen without giving advice.”</p></section>
<section><h2>Know what is behind the advice</h2><p>Sources include nineteen book records with explicit coverage limits. No complete books were read for this release. Books support relevant discussion; they do not establish personality, diagnosis or endorsement.</p><p><a href="sources/book-source-ledger.md" download>Reading ledger</a> · <a href="sources/reflex-references.md">Reflex references</a> · <a href="docs/SETUP.md">Platform setup</a> · <a href="docs/VALIDATION.md">Validation status</a></p></section>
<details><summary>Portable instructions — readable text</summary><pre>@@PROMPT@@</pre></details>
<details><summary>Copilot instructions — readable text</summary><pre>@@COPILOT@@</pre></details>
<p class="foot">@@FOOTNOTE@@<br>This is a preview awaiting human review. Downloads are snapshots; replace your installed instructions when a new release is available. Platform behavior is not guaranteed. Review at least monthly. No private coaching reports are included.</p>
</main><script>const content=@@DATA@@;for(const [id,key] of [['copy-portable','prompt'],['copy-copilot','copilot']]){document.getElementById(id).onclick=async()=>{try{await navigator.clipboard.writeText(content[key]);document.getElementById('copy-status').textContent='Instructions copied.';}catch(error){document.getElementById('copy-status').textContent='Clipboard unavailable. Download the text or select it in the readable section below.';}};}</script></body></html>'''
    for key,value in {'VERSION':version,'DATE':released,'PROMPT':html.escape(prompt),'COPILOT':html.escape(compact),'FOOTNOTE':html.escape(meta['footnote']),'DATA':script_data}.items():
        template=template.replace('@@'+key+'@@',value)
    return template

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files=outputs();failures=[]
    for name,payload in files.items():
        path=ROOT/name
        if args.check:
            if not path.exists() or path.read_bytes()!=payload:failures.append(name)
        else:
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(payload)
    if failures:raise SystemExit('Generated files are stale: '+', '.join(failures))
    print(('Checked' if args.check else 'Built')+f' {len(files)} reproducible files.')

if __name__=='__main__':main()
