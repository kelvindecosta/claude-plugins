#!/usr/bin/env python3
"""Speak a per-event announcement for Claude Code hook events (macOS).

Usage: announce.py <event>
  event is one of: done | approval | asking | question | issue

Spoken events use the macOS `say` command; the `issue` event instead plays a
short system beep. The announcement names the conversation, preferring the
transcript's custom title, then its generated summary, then the project folder.

Configuration (environment variables, all optional):
  CLAUDE_ANNOUNCE_VOICE   `say` voice name (e.g. "Samantha"). Unset -> system default.
  CLAUDE_ANNOUNCE_SOUND   Path to the sound played for the `issue` event.

Non-macOS platforms (or a missing `say`/`afplay`) are a no-op, so this is safe
to install anywhere.
"""
import json
import os
import shutil
import subprocess
import sys

PHRASES = {
    "done": "{title} has replied",
    "approval": "{title} is waiting approval",
    "asking": "{title} is asking something",
    "question": "{title} has asked a question",
}

# Sound played for the `issue` event; override with CLAUDE_ANNOUNCE_SOUND.
DEFAULT_SOUND = "/System/Library/Sounds/Ping.aiff"


def humanize(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").strip() or "Claude"


def title_from_transcript(path: str) -> str | None:
    """Return the conversation's title from a transcript .jsonl, if any.

    Prefers the user-set custom title, then a generated summary. Uses the most
    recent of each, since titles can be changed over the life of a session.
    """
    if not path or not os.path.isfile(path):
        return None
    custom_title = None
    summary = None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if not isinstance(entry, dict):
                    continue
                etype = entry.get("type")
                if etype == "custom-title" and entry.get("customTitle"):
                    custom_title = entry["customTitle"]
                elif etype == "summary" and entry.get("summary"):
                    summary = entry["summary"]
    except OSError:
        return None
    return custom_title or summary


def resolve_title(payload: dict) -> str:
    title = title_from_transcript(payload.get("transcript_path", ""))
    if title:
        return title
    cwd = payload.get("cwd") or os.getcwd()
    return humanize(os.path.basename(os.path.normpath(cwd)))


def play_sound() -> None:
    if not shutil.which("afplay"):
        return
    sound = os.environ.get("CLAUDE_ANNOUNCE_SOUND") or DEFAULT_SOUND
    if os.path.isfile(sound):
        subprocess.run(["afplay", sound], check=False)


def speak(phrase: str) -> None:
    if not shutil.which("say"):
        return
    voice = os.environ.get("CLAUDE_ANNOUNCE_VOICE")
    cmd = ["say"] + (["-v", voice] if voice else []) + [phrase]
    subprocess.run(cmd, check=False)


def main() -> int:
    event = sys.argv[1] if len(sys.argv) > 1 else "done"

    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        payload = {}

    if event == "issue":
        play_sound()
        return 0

    title = resolve_title(payload)
    phrase = PHRASES.get(event, PHRASES["done"]).format(title=title)
    speak(phrase)
    return 0


if __name__ == "__main__":
    sys.exit(main())
