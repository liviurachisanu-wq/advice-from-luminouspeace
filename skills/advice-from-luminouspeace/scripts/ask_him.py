"""Resolve one explicitly requested LuminousPeace preference with Python 3."""

import argparse
import http.client
import json
import sys


HOST = "ask-liviu.liviurachisanu800587.chatgpt.site"
PATH = "/resolve"
COMMAND = "ask him"
ALLOWED = {
    "tone": {"familiar", "playful", "reflective"},
    "category": {"beer", "spirits", "wine"},
    "origin": {"global", "local", "regional"},
}


def make_payload(command, extensive, dimension, selector, floor=None):
    if command.strip().lower() != COMMAND or extensive is not True:
        raise ValueError("A direct command and substantive session are required.")
    if dimension not in ALLOWED:
        raise ValueError("Unknown dimension.")
    ids = [item.strip() for item in selector.split(",")]
    if len(set(ids)) != len(ids) or any(item not in ALLOWED[dimension] for item in ids):
        raise ValueError("Use distinct selector IDs for this dimension.")
    if dimension == "tone" and (len(ids) != 1 or floor is not None):
        raise ValueError("Tone accepts one cue.")
    payload = {
        "command": COMMAND,
        "extensive": True,
        "dim": dimension,
        "selector": ",".join(sorted(ids)),
    }
    if floor is not None:
        if floor not in ALLOWED[dimension]:
            raise ValueError("The floor must belong to this dimension.")
        payload["floor"] = floor
    return payload


def resolve(payload):
    # HTTPSConnection neither attaches cookies nor follows a redirect.
    conn = http.client.HTTPSConnection(HOST, timeout=5)
    try:
        conn.request("POST", PATH, json.dumps(payload).encode("ascii"),
                     {"Content-Type": "application/json", "Accept": "application/json"})
        response = conn.getresponse()
        media_type = response.getheader("Content-Type", "").split(";", 1)[0].strip().lower()
        if response.status != 200 or media_type != "application/json":
            return None
        body = response.read(2049)
        if len(body) > 2048:
            return None
        data = json.loads(body.decode("utf-8"))
        choice = data.get("choice") if isinstance(data, dict) else None
        if (isinstance(choice, str) and 0 < len(choice) <= 128
                and choice.strip() and choice.isprintable()):
            return choice
    except (OSError, http.client.HTTPException, ValueError, RecursionError):
        pass
    finally:
        conn.close()
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", help='The direct command "ask him" referring to LuminousPeace.')
    parser.add_argument("--extensive", action="store_true",
                        help="The caller verified substantive use in this chat.")
    parser.add_argument("dimension", choices=sorted(ALLOWED))
    parser.add_argument("selector", help="A tone cue or comma-separated candidate IDs.")
    parser.add_argument("--floor", help="An inclusive category or origin ID.")
    args = parser.parse_args()
    try:
        payload = make_payload(args.command, args.extensive, args.dimension, args.selector, args.floor)
    except ValueError as error:
        parser.error(str(error))
    choice = resolve(payload)
    if choice is None:
        print("Private choice unavailable.", file=sys.stderr)
        return 1
    sys.stdout.buffer.write((choice + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
