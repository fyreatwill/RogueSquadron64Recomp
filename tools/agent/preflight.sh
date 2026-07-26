#!/bin/bash
# Fail fast on every environment failure that has previously burned a session:
# no-GUI sandbox (s6-s7), Accessibility silently absent, Screen Recording /
# locked screen, ROM not beside the binary (silent "place your ROM" VI), bare
# CLT without metal, missing PIL venv, submodule patches reverted.
set -u
cd "$(dirname "$0")/../.."
fail() { echo "[preflight] FAIL: $1"; exit 1; }

[ "$(launchctl managername 2>/dev/null)" = "Aqua" ] \
  || fail "not a GUI (Aqua) session - run the loop from Terminal on the logged-in desktop"

[ -x build/winctl ] || fail "build/winctl missing - rebuild: clang -O1 -fobjc-arc -framework Cocoa -framework CoreGraphics -o build/winctl tools/winctl.m"

# winctl trusted prints exactly "yes" or "no"
[ "$(build/winctl trusted 2>/dev/null)" = "yes" ] \
  || fail "Accessibility not granted to this terminal context (build/winctl trusted said no)"

# An untrusted workspace silently discards every permissions.allow entry in
# .claude/settings.json, which turns the whole loop into permission denials.
python3 - "$PWD" <<'PY' || fail "workspace not trusted - .claude/settings.json permissions are being IGNORED. Run 'claude' interactively once in this directory and accept the trust dialog."
import json, os, sys
p = os.path.expanduser("~/.claude.json")
try:
    e = json.load(open(p)).get("projects", {}).get(sys.argv[1], {})
except Exception:
    sys.exit(0)   # can't tell; don't block on it
sys.exit(0 if e.get("hasTrustDialogAccepted") else 1)
PY

t="$(mktemp -d)/pf.png"
screencapture -x "$t" 2>/dev/null
[ -s "$t" ] || fail "screencapture wrote nothing - Screen Recording permission or locked screen"

ls build 2>/dev/null | grep -qiE '\.(z64|n64|v64)$' \
  || fail "ROM not in build/ next to the executable (silent dead-VI trap)"

[ -d "${DEVELOPER_DIR:-/Applications/Xcode.app/Contents/Developer}" ] \
  || fail "full Xcode not found - metal shader rebuilds will fail (set DEVELOPER_DIR)"

scratch/venv/bin/python -c "import PIL" 2>/dev/null \
  || fail "scratch/venv python lacks PIL - image decoders will fail"

# The lib/ patches are the port. If a submodule got reset, stop before building
# something subtly wrong. --reverse --check succeeds iff the patch is applied.
for p in N64ModernRuntime:lib/N64ModernRuntime \
         rt64:lib/rt64 \
         rt64-hlslpp:lib/rt64/src/contrib/hlslpp \
         rt64-plume:lib/rt64/src/contrib/plume; do
  name="${p%%:*}"; sub="${p#*:}"
  if git -C "$sub" apply --reverse --check "$PWD/submodule-patches/$name.patch" 2>/dev/null; then
    continue
  fi
  if [ -z "$(git -C "$sub" status --porcelain)" ]; then
    fail "$sub has NO local modifications - the patches were wiped. Run ./submodule-patches/apply.sh before doing anything else."
  fi
  echo "[preflight] WARN: $sub differs from submodule-patches/$name.patch (you edited lib/ without re-exporting). Run ./submodule-patches/export.sh and commit."
done

echo "[preflight] OK"
