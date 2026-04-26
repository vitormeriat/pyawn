#!/usr/bin/env python3
"""Stop hook: appends one CSV row per interaction to logs/token_log.csv."""
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_FILE = Path(__file__).parent.parent.parent / "logs" / "token_log.csv"

HEADER = [
    "timestamp", "session_id", "model",
    "input_tokens", "output_tokens",
    "cache_read_tokens", "cache_write_tokens",
]


def last_assistant_usage(transcript_path: str) -> dict:
    """Return usage dict from the last assistant message in the transcript."""
    if not transcript_path:
        return {}
    path = Path(transcript_path)
    if not path.exists():
        return {}

    usage: dict = {}
    try:
        with open(path) as f:
            for raw in f:
                raw = raw.strip()
                if not raw:
                    continue
                try:
                    entry = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if entry.get("type") == "assistant":
                    msg = entry.get("message", {})
                    if "usage" in msg:
                        usage = {"model": msg.get("model", ""), **msg["usage"]}
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
    usage = last_assistant_usage(transcript_path)

    row = {
        "timestamp":          datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session_id":         session_id[:8] if session_id else "",
        "model":              usage.get("model", ""),
        "input_tokens":       usage.get("input_tokens", 0),
        "output_tokens":      usage.get("output_tokens", 0),
        "cache_read_tokens":  usage.get("cache_read_input_tokens", 0),
        "cache_write_tokens": usage.get("cache_creation_input_tokens", 0),
    }

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_header = not LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    main()
