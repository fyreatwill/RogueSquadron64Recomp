#!/bin/zsh
# M6 keyed endurance: s5377 key route (title->hangar->0x6A2900->mission 0x690400), retry up to 5 launches, then hold HOLD s after mission onset.
# Logs crash lines and VI-origin stalls (>30 s with no new origin row). usage: m6_keyed_hold.sh <tag> [hold_secs]
set -u
TAG=${TAG:-m6_god_x}; HOLD=${HOLD:-440}; FBD_EVERY=${FBD_EVERY_V:-$(print -r -- "${XENV:-}" | sed -n "s/.*ROGUESQ_FB_DUMP_EVERY=\([0-9]*\).*/\1/p")}; FBD_EVERY=${FBD_EVERY:-500}  # s6276: COMMON re-sets DUMP_EVERY after XENV, so XENV value was silently overridden
ROOT=$(git rev-parse --show-toplevel); OUT=$ROOT/scratch/agent/m6/$TAG; _c=$(sh $ROOT/tools/agent/run_dir_guard.sh $ROOT/scratch/agent/m6 $TAG) || { echo "tag=$TAG $_c alive_at_end=na vi_stalls30s=na (s7951: case-only TAG collision on a case-insensitive fs; rename the TAG)"; exit 3; }; BUILD=${BUILD:-$ROOT/build}; mkdir -p $OUT $OUT/fbd; K=$OUT/keys.log; : > $K
fbrun() { awk '{h=$NF} h==p {r++} h!=p {r=1;p=h} r>m {m=r} !(h in d) {d[h]=1;n++} END{print "maxrun=" m+0 " distinct=" n+0 " total=" NR}'; }
[ "$(printf 'a\nb\nb\nb\nb\nb\nc\n' | fbrun)" = "maxrun=5 distinct=3 total=7" ] && echo 'fbrun-control OK' >> $K || { echo 'fbrun-control FAIL' >> $K; exit 1; }
# s5553: mission_cycles = hangar entries after the first mission origin (title->hangar->mission re-entries). Control: synthetic sequence with 2 re-entries must give 2.
mcycles() { grep -a '^\[vi\] update_screen' "$1" | grep -o 'origin=0x[0-9A-Fa-f]*' | uniq | awk '/690400/{m=1} m&&/6AB400/{n++} END{print n+0}'; }
printf '[vi] update_screen origin=0x006AB400\n[vi] update_screen origin=0x00690400\n[vi] update_screen origin=0x006AB400\n[vi] update_screen origin=0x00690400\n[vi] update_screen origin=0x006AB400\n' > $OUT/mc_ctl.txt
[ "$(mcycles $OUT/mc_ctl.txt)" = 2 ] && echo 'mcycles-control OK' >> $K || { echo 'mcycles-control FAIL' >> $K; exit 1; }
# s6867: mcycles is a false zero wherever the origins move (dd>1, wide), and hold counts from the gate, so the summary now states real flight: inits = [initMission] lines in THIS attempt's run.log (s7454 class DJ: each attempt rewrites run.log with '>', so a relaunch never adds one; inits>1 = a same-process mission restart, see mission_restarts=), flight_s = run seconds minus the run clock at the first [initMission]. Control: synthetic log must give 2 and 70.
flightline() { awk -v end="$2" '/^\[autopilot\] fire/{ if (match($0,/t=[0-9.]+/)) t=substr($0,RSTART+2,RLENGTH-2)+0 } /^\[initMission\]/{ n++; if (n==1) i=t } END{ if (n) printf "inits=%d flight_s=%d", n, end-i; else printf "inits=0 flight_s=none" }' "$1"; }
# s7454 class DJ: launches= is the harness attempt count (processes started, one run.log each); mission_restarts= counts
# same-process re-inits ([initMission] call#>=2, the game's per-process counter). inits=1 alone could not tell these apart
# (s7449 L4 inits=2 = call#2 after endMissionCleanup <- mainGameLoop, alive, 0 crash). Pass checks should grep 'mission_restarts=0 '.
restarts() { awk '/^\[initMission\] call#/{ if (match($0,/call#[0-9]+/) && substr($0,RSTART+5,RLENGTH-5)+0 >= 2) n++ } END{ printf "%d", n }' "$1"; }
printf '[initMission] call#1 x\n[initMission] call#2 y\n[initMission] call#12 z\n' > $OUT/rs_ctl.txt; printf '[initMission] call#1 x\n' > $OUT/rs_ctl0.txt
[ "$(restarts $OUT/rs_ctl.txt)" = 2 ] && [ "$(restarts $OUT/rs_ctl0.txt)" = 0 ] && echo 'restart-control OK' >> $K || { echo 'restart-control FAIL' >> $K; exit 1; }
printf '[autopilot] fire t=30.0\n[initMission] x\n[autopilot] fire t=50.0\n[initMission] y\n' > $OUT/fl_ctl.txt
[ "$(flightline $OUT/fl_ctl.txt 100)" = "inits=2 flight_s=70" ] && echo 'flight-control OK' >> $K || { echo 'flight-control FAIL' >> $K; exit 1; }
zsh $ROOT/tools/agent/fatal_scan.sh --selftest >> $K || { echo 'fatal-control FAIL' >> $K; exit 1; }
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo "SCREEN LOCKED" | tee $OUT/summary; exit 4; }
# s5416: winctl keys never reach SDL (macOS refuses to activate the game: isfrontmost=NULL, 0 SDL key events). Use the in-process autopilot.
# s5435: schedule continues past the results screen (LATE s): a/start alternate; the old 62-event list ended at t=254 s, before results.
AP=""; t=10; for i in $(seq 1 300); do if (( t > ${STOP:-90} )); then break; elif (( t > ${LATE:-520} )); then if (( i % 2 == 0 || ${LATE_NOSTART:-0} )); then k=${LKEY:-a}; else k=start; fi; elif (( i % 2 == 0 || t > ${START_UNTIL:-74} )); then k=z; else k=start; fi; AP="$AP$t:$k,"; t=$((t+4)); done; AP=${AP%,}
# s5678: must precede COMMON=(...) - the array expands $AP at definition (s5677 arms ran with an empty schedule: no "[autopilot] armed" line).
[ -n "${AP_OVERRIDE:-}" ] && AP=$AP_OVERRIDE
COMMON=(${=XENV} ROGUESQ_GODMODE=${GODV:-1} ROGUESQ_AUTOPILOT=$AP ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_FB_HASH=${FBH_V:-1} ROGUESQ_LOG_RDP_TRICOUNT=${TRI_V:-1} ROGUESQ_LOG_RT64_DRAWN=${DRAWN_V:-1} ROGUESQ_FB_DUMP_DIR=$OUT/fbd ROGUESQ_FB_DUMP_EVERY=${FBD_EVERY:-500})
# s7014: ROGUESQ_LOG_PHASE above (needed for phase gating) turns G1E_FAST off and G1E_PROBES on, so every cost/fps arm
# run through this harness timed the diagnostic ucode path, not the owner's (s7010-s7013 rsp 13-17 ms vs 8.8-11.1 ms owner path,
# and a "VI cliff" that does not exist for the owner). OWNER_TIMING=1 restores the owner's gfx path; use it for any timing arm.
[ "${OWNER_TIMING:-0}" = 1 ] && COMMON+=(ROGUESQ_G1E_FAST=1 ROGUESQ_G1E_PROBES=0)
# s5676: AP_OVERRIDE replaces the generated key schedule (s5675 set ROGUESQ_AUTOPILOT in XENV, but COMMON re-sets it from $AP after XENV, and STOP=0 made $AP empty -> no keys -> nohangar x8).
if [ "${ROGUESQ_NO_PKILL:-0}" != 1 ]; then
  pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
