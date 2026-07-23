#!/usr/bin/env bash
# Demo every installed English `say` voice: prints its name and speaks
# "Hello, my name is <name>". Use the printed names to pick a voice via the
# CLAUDE_ANNOUNCE_VOICE environment variable.
#
# Usage:
#   ./demo_voices.sh            # play all English voices
#   ./demo_voices.sh Samantha   # replay a single voice by name

set -euo pipefail

if ! command -v say >/dev/null 2>&1; then
  echo "This script requires the macOS \`say\` command." >&2
  exit 1
fi

speak_one() {
  local name="$1"
  # Spoken name drops any locale suffix like " (English (US))".
  local spoken="${name% (*}"
  printf '  %s\n' "$name"
  say -v "$name" "Hello, my name is ${spoken}"
}

# Replay a single named voice if given.
if [[ $# -ge 1 ]]; then
  speak_one "$*"
  exit 0
fi

echo "English say voices (press Ctrl-C to stop):"
echo

# `say -v '?'` columns: <name...>  <locale>  # <sample>
# Keep only en_* locales; the name is everything left of the locale token.
say -v '?' | while IFS= read -r line; do
  locale=$(echo "$line" | sed -E 's/.*[[:space:]]([a-z]{2}_[A-Za-z0-9]+)[[:space:]]*#.*/\1/')
  case "$locale" in
    en_*)
      name=$(echo "$line" | sed -E 's/[[:space:]]+[a-z]{2}_[A-Za-z0-9]+[[:space:]]*#.*//' | sed -E 's/[[:space:]]+$//')
      speak_one "$name"
      ;;
  esac
done
