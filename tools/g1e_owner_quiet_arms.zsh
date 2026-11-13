#!/bin/zsh
# s6932: owner recipe with NO recipe logging, launched directly (m6_god_common.sh arms LOG_PHASE and session probes, ~0.7 MB/s, s6932). Only the route
# keys, godmode, NO_SAVE_WRITE and the present ring are added. Locked 60 Hz. Stops if a human touches the machine.
# usage: env ARMS="4:q4: 2:q2:" HOLD=300 zsh tools/g1e_owner_quiet_arms.zsh ; spec = dd:arm:extra env, several joined with +
cd "$(git rev-parse --show-toplevel)" || exit 1
R=${R:-$PWD/scratch/s6932}; DHZ=${DHZ:-$PWD/scratch/s6931/dhz}; HOLD=${HOLD:-300}
# s7243: RESUME=1 skips an arm that already completed (ok_<arm> written after its done line) when the key matches:
# binary mtime+size, the arm spec and HOLD. A void then costs only the voided arm and those after it, not the whole recipe.
# GAMEDIR/GAME are overridable for tools/s7243_resume_test.zsh (fake game). Default: build/RogueSquadron64Recomp.
GAMEDIR=${GAMEDIR:-build}; GAME=${GAME:-./RogueSquadron64Recomp}
armkey(){ echo "$(stat -f '%m:%z' $GAMEDIR/$GAME 2>/dev/null) H=$HOLD S=$1"; }
EARLY=""; e=10
for i in $(seq 1 20); do if (( i % 2 == 0 || e > 74 )); then k=z; else k=start; fi; EARLY="$EARLY$e:$k,"; e=$((e+4)); done
FL=""; t=95
for i in $(seq 1 100); do for k in a sl a sr; do FL="$FL$t:$k,"; t=$((t+2)); done; (( t > 520 )) && break; done
AP="${EARLY}${FL%,}"
idle(){ if [ -n "$IDLE_FEED" ]; then tail -1 "$IDLE_FEED"; else ioreg -c IOHIDSystem | awk '/HIDIdleTime/{printf "%d\n",$NF/1e9; exit}'; fi; }
# s6935: arm lq went void because a human left the fullscreen Space at t=80 while idle at the END of the arm still looked late (idle gives the LAST input, not the first).
# Any fall in idle during an arm means a human is on: kill the arm at once, hand the display back, exit 2. Test: IDLE_FEED=<file> with a falling tail, see tools/g1e_quiet_watch_test.zsh
# s7218: also log every change of the frontmost app (a Claude.app auto-update relaunch covered the fullscreen Space at t=354
# in s7218 arm a1: 64 s of presents never reached the screen, one 1 s nextDrawable timeout). Not a void, a recorded host event.
front(){ lsappinfo info -only name "$(lsappinfo front)" 2>/dev/null | sed 's/.*="//;s/"$//'; }
# s7233: arm r40 r40 froze at t=72 when the screen locked and the host slept 3.7 h (game clock t=69 -> 13608); nothing voided it.
# Now a locked screen or a wall-clock jump > 20 s between 2 s polls (host sleep) voids the arm like human input.
locked(){ /usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'; }
watch_human(){ local p=$(idle) c t=0 f0="" f w0=$(date +%s) w; while kill -0 $1 2>/dev/null; do /bin/sleep 2; t=$((t+2)); c=$(idle);
  w=$(date +%s); if (( w - w0 > 20 )) || locked; then echo "$(date +%T) $2 host slept/locked t=$t wall +$((w-w0))s, arm void" >> $R/arms.log; echo void > $R/void_$2; kill -KILL $1 2>/dev/null; return; fi; w0=$w
  f=$(front); [[ -n $f && $f != $f0 ]] && { echo "$(date +%T) $2 front t=$t $f" >> $R/arms.log; f0=$f; }; if (( c + 1 < p )); then echo "$(date +%T) $2 human input t=$t idle $p -> $c, arm void" >> $R/arms.log; echo void > $R/void_$2; kill -KILL $1 2>/dev/null; return; fi; p=$c; done; }
for spec in ${=${ARMS:-"4:q4: 2:q2: 4:q4b: 2:q2b:"}}; do
  a=("${(@s/:/)spec}"); x=${spec#*:*:}; x=${x//+/ }; dd=$a[1]; arm=$a[2]; i=$(idle)
  if [[ $RESUME == 1 && -e $R/ok_$arm && $(head -1 $R/ok_$arm) == "$(armkey $spec)" && -s ${LOGTO:-$R/log_$arm.txt} ]]; then
    echo "$(date +%T) $arm resume: key match, arm kept" >> $R/arms.log; tail -1 $R/ok_$arm >> $R/arms.log; continue; fi
  rm -f $R/ok_$arm
  echo "$(date +%T) $arm start idle=$i" >> $R/arms.log
  locked && { echo "$(date +%T) screen locked, stopping" >> $R/arms.log; echo locked > $R/quiet.done; exit 2; }
  (( i < 120 )) && { echo "$(date +%T) human active, stopping" >> $R/arms.log; echo human > $R/quiet.done; exit 2; }
  # s6991: FORCE_UNLOCK was hardcoded 1 here, which clamps the level-select cursor to level 1 whatever FORCE_SAVE_MISSION
  # says (s5707: the save byte alone is rewritten by the level-select tick). Every "LEVEL=N" arm run through this
  # harness before s6991 (s6962 l4/l10, s6990 L0-L18) actually flew level 1. Now FORCE_UNLOCK follows the requested level.
  lv=1; [[ " $x " == *" ROGUESQ_FORCE_SAVE_MISSION="* ]] && { lv=${x##*ROGUESQ_FORCE_SAVE_MISSION=}; lv=${lv%% *}; }
  [[ " $x " == *" ROGUESQ_FORCE_UNLOCK="* ]] || x="ROGUESQ_FORCE_UNLOCK=$lv $x"
  $DHZ 60 $((HOLD+30)) > $R/hz_$arm.txt 2>&1 & hp=$!; /bin/sleep 3
  ( cd $GAMEDIR && exec env ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$dd ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1 ROGUESQ_PRESENT_RING=$R/ring_$arm.txt ${=x} $GAME ) > ${LOGTO:-$R/log_$arm.txt} 2>&1 & gp=$!
  ( for k in 1 2 3 4 5 6 7 8; do /bin/sleep 12; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & rp=$!
  rm -f $R/void_$arm; watch_human $gp $arm & wp=$!
  # s7205: SHOTS="150,160,..." = screencapture -x at those seconds after launch (same autopilot timeline in every arm).
  if [ -n "$SHOTS" ]; then ( t0=$SECONDS; k=0; for s in ${(s:,:)SHOTS}; do k=$((k+1)); while (( SECONDS - t0 < s )); do /bin/sleep 0.5; done; [ -e $R/void_$arm ] && break; screencapture -x $R/shot_${arm}_c$k.png; done ) & sp=$!; fi
  for ((n=0; n<HOLD; n+=2)); do /bin/sleep 2; [ -e $R/void_$arm ] && break; done; [ -n "$sp" ] && kill $sp 2>/dev/null; alive=0; kill -0 $gp 2>/dev/null && alive=1
  kill -KILL $gp 2>/dev/null; kill $rp 2>/dev/null; kill $wp 2>/dev/null; kill -KILL $hp 2>/dev/null
  [ -e $R/void_$arm ] && { echo human > $R/quiet.done; exit 2; }
  cm=$(grep -a -m1 -o 'cursorMask)=0x[0-9A-Fa-f]*' ${LOGTO:-$R/log_$arm.txt} | sed 's/.*=//'); want=$(printf '0x%08X' $((1 << lv)))
  [[ $cm == $want ]] || echo "$(date +%T) $arm LEVEL MISMATCH want lvl $lv mask $want got ${cm:-none}" >> $R/arms.log
  dl="$(date +%T) $arm done alive=$alive log=$(wc -c < ${LOGTO:-$R/log_$arm.txt})"; echo "$dl" >> $R/arms.log
  printf '%s\n%s\n' "$(armkey $spec)" "$dl" > $R/ok_$arm; /bin/sleep ${ARM_GAP:-3}
done
echo done > $R/${DONE:-quiet.done}
