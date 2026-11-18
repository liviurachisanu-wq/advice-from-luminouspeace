"""Create a GitHub draft from the checkout of its existing version tag."""
from pathlib import Path
import json
import re
import subprocess
import tempfile

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

    commit = resolve(f'refs/tags/{tag}')
    if resolve('HEAD') != commit:
        raise ValueError(f'HEAD must match the commit tagged {tag}')
    status = subprocess.check_output(
        ['git', 'status', '--porcelain=v1', '-z', '--untracked-files=no'],
        cwd=root,
    )
    if status:
        raise ValueError('Release requires a clean index and tracked working tree')
    return commit


def tagged_blob(root, commit, path):
    return subprocess.check_output(['git', 'cat-file', 'blob', f'{commit}:{path}'], cwd=root)


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


def main(root=Path(__file__).resolve().parents[1]):
    meta = json.loads((root / 'release.json').read_text(encoding='utf-8'))
    edition = meta.get('edition')
    tag = edition['tag'] if edition else 'v' + meta['version']
    commit = require_tag_checkout(root, tag)
    meta = json.loads(tagged_blob(root, commit, 'release.json'))
    edition = meta.get('edition')
    title = (meta['name'] + ' · ' + edition['name'] + ' edition') if edition else meta['name'] + ' ' + tag
    notes = release_notes(tagged_blob(root, commit, 'CHANGELOG.md').decode('utf-8'), tag)
    assets = release_assets(root)
    with tempfile.TemporaryDirectory() as tmp:
        snapshots = []
        for asset in assets:
            name = asset.relative_to(root).as_posix()
            content = tagged_blob(root, commit, name)
            if asset.read_bytes() != content:
                raise ValueError(f'Release asset differs from the tagged file: {name}')
            snapshot = Path(tmp) / asset.name
            snapshot.write_bytes(content)
            snapshots.append(str(snapshot))
        subprocess.run(
            ['gh', 'release', 'create', tag, '--verify-tag', '--draft',
             '--title', title, '--notes-file', '-', *snapshots],
            input=notes.encode('utf-8'), cwd=root, check=True,
        )


if __name__ == '__main__':
    main()
