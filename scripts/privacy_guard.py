"""Conservative export checks. Never embed real protected identities in this file.

This detects common contact/credential patterns, not arbitrary personal history.
Manual review remains necessary. Errors identify rules and paths, never values.
"""
from io import BytesIO
from pathlib import PurePosixPath
import hashlib
import re
import subprocess
import zipfile

RULES = {
    'email address': re.compile(r'[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}', re.I),
    'private file reference': re.compile(r'libfile_[a-f0-9]{16,}|chatgpt[.]com/library', re.I),
    'personal filesystem path': re.compile(r'[A-Z]:[\\/]Users[\\/]|(?<![A-Z0-9./:-])/(?:[U]sers|[h]ome)/', re.I),
    'private key': re.compile(r'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----'),
    'access token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,})\b'),
}
# The deployment key is 32 bytes. Check common literal assignments and
# deployment API key/value objects without flagging reads of a runtime secret.
KEY_VALUE = r"""["']?(?:[0-9a-fA-F]{64}|[A-Za-z0-9+/]{43}=)(?![A-Za-z0-9+/=])"""
KEY_FIELD = r"""["'](?:name|key)["']\s*:\s*["']REFLEX_KEY["']"""
VALUE_FIELD = r"""["']value["']\s*:\s*""" + KEY_VALUE
RULES['literal preference decryption key'] = re.compile(
    r"""\bREFLEX_KEY\b["']?\s*[:=]\s*""" + KEY_VALUE + '|' +
    KEY_FIELD + r'[^{}]{0,1024}?' + VALUE_FIELD + '|' +
    VALUE_FIELD + r'[^{}]{0,1024}?' + KEY_FIELD
)
TEXT_EXTENSIONS = {'.md', '.txt', '.py', '.json', '.yml', '.yaml', '.html'}
TEXT_NAMES = {'LICENSE', '.gitignore', '.gitattributes', 'SHA256SUMS.txt'}
REVIEWED_MODULES = {'service/worker.mjs', 'tests/service.test.mjs'}
ENVELOPE_MEMBER = 'advice-from-luminouspeace/.reflex-preferences.enc'
EDITION_ARCHIVES = {
    'downloads/advice-from-luminouspeace-ask-him.zip',
    'editions/ask-him/advice-from-luminouspeace-ask-him.zip',
}
ENVELOPE_DIGEST = 'e536e6b16f726b9c209d6d6373a6bd6b00c2d350926b620bf48c7f1746a822ec'


def scan_payload(name, payload, depth=0, budget=None, container=None):
    """Inspect text and bounded ZIP members without extracting anything."""
    if budget is None:
        budget = [0, 0]
    budget[0] += len(payload)
    if len(payload) > 5_000_000 or budget[0] > 20_000_000:
        raise ValueError('Export size limit exceeded')
    path = PurePosixPath(name.replace('\\', '/'))
    if path.is_absolute() or '..' in path.parts or ':' in name:
        raise ValueError('Unsafe export path')
    if path.suffix.lower() == '.zip':
        if depth >= 2:
            raise ValueError('Archive nesting limit exceeded')
        with zipfile.ZipFile(BytesIO(payload)) as archive:
            for info in archive.infolist():
                budget[1] += 1
                if budget[1] > 100 or info.file_size > 5_000_000:
                    raise ValueError('Archive member limit exceeded')
                if info.flag_bits & 1 or (info.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError('Encrypted archives and symbolic links are not publishable')
                if not info.is_dir():
                    scan_payload(info.filename, archive.read(info), depth + 1, budget, name)
        return
    if path.suffix.lower() == '.enc':
        reviewed_location = (
            (depth == 0 and name == 'skills/' + ENVELOPE_MEMBER) or
            (depth == 1 and container in EDITION_ARCHIVES and name == ENVELOPE_MEMBER)
        )
        if (not reviewed_location or not payload.startswith(b'LPRF\x01\x01\x00\x00')
                or hashlib.sha256(payload).hexdigest() != ENVELOPE_DIGEST):
            raise ValueError('Unreviewed encrypted payload: ' + name)
        return
    reviewed_module = depth == 0 and name in REVIEWED_MODULES
    if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in TEXT_NAMES and not reviewed_module:
        raise ValueError('Unreviewed export file type: ' + name)
    text = payload.decode('utf-8')
    for rule, pattern in RULES.items():
        if pattern.search(text):
            raise ValueError(rule + ' detected in ' + name)


def scan_repository(root):
    """Include tests and untracked, nonignored files; do not scan Git internals."""
    result = subprocess.run(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'],
        cwd=root, check=True, capture_output=True,
    )
    for name in sorted(set(result.stdout.decode('utf-8').split('\0')) - {''}):
        path = root / name
        if path.is_symlink():
            raise ValueError('Symbolic link in export: ' + name)
        scan_payload(name, path.read_bytes())
