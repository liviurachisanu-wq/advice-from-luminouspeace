"""Create a GitHub draft from the checkout of its existing version tag."""
from pathlib import Path
import json
import re
import subprocess

from build import check_generated, outputs
from privacy_guard import scan_repository


def release_assets(root):
    generated = outputs(root)
    check_generated(root, generated)
    scan_repository(root)
    return [root / name for name in sorted(generated) if name.startswith('downloads/')]


def require_tag_checkout(root, tag):
    def resolve(ref):
        result = subprocess.run(
            ['git', 'rev-parse', '--verify', ref + '^{commit}'],
            cwd=root, capture_output=True, text=True,
        )
        if result.returncode:
            raise ValueError(f'Cannot resolve release commit: {ref}')
        return result.stdout.strip()

    if resolve('HEAD') != resolve(f'refs/tags/{tag}'):
        raise ValueError(f'HEAD must match the commit tagged {tag}')


def release_notes(changelog, tag):
    headings = list(re.finditer(r'^## (.+)$', changelog, re.MULTILINE))
    matches = [
        index for index, heading in enumerate(headings)
        if re.match(re.escape(tag) + r'(?:\s|$)', heading[1])
    ]
    if len(matches) != 1:
        raise ValueError(f'Expected one changelog section for {tag}')
    index = matches[0]
    end = headings[index + 1].start() if index + 1 < len(headings) else len(changelog)
    notes = changelog[headings[index].end():end].strip()
    if not notes:
        raise ValueError(f'Empty changelog section for {tag}')
    return notes + '\n'


def main():
    root = Path(__file__).resolve().parents[1]
    meta = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    tag = 'v' + meta['version']
    require_tag_checkout(root, tag)
    notes = release_notes((root / 'CHANGELOG.md').read_text(encoding='utf-8'), tag)
    assets = release_assets(root)
    subprocess.run(
        ['gh', 'release', 'create', tag, '--verify-tag', '--draft',
         '--title', meta['name'] + ' ' + tag, '--notes-file', '-', *map(str, assets)],
        input=notes.encode('utf-8'), cwd=root, check=True,
    )


if __name__ == '__main__':
    main()
