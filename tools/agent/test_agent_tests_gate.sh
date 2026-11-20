#!/bin/sh
# s7709 test: stop_gate.sh --verify runs tools/agent/run_tests.sh when the iteration's commits touch tools/agent/*.sh|*.py and
# blocks naming the failing test. Detached worktree of HEAD (never touches this checkout, lib/ or build/saves); the test dir is
# a temp dir holding one planted test (RS64_AGENT_TESTS_DIR), so the inner run cannot recurse into this file. Arms:
#   red        planted test exits 1, commit touches tools/agent/  -> BLOCK naming test_zz_planted
#   green      planted test exits 0, commit touches tools/agent/  -> ALLOW
#   untouched  planted test exits 1, commit touches no tools/agent -> ALLOW (tests not run)
# Usage: test_agent_tests_gate.sh [stop_gate.sh]  (a mutated copy is the control: red must then FAIL)
set -u
REPO="$(cd "$(dirname "$0")/../.." && pwd)"; GATE=${1:-$REPO/tools/agent/stop_gate.sh}   # default: the working copy, so an uncommitted gate edit is what gets tested
fail=0
arm() { # name planted_rc touch_agent(0/1) expect
  name=$1; code=$2; touch=$3; expect=$4
  B="$(mktemp -d "${TMPDIR:-/tmp}/rs64_atest.XXXXXX")"; W="$B/wt"; mkdir "$B/tests"
  printf '#!/bin/sh\necho "planted %s"\nexit %s\n' "$name" "$code" > "$B/tests/test_zz_planted.sh"
  git -C "$REPO" worktree add --detach -q "$W" HEAD 2>/dev/null || { echo "FAIL $name: worktree"; fail=1; return; }
  (
    cd "$W" || exit 9
    cp "$REPO/tools/agent/run_tests.sh" tools/agent/run_tests.sh   # the runner under test is the working copy's
    cp "$GATE" tools/agent/stop_gate.sh
    git add -A && git -c user.name=t -c user.email=t@t commit -qm base --allow-empty
    mkdir -p scratch/agent
    git rev-parse HEAD > scratch/agent/ITER_START_HEAD
    touch scratch/agent/ITER_START_MARK; sleep 1
    printf '\n## Session 99999 (2026-11-20) — agent tests gate arm %s\n' "$name" >> PORTING-STATE.md
    echo "<!-- test $name -->" >> docs/CURRENT-TRUTH.md
    if [ "$touch" = 1 ]; then echo "# $name" >> tools/agent/summary_field.sh; else echo "$name" > tools/s7999_note.txt; fi
    git add -A && git -c user.name=t -c user.email=t@t commit -qm "test $name"
    echo DONE > scratch/agent/STATUS; echo ADVANCED > scratch/agent/OUTCOME
    printf 'x\nHYPOTHESIS-ID: test\n' > scratch/agent/NEXT.md
    out="$(env RS64_AGENT_TESTS=1 RS64_AGENT_TESTS_DIR="$B/tests" RS64_GATE_SWEEP=0 RS64_CRASH_REPORTS=0 \
      tools/agent/stop_gate.sh --verify 2>&1)"; rc=$?
    got=allow; [ $rc != 0 ] && got=block
    if [ "$got" = "$expect" ] && { [ "$expect" = allow ] || printf '%s' "$out" | grep -q 'agent tool tests FAIL: test_zz_planted'; }; then
      echo "PASS $name ($got)"
    else
      echo "FAIL $name: expected $expect got $got rc=$rc"; printf '%s\n' "$out" | head -6; exit 1
    fi
  ) || fail=1
  git -C "$REPO" worktree remove --force "$W" 2>/dev/null; rm -rf "$B"
}
arm red 1 1 block
arm green 0 1 allow
arm untouched 1 0 allow
[ $fail = 0 ] && echo "test_agent_tests_gate: ALL PASS" || echo "test_agent_tests_gate: FAIL"
exit $fail
