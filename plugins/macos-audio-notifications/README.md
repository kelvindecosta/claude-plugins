# macOS Audio Notifications

**macOS only.** Spoken notifications for Claude Code lifecycle events, using the
built-in macOS `say` command. Instead of watching the terminal, you hear what Claude is
doing — announced by the conversation's title so you can tell sessions apart by ear.

## What you hear

| Event | Hook | Announcement |
| --- | --- | --- |
| Claude finishes replying | `Stop` | "_\<title\>_ has replied" |
| A tool needs your approval | `PermissionRequest` | "_\<title\>_ is waiting approval" |
| Claude sends a notification | `Notification` | "_\<title\>_ is asking something" |
| `AskUserQuestion` is about to run | `PreToolUse` | "_\<title\>_ has asked a question" |
| A tool call fails | `PostToolUseFailure` | a short beep |

The `<title>` is resolved from the session transcript — the custom title you set,
falling back to a generated summary, then the project folder name.

## Install

```
/plugin marketplace add kelvindecosta/claude-plugins
/plugin install macos-audio-notifications@kelvindecosta
```

Then `/reload-plugins` (or restart Claude Code) to activate.

## Configuration

Both are optional environment variables, read at hook time:

| Variable | Effect | Default |
| --- | --- | --- |
| `CLAUDE_ANNOUNCE_VOICE` | `say` voice name, e.g. `Samantha` | system default voice |
| `CLAUDE_ANNOUNCE_SOUND` | sound file for the error beep | `/System/Library/Sounds/Ping.aiff` |
| `CLAUDE_ANNOUNCE_VOLUME` | loudness from `0.0` to `1.0`, relative to system volume | `0.05` |

To browse voices and pick one, run the bundled demo (it speaks each installed English
voice saying its own name):

```bash
./scripts/demo_voices.sh            # play them all
./scripts/demo_voices.sh Samantha   # replay just one
```

## Requirements

macOS — uses the built-in `say` and `afplay` commands. On other platforms the hooks
run but do nothing, so the plugin is safe to have installed anywhere.
