#!/bin/bash
# s7234 test for loop.sh's idle-gated soak queue (SOAK_NEEDS_IDLE / re-queue on rc=2).
# Pulls host_idle_s..run_soak_queue out of loop.sh and runs it on a temp queue with a fake idle feed.
set -u
here=$(cd "$(dirname "$0")" && pwd); T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
awk '/^host_idle_s\(\)/{f=1} f{print} f&&/^}$/&&seen{exit} /^run_soak_queue\(\)/{seen=1}' "$here/loop.sh" > "$T/fn.sh"
log(){ echo "LOG $*" >> "$T/log"; }
AG=$T/ag; mkdir -p $AG/soak_queue; SOAKS_BETWEEN_ITERS=2; SOAK_TIMEOUT=30; SOAK_MAX_VOIDS=3; SOAK_IDLE_WAIT=0; SOAK_IDLE_POLL=1
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
# s7254: bounded idle wait when every queued recipe is gated and the host is busy.
mk w 0; echo 5 > $T/idle; SOAK_IDLE_WAIT=3; t0=$SECONDS; run_soak_queue
chk "wait expires on a busy host, recipe stays queued" '[ -e $q/w.sh ] && grep -q "idle wait expired" $T/log && [ $((SECONDS-t0)) -ge 3 ]'
( sleep 2; echo 300 > $T/idle ) & SOAK_IDLE_WAIT=20; t0=$SECONDS; run_soak_queue; wait
chk "host goes idle mid-wait: recipe runs, wait ends early" '[ ! -e $q/w.sh ] && ls $q/done | grep -q "^w_" && grep -q "host idle after" $T/log && [ $((SECONDS-t0)) -lt 15 ]'
mk x 0; printf '#!/bin/bash\nexit 0\n' > "$q/plain2.sh"; echo 5 > $T/idle; t0=$SECONDS; run_soak_queue
chk "no wait when an ungated recipe ran (control)" '[ -e $q/x.sh ] && [ $((SECONDS-t0)) -lt 3 ]'
SOAK_IDLE_WAIT=0; t0=$SECONDS; run_soak_queue
chk "SOAK_IDLE_WAIT=0 keeps the old one-check behaviour" '[ -e $q/x.sh ] && [ $((SECONDS-t0)) -lt 2 ]'
rm -f $q/x.sh
# s7287: shebang picks the shell; a syntax error is filed as SYNTAX, never as a void.
printf '#!/bin/zsh\n# SOAK_NEEDS_IDLE=120\nx=(a b); rm -f /nonexistent_*(N); exit 0\n' > "$q/z.sh"; echo 300 > $T/idle; SOAK_IDLE_WAIT=0; run_soak_queue
chk "zsh-shebang recipe with zsh syntax runs under zsh" 'ls $q/done | grep -q "^z_" && grep -q "| z | rc=0 |" $AG/SOAK-RESULTS.md'
printf '#!/bin/bash\n# SOAK_NEEDS_IDLE=120\nif then fi (\n' > "$q/s.sh"; run_soak_queue
chk "syntax error filed as SYNTAX, not re-queued as a void" '[ ! -e $q/s.sh ] && grep -q "| s | rc=SYNTAX" $AG/SOAK-RESULTS.md && ! grep -q "| s | rc=2 VOID" $AG/SOAK-RESULTS.md'
# s7314: one game at a time. A fake game (C sleeper; a copied /bin/sleep is SIGKILLed by macOS) named SOAK_GAME_NAME.
export SOAK_GAME_NAME=rs64fake7314
if printf '#include <unistd.h>\n#include <stdlib.h>\nint main(int c,char**v){sleep(atoi(v[1]));return 0;}\n' | clang -x c -o "$T/$SOAK_GAME_NAME" - 2>/dev/null; then
  echo 300 > $T/idle; SOAK_IDLE_WAIT=0
  printf '#!/bin/bash\nexit 0\n' > "$q/g0.sh"; run_soak_queue
  chk "no game alive: no foreign/outlived note (control)" 'grep "| g0 | rc=0" $AG/SOAK-RESULTS.md | grep -vq "killed\|SIGKILLed"'
  "$T/$SOAK_GAME_NAME" 60 & fk=$!; sleep 0.3
  printf '#!/bin/bash\npgrep -x %s >/dev/null && exit 7; exit 0\n' "$SOAK_GAME_NAME" > "$q/g1.sh"; run_soak_pass
  chk "leftover game SIGKILLed before the recipe starts" '! kill -0 $fk 2>/dev/null && grep "| g1 | rc=0" $AG/SOAK-RESULTS.md | grep -q "foreign game killed before start: pids $fk"'
  wait $fk 2>/dev/null
  printf '#!/bin/bash\nperl -e "setpgrp(0,0); exec @ARGV" %s 60 >/dev/null 2>&1 &\nsleep 0.3; exit 0\n' "$T/$SOAK_GAME_NAME" > "$q/g2.sh"; run_soak_queue
  chk "game escaping the recipe's process group is reaped and logged" '! pgrep -x $SOAK_GAME_NAME >/dev/null && grep "| g2 | rc=0" $AG/SOAK-RESULTS.md | grep -q "own game outlived the recipe"'
  mkdir -p $T/emptyq; AGs=$AG; AG=$T/emptyq; "$T/$SOAK_GAME_NAME" 60 & fk=$!; sleep 0.3; run_soak_queue; AG=$AGs
  chk "empty queue: iteration leftover reaped at soak-phase start" '! kill -0 $fk 2>/dev/null && grep -q "| loop | leftover game alive after the iteration, SIGKILLed: pids $fk" $T/emptyq/SOAK-RESULTS.md'
  wait $fk 2>/dev/null; pkill -9 -x $SOAK_GAME_NAME 2>/dev/null
else echo "FAIL s7314 fake game build (clang)"; fail=1; fi
unset SOAK_GAME_NAME
# s7235: the soak phase must run under the current loop.sh (re-exec first, soaks run by the new process).
L=$here/loop.sh
w=$(grep -n '^while \[ "\$ITER_CAP"' "$L" | head -1 | cut -d: -f1)
f=$(grep -n 'RS64_LOOP_SOAKS_FIRST:-0' "$L" | head -1 | cut -d: -f1)
e=$(grep -n 'RS64_LOOP_SOAKS_FIRST=1 exec' "$L" | head -1 | cut -d: -f1)
r=$(grep -n '^  run_soak_queue$' "$L" | tail -1 | cut -d: -f1)
chk "deferred soak phase runs before the first iteration" '[ -n "$f" ] && [ -n "$w" ] && [ "$f" -lt "$w" ]'
chk "loop-tail re-exec precedes the soak call" '[ -n "$e" ] && [ -n "$r" ] && [ "$e" -lt "$r" ] && [ "$e" -gt "$w" ]'
exit $fail
