"""Assemble the hosted Worker from its source and the exact published skill ZIP."""
import argparse
import base64
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def render_worker(root=ROOT):
    archive = (root / "editions/ask-him/advice-from-luminouspeace-ask-him.zip").read_bytes()
    with ZipFile(BytesIO(archive)) as skill:
        envelope = skill.read("advice-from-luminouspeace/.reflex-preferences.enc")
    source = (root / "service/worker.mjs").read_text(encoding="utf-8")
    for marker, payload in (
        ("__ASK_HIM_SKILL_ZIP__", archive),
        ("__ASK_HIM_SEALED_PREFERENCES__", envelope),
    ):
        if source.count(marker) != 1:
            raise ValueError("Expected one Worker build marker " + marker)
        source = source.replace(marker, base64.b64encode(payload).decode("ascii"))
    return source.encode("utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="Destination for the self-contained Worker module")
    args = parser.parse_args()
    args.output.write_bytes(render_worker())
