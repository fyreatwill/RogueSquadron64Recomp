#!/bin/sh
# s7656 test: stop_gate.sh --verify blocks on a NEW red census gate and passes a green one.
# Builds a detached git worktree of HEAD under $TMPDIR (never touches this checkout, lib/ or build/saves), fakes a finished
# iteration in it (STATUS/NEXT/OUTCOME, a commit adding a session entry + CURRENT-TRUTH edit + a planted census tool), and
# runs the real stop_gate.sh there with the sweep narrowed to the planted tool. Arms:
#   red     planted tool exits 1              -> gate must BLOCK naming it
#   green   planted tool exits 0              -> gate must ALLOW
#   allowed planted red, listed in the allowed-RED file -> ALLOW
#   untouched  red tool exists but the iteration's commit touches no code/census path -> ALLOW (sweep not run)
set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
fail=0
arm() { # name exit_code allow_list(0/1) touch_tool(0/1) expect(block|allow)
  name=$1; code=$2; allow=$3; touchtool=$4; expect=$5
  W="$(mktemp -d "${TMPDIR:-/tmp}/rs64_gsweep.XXXXXX")/wt"
  git -C "$REPO" worktree add --detach -q "$W" HEAD 2>/dev/null || { echo "FAIL $name: worktree"; fail=1; return; }
  (
    cd "$W" || exit 9
    mkdir -p scratch/agent
    if [ "$touchtool" = 1 ]; then
      printf 'import sys\nprint("planted %s")\nsys.exit(%s)\n' "$name" "$code" > tools/s7999_planted_census.py
    else  # tool committed BEFORE the iteration starts, so the iteration's commits do not touch it
      printf 'import sys\nsys.exit(%s)\n' "$code" > tools/s7999_planted_census.py
      git add -A && git -c user.name=t -c user.email=t@t commit -qm base
    fi
    git rev-parse HEAD > scratch/agent/ITER_START_HEAD
    touch scratch/agent/ITER_START_MARK; sleep 1
    [ "$allow" = 1 ] && echo "s7999_planted_census.py test arm" >> tools/gate_sweep_allowed_red.txt
    printf '\n## Session 99999 (2026-11-19) — gate sweep test arm %s\n' "$name" >> PORTING-STATE.md
    echo "<!-- test $name -->" >> docs/CURRENT-TRUTH.md
    git add -A && git -c user.name=t -c user.email=t@t commit -qm "test $name"
    echo DONE > scratch/agent/STATUS; echo ADVANCED > scratch/agent/OUTCOME
    printf 'x\nHYPOTHESIS-ID: test\n' > scratch/agent/NEXT.md
    out="$(env RS64_GATE_SWEEP_ONLY='^s7999_planted' tools/agent/stop_gate.sh --verify 2>&1)"; rc=$?
    got=allow; [ $rc != 0 ] && got=block
    if [ "$got" = "$expect" ] && { [ "$expect" = allow ] || printf '%s' "$out" | grep -q 's7999_planted_census.py'; }; then
      echo "PASS $name ($got)"
    else
      echo "FAIL $name: expected $expect got $got rc=$rc"; printf '%s\n' "$out" | head -8; exit 1
    fi
  ) || fail=1
  git -C "$REPO" worktree remove --force "$W" 2>/dev/null
}
arm red 1 0 1 block
arm green 0 0 1 allow
arm allowed 1 1 1 allow
arm untouched 1 0 0 allow
[ $fail = 0 ] && echo "test_gate_sweep: ALL PASS" || echo "test_gate_sweep: FAIL"
exit $fail
