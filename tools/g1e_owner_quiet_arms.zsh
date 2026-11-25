#!/bin/zsh
# s6932: owner recipe with NO recipe logging, launched directly (m6_god_common.sh arms LOG_PHASE and session probes, ~0.7 MB/s, s6932). Only the route
# keys, godmode, NO_SAVE_WRITE and the present ring are added. Locked 60 Hz. Stops if a human touches the machine.
# usage: env ARMS="4:q4: 2:q2:" HOLD=300 zsh tools/g1e_owner_quiet_arms.zsh ; spec = dd:arm:extra env, several joined with +
cd "$(git rev-parse --show-toplevel)" || exit 1
R=${R:-$PWD/scratch/s6932}; DHZ=${DHZ:-$PWD/scratch/s6931/dhz}; HOLD=${HOLD:-300}
# s7243: RESUME=1 skips an arm that already completed (ok_<arm> written after its done line) when the key matches:
# binary mtime+size, the arm spec and HOLD. A void then costs only the voided arm and those after it, not the whole recipe.
# GAMEDIR/GAME are overridable for tools/s7243_resume_test.zsh (fake game). Default: build/RogueSquadron64Recomp.
TOOLS=$PWD/tools; [ -x $TOOLS/s7250_duty ] || cc -O2 -o $TOOLS/s7250_duty $TOOLS/s7250_duty.c; [ -x $TOOLS/s7253_clkprobe ] || cc -O2 -o $TOOLS/s7253_clkprobe $TOOLS/s7253_clkprobe.c
GAMEDIR=${GAMEDIR:-build}; GAME=${GAME:-./RogueSquadron64Recomp}
armkey(){ echo "$(stat -f '%m:%z' $GAMEDIR/$GAME 2>/dev/null) H=$HOLD S=$1"; }
# s7457 class DM: one stdout "tag=" line per scored arm (loop.sh verdict fields, tools/agent/soak_verdict_fields.sh). Before s7457 the
# done line went only to $R/arms.log, so every g1e soak (s7264-s7311) read arms=0 and was scored on rc alone.
# s7458 class DN: vi_stalls30s comes from the arm's present ring (tools/agent/ring_stalls.py; no game log needed): episodes >= RING_GAP_S
# (default 30) with no present, or with presents but an unchanged VI origin (s6993 L4 boot freeze: 235 s hold, max present gap 77 ms),
# or a silent ring tail before the SIGKILL of a live arm (ke = wall time of the alive check). No ring rows -> na (stall_na).
tagline(){ local d=$2 al fa rs ew=(); al=${d##* alive=}; al=${al%% *}; fa=${d##* fatal=}; [[ $fa == "$d" ]] && fa=0; fa=${fa%% *}
  [[ $al == 1 && -n $ke && $3 != resumed ]] && ew=(--end-wall $ke)
  rs=$(python3 $TOOLS/agent/ring_stalls.py $R/ring_$1.txt ${RING_GAP_S:-30} $ew 2>/dev/null); [[ $rs == vi_stalls30s=* ]] || rs="vi_stalls30s=na"
  echo "tag=g1eq_$1 alive_at_end=$al crashlines=$fa $rs hold=$HOLD level_ok=${3:-na}"; }
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
# s7249: s7231's "WIDEWIN costs a flat 30" ran on BATTERY at 10%->2% charge (pmset log; host hibernated at 1% at 15:22) and every task's CPU time was a
# constant 1.40x the AC run s7248 in light and heavy scenes alike (a clock signature, not load). Timing arms on battery are not comparable to AC arms:
# log the power source on every start/done line and stop (exit 2, re-queued) on battery unless ALLOW_BATT=1.
# s7253: battery is necessary but not sufficient for the cap (s7252), so the refusal now keys on a MEASURED clock ratio:
# tools/s7253_clkprobe min ms / tools/s7253_clkprobe.base (controls: DUTY 1.40 reads 1.39, 15-core spin load reads 1.02).
# Refuse (exit 2) when clk > CLK_MAX (default 1.15) unless ALLOW_SLOW=1; battery alone is only logged now.
clk(){ local b m; b=$(awk 'NR==1{print $1}' $TOOLS/s7253_clkprobe.base 2>/dev/null); m=$($TOOLS/s7253_clkprobe 60 5 2>/dev/null | sed -n 's/^clk_ms=\([0-9.]*\).*/\1/p')
  [[ -n $b && -n $m ]] && awk -v m=$m -v b=$b 'BEGIN{printf "%.3f", m/b}' || echo NA; }
pwr(){ pmset -g batt 2>/dev/null | awk -F"'" 'NR==1{s=($2=="AC Power")?"AC":"BATT"} NR==2{match($0,/[0-9]+%/); c=substr($0,RSTART,RLENGTH)} END{print s c}'; }
locked(){ /usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes'; }
watch_human(){ local p=$(idle) c t=0 f0="" f w0=$(date +%s) w; while kill -0 $1 2>/dev/null; do /bin/sleep 2; t=$((t+2)); c=$(idle);
  w=$(date +%s); if (( w - w0 > 20 )) || locked; then echo "$(date +%T) $2 host slept/locked t=$t wall +$((w-w0))s, arm void" >> $R/arms.log; echo "void $t lock" > $R/void_$2; kill -KILL $1 2>/dev/null; return; fi; w0=$w
  f=$(front); [[ -n $f && $f != $f0 ]] && { echo "$(date +%T) $2 front t=$t $f" >> $R/arms.log; f0=$f; }; if (( c + 1 < p )); then echo "$(date +%T) $2 human input t=$t idle $p -> $c, arm void" >> $R/arms.log; echo "void $t human" > $R/void_$2; kill -KILL $1 2>/dev/null; return; fi; p=$c; done; }
# s7464 class DU: specs are whitespace-separated, so a spec's own env vars must be joined with "+". s7463_padhash_flight wrote
# "4:cnt:A=1 B=2": the loop ran 4 arms, two with an empty name and dd=<an env assignment>, and the second empty arm overwrote the
# first's log_.txt, so the measuring arm's data were lost and the control read FAIL on an arm that never existed. Validate every
# spec before launching anything: dd numeric, arm name [A-Za-z0-9_]+, names unique. Bad spec -> exit 3 (not 2: never re-queue).
# Test: tools/agent/test_quiet_arms_spec.sh.
# s7952: arm names key per-arm files in $R (log_/ring_/ok_/void_<arm>), so q4 and Q4 are ONE file on this case-insensitive fs:
# uniqueness is checked case-folded. $R itself is refused when it differs from an existing sibling only by case (run_dir_guard.sh).
_c=$(sh $PWD/tools/agent/run_dir_guard.sh $R) || { echo "bad R: $_c (case-only collision; rename)" >&2; exit 3; }
typeset -A seen; for spec in ${=${ARMS:-"4:q4: 2:q2: 4:q4b: 2:q2b:"}}; do a=("${(@s/:/)spec}")
  if [[ $spec != *:*:* || ! $a[1] =~ '^[0-9]+(\.[0-9]+)?$' || ! $a[2] =~ '^[A-Za-z0-9_]+$' || -n ${seen[${(L)a[2]}]} ]]; then
    echo "bad arm spec '$spec' (want dd:arm:ENV1=v+ENV2=v, unique arm names)" | tee -a $R/arms.log >&2; exit 3; fi; seen[${(L)a[2]}]=1; done
[[ $SPEC_CHECK_ONLY == 1 ]] && { echo "spec ok"; exit 0; }
for spec in ${=${ARMS:-"4:q4: 2:q2: 4:q4b: 2:q2b:"}}; do
  a=("${(@s/:/)spec}"); x=${spec#*:*:}; x=${x//+/ }; dd=$a[1]; arm=$a[2]; i=$(idle)
  if [[ $RESUME == 1 && -e $R/ok_$arm && $(head -1 $R/ok_$arm) == "$(armkey $spec)" && -s ${LOGTO:-$R/log_$arm.txt} ]]; then
    echo "$(date +%T) $arm resume: key match, arm kept" >> $R/arms.log; tail -1 $R/ok_$arm >> $R/arms.log; tagline $arm "$(tail -1 $R/ok_$arm)" resumed; continue; fi
  rm -f $R/ok_$arm
  pw=$(pwr); ck=$(clk); echo "$(date +%T) $arm start idle=$i pwr=$pw clk=$ck" >> $R/arms.log
  [[ $ck != NA && $ALLOW_SLOW != 1 ]] && (( ck > ${CLK_MAX:-1.15} )) && { echo "$(date +%T) host clock capped (clk=$ck > ${CLK_MAX:-1.15}, pwr=$pw), stopping" >> $R/arms.log; echo slowclk > $R/quiet.done; exit 2; }
  locked && { echo "$(date +%T) screen locked, stopping" >> $R/arms.log; echo locked > $R/quiet.done; exit 2; }
  (( i < 120 )) && { echo "$(date +%T) human active, stopping" >> $R/arms.log; echo human > $R/quiet.done; exit 2; }
  # s6991: FORCE_UNLOCK was hardcoded 1 here, which clamps the level-select cursor to level 1 whatever FORCE_SAVE_MISSION
  # says (s5707: the save byte alone is rewritten by the level-select tick). Every "LEVEL=N" arm run through this
  # harness before s6991 (s6962 l4/l10, s6990 L0-L18) actually flew level 1. Now FORCE_UNLOCK follows the requested level.
  # s7250: harness token DUTY=<factor> (not passed to the game) runs tools/s7250_duty on the game pid: SIGSTOP/SIGCONT at an 8 ms
  # period, a calibrated whole-process slow-down standing in for battery Low Power Mode (s7249 x1.40; taskpolicy gives 1.0x or 3.2x).
  du=""; [[ " $x " == *" DUTY="* ]] && { du=${x##*DUTY=}; du=${du%% *}; x=${x//DUTY=$du/}; }
  lv=1; [[ " $x " == *" ROGUESQ_FORCE_SAVE_MISSION="* ]] && { lv=${x##*ROGUESQ_FORCE_SAVE_MISSION=}; lv=${lv%% *}; }
  [[ " $x " == *" ROGUESQ_FORCE_UNLOCK="* ]] || x="ROGUESQ_FORCE_UNLOCK=$lv $x"
  rm -f $R/ring_$arm.txt  # s7458: a game that dies before opening its ring must not be scored on the previous run's ring
  $DHZ 60 $((HOLD+30)) > $R/hz_$arm.txt 2>&1 & hp=$!; /bin/sleep 3
  ( cd $GAMEDIR && exec env ROGUESQ_FORCE_SAVE_MISSION=1 ROGUESQ_FORCE_UNLOCK=1 ROGUESQ_NO_SAVE_WRITE=1 ROGUESQ_GODMODE=1 ROGUESQ_AUTOPILOT_HOLD_MS=1800 ROGUESQ_AUTOPILOT=$AP ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=$dd ROGUESQ_ASPECT=16:9 ROGUESQ_FULLSCREEN=1 ROGUESQ_PRESENT_RING=$R/ring_$arm.txt ${=x} $GAME ) > ${LOGTO:-$R/log_$arm.txt} 2>&1 & gp=$!
  dp=""; [ -n "$du" ] && { $TOOLS/s7250_duty $gp $du ${DUTY_PERIOD:-8000} 2> $R/duty_$arm.txt & dp=$!; echo "$(date +%T) $arm duty=$du" >> $R/arms.log; }
  ( for k in 1 2 3 4 5 6 7 8; do /bin/sleep 12; osascript -e 'tell application "System Events" to set frontmost of (first process whose name contains "RogueSquadron64Recomp") to true' >/dev/null 2>&1; done ) & rp=$!
  rm -f $R/void_$arm; watch_human $gp $arm & wp=$!
  # s7205: SHOTS="150,160,..." = screencapture -x at those seconds after launch (same autopilot timeline in every arm).
  if [ -n "$SHOTS" ]; then ( t0=$SECONDS; k=0; for s in ${(s:,:)SHOTS}; do k=$((k+1)); while (( SECONDS - t0 < s )); do /bin/sleep 0.5; done; [ -e $R/void_$arm ] && break; screencapture -x $R/shot_${arm}_c$k.png; done ) & sp=$!; fi
  for ((n=0; n<HOLD; n+=2)); do /bin/sleep 2; [ -e $R/void_$arm ] && break; done; [ -n "$sp" ] && kill $sp 2>/dev/null; alive=0; kill -0 $gp 2>/dev/null && alive=1; ke=$(date +%s)
  kill -KILL $gp 2>/dev/null; kill $rp 2>/dev/null; kill $wp 2>/dev/null; kill -KILL $hp 2>/dev/null; [ -n "$dp" ] && kill $dp 2>/dev/null
  # s7256: VOID_OK_AFTER=<s> keeps an arm voided by HUMAN input at watch t >= s (its scored window, e.g. L4 t=77-97, already ran clean):
  # ok_<arm> is written so RESUME=1 skips it, then the recipe still stops (exit 2) because a human is on. A lock/sleep void is never kept
  # (the screen may have frozen presents before the void was seen). s7248 voided at t=114, s7250 at t=160: both windows were clean, both arms re-ran.
  if [ -e $R/void_$arm ]; then vt=$(awk '{print $2; exit}' $R/void_$arm); vk=$(awk '{print $3; exit}' $R/void_$arm)
    if [[ -n $VOID_OK_AFTER && $vk == human && -n $vt ]] && (( vt >= VOID_OK_AFTER )); then
      dl="$(date +%T) $arm done alive=1 latevoid=t$vt log=$(wc -c < ${LOGTO:-$R/log_$arm.txt}) pwr=$(pwr) clk=$(clk)"; echo "$dl" >> $R/arms.log
      printf '%s\n%s\n' "$(armkey $spec)" "$dl" > $R/ok_$arm; tagline $arm "$dl" latevoid; fi
    echo human > $R/quiet.done; exit 2; fi
  cm=$(grep -a -m1 -o 'cursorMask)=0x[0-9A-Fa-f]*' ${LOGTO:-$R/log_$arm.txt} | sed 's/.*=//'); want=$(printf '0x%08X' $((1 << lv)))
  lok=1; [[ $cm == $want ]] || { lok=0; echo "$(date +%T) $arm LEVEL MISMATCH want lvl $lv mask $want got ${cm:-none}" >> $R/arms.log; }
  # s7453 class DI: an arm whose game died before HOLD (alive=0) or printed a fatal line used to log "done alive=0" and exit 0.
  # Now the done line carries the shared fatal_scan score and the recipe exits 1 at the end (all arms still run).
  fs=$(zsh $TOOLS/agent/fatal_scan.sh ${LOGTO:-$R/log_$arm.txt}); [[ $alive == 0 || $fs != fatal=0* ]] && died=1
  dl="$(date +%T) $arm done alive=$alive log=$(wc -c < ${LOGTO:-$R/log_$arm.txt}) $fs pwr=$(pwr) clk=$(clk)"; echo "$dl" >> $R/arms.log
  printf '%s\n%s\n' "$(armkey $spec)" "$dl" > $R/ok_$arm; tagline $arm "$dl" $lok; /bin/sleep ${ARM_GAP:-3}
done
echo done > $R/${DONE:-quiet.done}
[[ -n $died ]] && { echo "$(date +%T) DIED: an arm died or printed a fatal line (s7453), exit 1" >> $R/arms.log; exit 1; }
exit 0
