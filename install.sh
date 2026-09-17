#!/usr/bin/env bash
# Protean Kit installer entrypoint.
#
#   bash install.sh --all --target <dir>
#   bash install.sh --ingredient <slug> --target <dir>
#   bash install.sh --ingredient <slug> --no-deps --target <dir>
#   bash install.sh --all --target <dir> --offline
#   bash install.sh --all --target <dir> --dry-run
#
# The installer resolves the selection from kit.lock.json, fetches each pinned
# ingredient from its annotated tag, verifies the tag's peeled commit sha and the
# ingredient tree hash, installs it, and reads every written file back.
#
# Exit codes: 0 ok, 1 usage/input, 2 lock invalid, 3 dependency, 4 integrity,
# 5 install, 6 post-install verification. A run that installs part of the
# selection exits non-zero: there is no partial-success zero.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v python3 >/dev/null 2>&1; then
  printf 'error: install: python3 is required (%s)\n' "the installer is stdlib Python" >&2
  exit 1
fi

exec python3 "$ROOT/build/install.py" "$@"
