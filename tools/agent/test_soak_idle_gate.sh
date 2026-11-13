#!/bin/bash
# s7234 test for loop.sh's idle-gated soak queue (SOAK_NEEDS_IDLE / re-queue on rc=2).
# Pulls host_idle_s..run_soak_queue out of loop.sh and runs it on a temp queue with a fake idle feed.
set -u
here=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
awk '/^host_idle_s\(\)/{f=1} f{print} f&&/^}$/&&seen{exit} /^run_soak_queue\(\)/{seen=1}' "$here/loop.sh" > "$T/fn.sh"
log(){ echo "LOG $*" >> "$T/log"; }
AG=$T/ag; mkdir -p $AG/soak_queue; SOAKS_BETWEEN_ITERS=2; SOAK_TIMEOUT=30; SOAK_MAX_VOIDS=3
source "$T/fn.sh"
q=$AG/soak_queue; fail=0
mk(){ printf '#!/bin/bash\n# SOAK_NEEDS_IDLE=120\nexit %s\n' "$2" > "$q/$1.sh"; }
chk(){ if eval "$2"; then echo "PASS $1"; else echo "FAIL $1"; fail=1; fi; }
export SOAK_IDLE_FEED=$T/idle
mk a 0; printf '#!/bin/bash\nexit 0\n' > "$q/plain.sh"
echo 5 > $T/idle; run_soak_queue
chk "busy host: gated recipe stays queued" '[ -e $q/a.sh ]'
chk "busy host: ungated recipe still runs (control)" '[ ! -e $q/plain.sh ] && ls $q/done | grep -q plain'
echo 300 > $T/idle; run_soak_queue
chk "idle host: gated recipe runs and is filed" '[ ! -e $q/a.sh ] && ls $q/done | grep -q "^a_"'
mk v 2; for k in 1 2; do run_soak_queue; done
chk "rc=2 re-queued below the void cap" '[ -e $q/v.sh ] && [ "$(cat $q/.v.voids)" = 2 ]'
run_soak_queue
chk "rc=2 at the void cap is filed" '[ ! -e $q/v.sh ] && [ ! -e $q/.v.voids ] && ls $q/done | grep -q "^v_"'
mk c 1; run_soak_queue
chk "rc=1 (real failure) is filed at once" '[ ! -e $q/c.sh ]'
chk "verdict lines written" '[ $(grep -c "re-queued" $AG/SOAK-RESULTS.md) = 2 ]'
# s7235: the soak phase must run under the current loop.sh (re-exec first, soaks run by the new process).
L=$here/loop.sh
w=$(grep -n '^while \[ "\$ITER_CAP"' "$L" | head -1 | cut -d: -f1)
f=$(grep -n 'RS64_LOOP_SOAKS_FIRST:-0' "$L" | head -1 | cut -d: -f1)
e=$(grep -n 'RS64_LOOP_SOAKS_FIRST=1 exec' "$L" | head -1 | cut -d: -f1)
r=$(grep -n '^  run_soak_queue$' "$L" | tail -1 | cut -d: -f1)
chk "deferred soak phase runs before the first iteration" '[ -n "$f" ] && [ -n "$w" ] && [ "$f" -lt "$w" ]'
chk "loop-tail re-exec precedes the soak call" '[ -n "$e" ] && [ -n "$r" ] && [ "$e" -lt "$r" ] && [ "$e" -gt "$w" ]'
exit $fail
