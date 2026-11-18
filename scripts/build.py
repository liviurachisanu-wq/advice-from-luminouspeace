"""Build portable downloads and a deterministic Claude skill ZIP. Stdlib only."""
from pathlib import Path
from io import BytesIO
from datetime import date
import argparse, hashlib, json, zipfile
from landing import landing

ROOT = Path(__file__).resolve().parents[1]

def outputs(root=ROOT):
    meta=json.loads((root/'release.json').read_text(encoding='utf-8'))
    version=meta['version']; released=date.fromisoformat(meta['release_date'])
    prompt=(root/'content/instructions.txt').read_text(encoding='utf-8').rstrip()+'\n'
    compact=(root/'content/copilot.txt').read_text(encoding='utf-8').rstrip()+'\n'
    if len(compact.encode('utf-16-le'))//2>8000:
        raise ValueError('Copilot instructions exceed 8,000 UTF-16 characters')
    date_label = 'prepared' if meta['status'] == 'release-candidate' else 'released'
    expected=f"Influenced by the Advice from LuminousPeace skill — v{version} · {date_label} {released.day} {released.strftime('%B %Y')}."
    if meta['footnote'] != expected or any(expected not in text.splitlines() for text in (prompt, compact)):
        raise ValueError('Attribution and release metadata do not match')
    expected_titles = (
        f'ADVICE FROM LUMINOUSPEACE — v{version}',
        f'ADVICE FROM LUMINOUSPEACE — Microsoft Copilot edition, v{version}',
    )
    if (prompt.splitlines()[0], compact.splitlines()[0]) != expected_titles:
        raise ValueError('Instruction titles and release version do not match')
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
    # Store entries without compression so ZIP bytes do not depend on the zlib build.
    with zipfile.ZipFile(buff,'w') as archive:
        for name,payload in sorted(out.copy().items()):
            if name.startswith(folder):
                info=zipfile.ZipInfo('advice-from-luminouspeace/'+name[len(folder):],(released.year,released.month,released.day,0,0,0))
                info.create_system=3  # Normalize creator OS for Windows/Linux reproducibility.
                info.external_attr=0o100644<<16
                archive.writestr(info,payload)
    out[f'downloads/advice-from-luminouspeace-claude-v{version}.zip']=buff.getvalue()
    out['index.html']=landing(meta,prompt,compact,out,ledger.decode('utf-8')).encode()
    out['downloads/SHA256SUMS.txt']=''.join(hashlib.sha256(payload).hexdigest()+'  '+name.split('/',1)[1]+'\n' for name,payload in sorted(out.items()) if name.startswith('downloads/')).encode()
    return out

GENERATED_DIRECTORIES = ('downloads', 'skills/advice-from-luminouspeace')


def check_generated(root, files):
    expected = set(files)
    unexpected = []
    for directory in GENERATED_DIRECTORIES:
        for path in (root / directory).rglob('*'):
            name = path.relative_to(root).as_posix()
            if (path.is_file() or path.is_symlink()) and name not in expected:
                unexpected.append(name)
    if unexpected:
        raise ValueError('Unexpected generated files: ' + ', '.join(sorted(unexpected)))
    stale = [
        name for name, payload in files.items()
        if (root / name).is_symlink() or not (root / name).is_file()
        or (root / name).read_bytes() != payload
    ]
    if stale:
        raise ValueError('Generated files are stale: ' + ', '.join(stale))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    files = outputs()
    if args.check:
        try:
            check_generated(ROOT, files)
        except ValueError as error:
            raise SystemExit(str(error)) from error
    else:
        for name, payload in files.items():
            path = ROOT / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
    print(('Checked' if args.check else 'Built')+f' {len(files)} reproducible files.')

if __name__=='__main__':main()