fi
void_holds=0
for att in $(seq 1 ${MAXATT:-5}); do
  L=$OUT/run.log
  ( cd $BUILD && exec env "${COMMON[@]}" ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$SECONDS
  has() { grep -aq "$1" $L; }
  key() { :; }  # no-op: autopilot injects keys
  # s7451: fail() records how the attempt ended (exitrc=killed when the harness killed a live game, else the game's own status) and its fatal_scan score; before s7451 a void attempt's crash text was never scored.
  # s7462 class DR: a void attempt (notitle/nohangar/nomission/died_in_verify) was retried with its stalls unscored, so a pre-gate
  # held frame (the s6993 boot-freeze shape: fs stuck while VI ticks, title gate times out -> notitle) vanished behind a later
  # good attempt. fail() now scores the attempt's log with vilog_stalls.py and sums fs_holds into void_holds=, which every summary
  # carries (soak_verdict_fields counts void_holds>0 as a stall arm). M6_VOID_BLIND=1 restores the unscored void (mutation control).
  fail() { local lv=1 vs="" vn; kill -0 $p 2>/dev/null || lv=0; kill -9 $p 2>/dev/null; wait $p 2>/dev/null; frc=$?; [ $lv = 1 ] && frc=killed
    if [ "${M6_VOID_BLIND:-0}" != 1 ]; then vs=$(python3 $ROOT/tools/agent/vilog_stalls.py $L 2>/dev/null | cut -d" " -f1-2); vn=${${vs%% *}#fs_holds=}; [[ $vn == <-> ]] && void_holds=$((void_holds+vn)); fi
    echo "$1-att$att exitrc=$frc $(zsh $ROOT/tools/agent/fatal_scan.sh $L) $vs" >> $K; cp $L $OUT/fail_att$att.log; }
  # s6434: wide-aspect arms move every framebuffer origin (FB_WIDTH 796/1024), so the 0x790400/0x6AB400 gates false-fail (s6433: 6/6 'notitle' while the autopilot reached hangar+flight). WIDE_ROUTE=1 gates on autopilot-armed and skips the hangar origin gates.
  [ "${WIDE_ROUTE:-0}" = 1 ] && { TITLE_OPTIONAL=1; AP_OVERRIDE_WIDE=1; }
  if [ "${TITLE_OPTIONAL:-0}" = 1 ]; then
    for i in $(seq 1 150); do grep -a -F -q '[autopilot] armed' "$L" && break; kill -0 $p 2>/dev/null || break; sleep 1; done
    grep -a -F -q '[autopilot] armed' "$L" || { fail notitle; continue; }
  elif [ "${TITLE_ANY:-0}" = 1 ]; then
    for i in $(seq 1 150); do has "origin=${TITLE_ORIGIN:-0x00790400}" && break; kill -0 $p 2>/dev/null || break; sleep 1; done
    grep -a -F -q '[autopilot] armed' "$L" || { fail notitle; continue; }
  else
    for i in $(seq 1 150); do has "origin=${TITLE_ORIGIN:-0x00790400}" && break; kill -0 $p 2>/dev/null || break; sleep 1; done
    has "origin=${TITLE_ORIGIN:-0x00790400}" || { fail notitle; continue; }
  fi
  [ -n "${AP_OVERRIDE:-}${AP_OVERRIDE_WIDE:-}" ] || for n in $(seq 1 12); do has 'origin=0x006AB400' && break; key 36; sleep 4; key 6; sleep 7; done
  if [ -z "${AP_OVERRIDE:-}${AP_OVERRIDE_WIDE:-}" ]; then
  has 'origin=0x006AB400' || { fail nohangar; continue; }
  sleep 15
  for n in $(seq 1 14); do { has 'origin=0x006A2900' || has 'origin=0x6A2900'; } && break; key 6; sleep 7; done
  fi  # s5677: AP_OVERRIDE routes skip the hangar gates (s5676 runs reached 0x690400/0x696100 with no 0x6AB400 -> all 8 attempts void as nohangar)
  mt=-1
  for n in $(seq 1 ${WAITN:-30}); do
    sleep 5; kill -0 $p 2>/dev/null || break
    [ $((n%6)) -eq 0 ] && key 6
    if [ "${MISSION_INIT:-0}" = 1 ]; then
      # s6865: gate on the game's own [initMission] line. Origins move with dd/aspect, and intros run to ~187 s on lvl5/10, so an origin gate either never fires or fires at boot and the hold counts cinematics as flight.
      grep -aq '^\[initMission\]' $L && { mt=$SECONDS; break; }
    elif [ -n "${MISSION_WIDTH:-}" ]; then
      # s6431: wide-aspect arms move the framebuffer origins (MISSION_RE=ZZZ never matched -> false nomission); gate on sustained flight-width rows instead.
      [ "$(grep -ac "width=${MISSION_WIDTH}\\b" $L)" -gt 300 ] && { mt=$SECONDS; break; }
    elif [ "${MISSION_WIDE_FLIGHT:-0}" = 1 ]; then
      # Route gate: allocator-independent wide flight plus the phase-5 writer witness.
      grep -aqE 'width=796' $L &&
        grep -aq '\[f5-phase5-target-store\]' $L && { mt=$SECONDS; break; }
    else
      grep -aqE "origin=0x(00)?(${MISSION_RE:-690400})" $L && { mt=$SECONDS; break; }
    fi
  done
  [ $mt -ge 0 ] || { fail nomission; continue; }
  echo "att=$att mission t=$((mt-t0))" >> $K
  # s5394: the attract demo also shows 0x690400 and ends at ~167 s; a real mission must outlast it.
  # s7451: a game death after the mission gate is a datum, not a void route: s7450 arm P (planted _Exit at 110 s) died_in_verify 4/5,
  # was retried each time, and its summary read "allattempts-failed" with the fatal line unscored. Now terminal; DIED_RETRY=1 restores the retry.
  # s7459 class DO: [vi] update_screen rows print every 64 VIs whatever the game does, so a growing row COUNT proves only that the
  # VI thread ticks: a game holding one frame (s6993 boot freeze shape, fs stuck) scored 0 here. Progress = the newest row's fs=
  # (game frame-swap counter); no fs= in the log -> row count (old). M6_STALL_LINES=1 restores the row count (mutation control).
  vprog(){ local f; [ "${M6_STALL_LINES:-0}" = 1 ] || f=$(grep -a 'update_screen #' $L | tail -1 | grep -oE 'fs=[0-9]+'); [ -n "$f" ] && echo "$f" || grep -ac origin= $L; }
  last=$(vprog); lastt=$SECONDS; stalls=0
  vtick(){ local c; c=$(vprog); [ "$c" != "$last" ] && { last=$c; lastt=$SECONDS; }
    [ $((SECONDS-lastt)) -gt 30 ] && { stalls=$((stalls+1)); echo "stall t=$((SECONDS-t0))" >> $K; lastt=$SECONDS; }; }
  # s7461 class DQ: the poller used to start only after this 130 s verify sleep, so a held frame in mission t 0-130 s scored
  # vi_stalls30s=0 (s7460 plant 120-160 s: live 0, offline fs_holds=1 max 2368 VIs). It now polls through the verify window too.
  # M6_VERIFY_BLIND=1 restores the old blind sleep (mutation control).
  if [ "${M6_VERIFY_BLIND:-0}" = 1 ]; then sleep 130
  else for n in $(seq 1 26); do sleep 5; kill -0 $p 2>/dev/null || break; vtick; done; fi
  kill -0 $p 2>/dev/null || { fail died_in_verify; [ "${DIED_RETRY:-0}" = 1 ] && continue
    echo "tag=$TAG att=$att mission_t=$((mt-t0))s died_in_verify=1 inits=$(grep -ac "^.initMission" $L) launches=$att mission_restarts=$(restarts $L) died_within_s=130 alive_at_end=0 vi_stalls30s=na void_holds=$void_holds crashlines=$(grep -acEf $ROOT/tools/agent/fatal_patterns.txt $L) exitrc=$frc" | tee $OUT/summary; exit 1; }
  echo "att=$att mission_verified_130s" >> $K
  while kill -0 $p 2>/dev/null && [ $((SECONDS-mt)) -lt $HOLD ]; do sleep 5; vtick; done
  alive=0; kill -0 $p 2>/dev/null && alive=1
  kill -9 $p 2>/dev/null; wait $p 2>/dev/null; xrc=$?; [ $alive = 1 ] && xrc=held  # s7450: a death's own exit status (non-signal exits print no CRASH)
  echo "fbhash $(grep -a '^.fbhash' $L | sed 's/.*h=//' | fbrun)" >> $K
  echo "tag=$TAG att=$att mission_t=$((mt-t0))s hold=$((SECONDS-mt))s $(flightline $L $((SECONDS-t0))) launches=$att mission_restarts=$(restarts $L) alive_at_end=$alive vi_stalls30s=$stalls godrefills=$(grep -ac "^.godmode" $L) mission_cycles=$(mcycles $L) void_holds=$void_holds $(python3 $ROOT/tools/agent/vilog_stalls.py $L 2>/dev/null | cut -d" " -f1-2) crashlines=$(grep -acEf $ROOT/tools/agent/fatal_patterns.txt $L) exitrc=$xrc" | tee $OUT/summary  # s7450 class DG: shared fatal list; s7452: this comment used to precede the tee, so no passing run wrote a summary
  exit 0
done
echo "tag=$TAG allattempts-failed void_holds=$void_holds $(grep -a -- '-att[0-9]* exitrc=' $K | awk '{f=$3; sub("fatal=","",f); n+=f; if($2!="exitrc=killed") d++} END{printf "deaths=%d fatal_total=%d", d, n}')" | tee $OUT/summary; exit 1
