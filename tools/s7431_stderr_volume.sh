#!/bin/zsh
# s7431 class CN runtime half: one owner-recipe run (no logging env) forced to level 1 flight by the in-process autopilot
# (wall clock, no window keys), in a copied folder (owner save copied, ROGUESQ_NO_SAVE_WRITE=1). stdout+stderr are
# timestamped per line on arrival, then tools/s7431_stderr_volume.py classifies every tag.
# Planted control ROGUESQ_FB_HASH=1 (per-frame [fbhash line) - excluded from the verdict by name.
# usage: tools/s7431_stderr_volume.sh [secs=260] [extra env...]   Exit = analyzer exit (0 capped, 1 found, 3 control fail).
ROOT=${0:A:h:h}; B=/tmp/rs64_s7431; T=${1:-260}; shift 2>/dev/null; D=$B/${S7431_ARM:-A}
rm -rf $D; mkdir -p $D/saves; cp ${S7431_BIN:-$ROOT/build/RogueSquadron64Recomp} $D/RogueSquadron64Recomp
cp $ROOT/build/rogue_squadron.z64 $ROOT/build/rs64.n64.us.1.0.z64 $D/ 2>/dev/null; cp $ROOT/build/saves/rs64.n64.us.1.0.bin $D/saves/
E=""; e=10; for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; E="$E$e:$k,"; e=$((e+4)); done
F=""; t=95; while (( t <= 520 )); do for k in a sl a sr; do F="$F$t:$k,"; t=$((t+2)); done; done
# S7431_TTY=1: run under script(1) so the game's stderr is a terminal (the owner's Terminal launch).
PTY=""; [[ ${S7431_TTY:-0} = 1 ]] && PTY="script -q /dev/null"
pkill -9 -x RogueSquadron64Recomp; sleep 1
(cd $D && exec env ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4 ROGUESQ_ASPECT=16:9 \
  ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 \
  ROGUESQ_AUTOPILOT="$E${F%,}" ROGUESQ_FB_HASH=1 "$@" ${=PTY} ./RogueSquadron64Recomp 2>&1 < /dev/null) \
  | python3 -u -c 'import sys,time
t0=time.monotonic(); o=open(sys.argv[1],"wb")
for l in sys.stdin.buffer: o.write(b"%d\t"%int((time.monotonic()-t0)*1000)+l)
o.flush()' $D/run.tlog &
sleep $T; pkill -9 -x RogueSquadron64Recomp; wait
print "crashlines=$(grep -ac "CRASH\|SIGSEGV\|SIGBUS" $D/run.tlog); $(wc -c < $D/run.tlog) B"
python3 $ROOT/tools/s7431_stderr_volume.py $D/run.tlog ${=S7431_PYARGS:-}
