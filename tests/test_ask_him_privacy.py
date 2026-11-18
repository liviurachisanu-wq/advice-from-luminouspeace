"""The published edition admits one reviewed encrypted preference envelope."""
import base64
from io import BytesIO
import json
from pathlib import Path
import sys
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from privacy_guard import scan_payload


MEMBER = 'advice-from-luminouspeace/.reflex-preferences.enc'
NATIVE = 'skills/' + MEMBER
SOURCE = 'editions/ask-him/advice-from-luminouspeace-ask-him.zip'
DOWNLOAD = 'downloads/advice-from-luminouspeace-ask-him.zip'


def archive(name, payload):
    buffer = BytesIO()
    with ZipFile(buffer, 'w') as zipped:
        zipped.writestr(name, payload)
    return buffer.getvalue()


class AskHimPrivacyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = (ROOT / SOURCE).read_bytes()
        with ZipFile(BytesIO(cls.package)) as zipped:
            cls.envelope = zipped.read(MEMBER)

    def test_reviewed_edition(self):
        scan_payload(SOURCE, self.package)
        scan_payload(DOWNLOAD, self.package)
        scan_payload(NATIVE, self.envelope)

    def test_rejects_altered_header_and_ciphertext(self):
        for index in (0, len(self.envelope) - 1):
            modified = bytearray(self.envelope)
            modified[index] ^= 1
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'Unreviewed encrypted'):
                scan_payload(NATIVE, modified)
            with self.subTest(index=index), self.assertRaisesRegex(ValueError, 'Unreviewed encrypted'):
                scan_payload(DOWNLOAD, archive(MEMBER, modified))

    def test_rejects_unreviewed_locations_and_nested_envelopes(self):
        for name, content in (
                ('other/.reflex-preferences.enc', self.envelope),
                ('other.zip', archive(MEMBER, self.envelope)),
                (DOWNLOAD, archive('other/.reflex-preferences.enc', self.envelope)),
                ('outer.zip', archive(SOURCE, self.package)),
                ('owner/reflex.key', self.envelope)):
            with self.subTest(name=name), self.assertRaises(ValueError):
                scan_payload(name, content)

    def test_service_modules_are_scanned_only_at_reviewed_source_paths(self):
        safe = b'const key = env.REFLEX_KEY;'
        scan_payload('service/worker.mjs', safe)
        scan_payload('tests/service.test.mjs', safe)
        for name, content in (
                ('worker.mjs', safe),
                ('outer.zip', archive('service/worker.mjs', safe)),
                ('service/worker.mjs', b'const token = "ghp_' + b'x' * 32 + b'"')):
            with self.subTest(name=name), self.assertRaises(ValueError):
                scan_payload(name, content)

    def test_detects_literal_deployment_secret_without_echoing_value(self):
        sample = bytes(range(32))
        for value in (base64.b64encode(sample).decode(), sample.hex()):
            for config in (
                    'REFLEX_KEY=' + value,
                    json.dumps({'REFLEX_KEY': value}),
                    json.dumps({'key': 'REFLEX_KEY', 'is_secret': True, 'value': value}),
                    json.dumps({'value': value, 'name': 'REFLEX_KEY'})):
                with self.assertRaisesRegex(ValueError, 'literal preference decryption key') as caught:
                    scan_payload('deployment.json', config.encode())
                self.assertNotIn(value, str(caught.exception))


if __name__ == '__main__':
    unittest.main()
