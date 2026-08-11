#!/usr/bin/env bash
# Fetch GLideN64's semantic implementation of the Factor 5 microcodes.
#
# These are REFERENCE ONLY. GLideN64 is GPL-2.0-or-later and this project is
# not, so reference/ is gitignored and nothing from it may be copied into our
# tree. We take the meaning, not the code - see docs/F5-UCODE-REFERENCE.md.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
dest="$repo_root/reference/gliden64"
base="https://raw.githubusercontent.com/gonetz/GLideN64/master/src/uCodes"

mkdir -p "$dest"
for f in F5Rogue.cpp F5Rogue.h F5Indi_Naboo.cpp F5Indi_Naboo.h; do
  curl -sfL -o "$dest/$f" "$base/$f"
  printf '%-20s %6s lines\n' "$f" "$(wc -l < "$dest/$f" | tr -d ' ')"
done

echo
echo "reference in $dest (gitignored, GPL - do not copy into src/)"
