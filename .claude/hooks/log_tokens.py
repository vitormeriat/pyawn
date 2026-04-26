#!/usr/bin/env python3
"""Stop hook: appends one log line per interaction to docs/token_log.log."""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent.parent / "docs" / "token_log.log"


def find_usage(obj: object) -> dict | None:
    """Recursively search for an API usage dict inside the transcript message."""
    if isinstance(obj, dict):
        if "input_tokens" in obj and "output_tokens" in obj:
            return obj
        for v in obj.values():
            found = find_usage(v)
            if found:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_usage(item)
            if found:
                return found
    return None


def last_usage_from_transcript(path: str) -> dict:
    if not path:
        return {}
    transcript = Path(path)
    if not transcript.exists():
        return {}
    usage: dict = {}
    try:
        with open(transcript) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    msg = json.loads(line)
                    found = find_usage(msg)
                    if found:
                        usage = found
                except json.JSONDecodeError:
                    continue
    except OSError:
        pass
    return usage


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, OSError):
        return

    session_id = payload.get("session_id", "")
    transcript_path = payload.get("transcript_path", "")

    usage = last_usage_from_transcript(transcript_path)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    sess = session_id[:8] if session_id else "--------"
    inp = usage.get("input_tokens", 0)
    out = usage.get("output_tokens", 0)
    cache_r = usage.get("cache_read_input_tokens", 0)
    cache_w = usage.get("cache_creation_input_tokens", 0)

    line = (
        f"{ts}  sess={sess}"
        f"  in={inp:>6}  out={out:>5}"
        f"  cache_r={cache_r:>6}  cache_w={cache_w:>6}\n"
    )

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(line)


if __name__ == "__main__":
    main()
