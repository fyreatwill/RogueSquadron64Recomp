#!/bin/sh
# s7709: run every tools/agent/test_*.sh with its own shebang interpreter, one PASS/FAIL line each; rc 1 on any FAIL.
# stop_gate.sh --verify calls this when an iteration's commits touch tools/agent/*.sh|*.py (tests were hand-run only before,
# so a loop.sh / stop_gate.sh edit could silently break the soak gate, crash gate or the s7708 contract carry).
# Usage: run_tests.sh [dir]  (dir defaults to this script's directory; the control passes a temp copy with a planted test).
# RS64_AGENT_TESTS=0 is exported so a test that runs stop_gate.sh itself cannot recurse into this runner.
DIR=${1:-$(cd "$(dirname "$0")" && pwd)}
cd "$(cd "$(dirname "$0")/../.." && pwd)" || exit 2
export RS64_AGENT_TESTS=0
# The gate's skip/narrow knobs must not leak into tests that run stop_gate.sh themselves (s7709: RS64_GATE_SWEEP=0 on the
# outer gate made test_gate_sweep's red arm ALLOW). Each test sets what it needs explicitly.
unset RS64_GATE_SWEEP RS64_GATE_SWEEP_ONLY RS64_CRASH_REPORTS RS64_CRASH_DIR RS64_AGENT_TESTS_DIR RS64_SKIP_STOP_HOOK
fail=0; n=0; failed=
for t in "$DIR"/test_*.sh; do
  [ -f "$t" ] || continue
  n=$((n+1)); name=$(basename "$t" .sh)
  interp=$(head -1 "$t" | sed -n 's/^#![[:space:]]*\([^[:space:]]*\).*/\1/p'); [ -n "$interp" ] || interp=/bin/sh
  out=$("$interp" "$t" 2>&1); rc=$?
  if [ $rc = 0 ]; then echo "PASS $name"
  else echo "FAIL $name rc=$rc: $(printf '%s\n' "$out" | grep -iE 'fail' | head -2 | tr '\n' ' ' | cut -c1-200)"
       fail=$((fail+1)); failed="$failed $name"; fi
done
[ $n -gt 0 ] || { echo "FAIL no tests found in $DIR"; exit 1; }
echo "run_tests: $((n-fail))/$n PASS${failed:+ FAILED:$failed}"
[ $fail = 0 ]
