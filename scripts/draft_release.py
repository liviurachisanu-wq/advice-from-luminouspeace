"""Create a GitHub draft only; requires a reviewed, existing version tag."""
from pathlib import Path
import json,subprocess
from build import outputs
from privacy_guard import scan_repository

def release_assets(root):
    expected = {name for name in outputs(root) if name.startswith('downloads/')}
    actual = {'downloads/' + path.name for path in (root/'downloads').iterdir()}
    if actual != expected or any(not (root/name).is_file() for name in expected):
        raise ValueError('Download directory must contain only the generated release assets')
    generated = outputs(root)
    for name in expected:
        if (root/name).read_bytes() != generated[name]:
            raise ValueError('Release asset differs from generated output: ' + name)
    scan_repository(root)
    return [root/name for name in sorted(expected)]
def main():
    root=Path(__file__).resolve().parents[1]
    meta=json.loads((root/'release.json').read_text())
    assets=release_assets(root)
    tag='v'+meta['version']
    subprocess.run(['gh','release','create',tag,'--verify-tag','--draft','--title',meta['name']+' '+tag,'--notes-file','CHANGELOG.md',*map(str,assets)],cwd=root,check=True)

if __name__ == '__main__':
    main()
