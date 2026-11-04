#!/bin/zsh
# M6 keyed endurance: s5377 key route (title->hangar->0x6A2900->mission 0x690400), retry up to 5 launches, then hold HOLD s after mission onset.
# Logs crash lines and VI-origin stalls (>30 s with no new origin row). usage: m6_keyed_hold.sh <tag> [hold_secs]
set -u
TAG=${TAG:-m6_god_x}; HOLD=${HOLD:-440}; FBD_EVERY=${FBD_EVERY_V:-$(print -r -- "${XENV:-}" | sed -n "s/.*ROGUESQ_FB_DUMP_EVERY=\([0-9]*\).*/\1/p")}; FBD_EVERY=${FBD_EVERY:-500}  # s6276: COMMON re-sets DUMP_EVERY after XENV, so XENV value was silently overridden
ROOT=$(git rev-parse --show-toplevel); OUT=$ROOT/scratch/agent/m6/$TAG; BUILD=${BUILD:-$ROOT/build}; mkdir -p $OUT $OUT/fbd; K=$OUT/keys.log; : > $K
fbrun() { awk '{h=$NF} h==p {r++} h!=p {r=1;p=h} r>m {m=r} !(h in d) {d[h]=1;n++} END{print "maxrun=" m+0 " distinct=" n+0 " total=" NR}'; }
[ "$(printf 'a\nb\nb\nb\nb\nb\nc\n' | fbrun)" = "maxrun=5 distinct=3 total=7" ] && echo 'fbrun-control OK' >> $K || { echo 'fbrun-control FAIL' >> $K; exit 1; }
# s5553: mission_cycles = hangar entries after the first mission origin (title->hangar->mission re-entries). Control: synthetic sequence with 2 re-entries must give 2.
mcycles() { grep -a '^\[vi\] update_screen' "$1" | grep -o 'origin=0x[0-9A-Fa-f]*' | uniq | awk '/690400/{m=1} m&&/6AB400/{n++} END{print n+0}'; }
printf '[vi] update_screen origin=0x006AB400\n[vi] update_screen origin=0x00690400\n[vi] update_screen origin=0x006AB400\n[vi] update_screen origin=0x00690400\n[vi] update_screen origin=0x006AB400\n' > $OUT/mc_ctl.txt
[ "$(mcycles $OUT/mc_ctl.txt)" = 2 ] && echo 'mcycles-control OK' >> $K || { echo 'mcycles-control FAIL' >> $K; exit 1; }
/usr/sbin/ioreg -n Root -d1 | grep -q '"CGSSessionScreenIsLocked"=Yes' && { echo "SCREEN LOCKED" | tee $OUT/summary; exit 4; }
# s5416: winctl keys never reach SDL (macOS refuses to activate the game: isfrontmost=NULL, 0 SDL key events). Use the in-process autopilot.
# s5435: schedule continues past the results screen (LATE s): a/start alternate; the old 62-event list ended at t=254 s, before results.
AP=""; t=10; for i in $(seq 1 300); do if (( t > ${STOP:-90} )); then break; elif (( t > ${LATE:-520} )); then if (( i % 2 == 0 || ${LATE_NOSTART:-0} )); then k=${LKEY:-a}; else k=start; fi; elif (( i % 2 == 0 || t > ${START_UNTIL:-74} )); then k=z; else k=start; fi; AP="$AP$t:$k,"; t=$((t+4)); done; AP=${AP%,}
# s5678: must precede COMMON=(...) - the array expands $AP at definition (s5677 arms ran with an empty schedule: no "[autopilot] armed" line).
[ -n "${AP_OVERRIDE:-}" ] && AP=$AP_OVERRIDE
COMMON=(${=XENV} ROGUESQ_GODMODE=${GODV:-1} ROGUESQ_AUTOPILOT=$AP ROGUESQ_OVL2C_DROP=0 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 ROGUESQ_LOG_PHASE=1 ROGUESQ_AUDIO_UCODE=1 PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=240 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 ROGUESQ_FB_HASH=${FBH_V:-1} ROGUESQ_LOG_RDP_TRICOUNT=${TRI_V:-1} ROGUESQ_LOG_RT64_DRAWN=${DRAWN_V:-1} ROGUESQ_FB_DUMP_DIR=$OUT/fbd ROGUESQ_FB_DUMP_EVERY=${FBD_EVERY:-500})
# s5676: AP_OVERRIDE replaces the generated key schedule (s5675 set ROGUESQ_AUTOPILOT in XENV, but COMMON re-sets it from $AP after XENV, and STOP=0 made $AP empty -> no keys -> nohangar x8).
if [ "${ROGUESQ_NO_PKILL:-0}" != 1 ]; then
  pkill -KILL -x RogueSquadron64Recomp >/dev/null 2>&1 || true
fi
for att in $(seq 1 ${MAXATT:-5}); do
  L=$OUT/run.log
  ( cd $BUILD && exec env "${COMMON[@]}" ./RogueSquadron64Recomp ) > $L 2>&1 &
  p=$!; t0=$SECONDS
  has() { grep -aq "$1" $L; }
  key() { :; }  # no-op: autopilot injects keys
  fail() { echo "$1-att$att" >> $K; kill -9 $p 2>/dev/null; wait $p 2>/dev/null; cp $L $OUT/fail_att$att.log; }
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
  sleep 130; kill -0 $p 2>/dev/null || { fail died_in_verify; continue; }
  echo "att=$att mission_verified_130s" >> $K
  last=$(grep -ac origin= $L); lastt=$SECONDS; stalls=0
  while kill -0 $p 2>/dev/null && [ $((SECONDS-mt)) -lt $HOLD ]; do
    sleep 5; c=$(grep -ac origin= $L)
    [ "$c" != "$last" ] && { last=$c; lastt=$SECONDS; }
    [ $((SECONDS-lastt)) -gt 30 ] && { stalls=$((stalls+1)); echo "stall t=$((SECONDS-t0))" >> $K; lastt=$SECONDS; }
  done
  alive=0; kill -0 $p 2>/dev/null && alive=1
  kill -9 $p 2>/dev/null; wait $p 2>/dev/null
  echo "fbhash $(grep -a '^.fbhash' $L | sed 's/.*h=//' | fbrun)" >> $K
  echo "tag=$TAG att=$att mission_t=$((mt-t0))s hold=$((SECONDS-mt))s alive_at_end=$alive vi_stalls30s=$stalls godrefills=$(grep -ac "^.godmode" $L) mission_cycles=$(mcycles $L) crashlines=$(grep -ac 'CRASH\|SIGSEGV\|abort' $L)" | tee $OUT/summary
  exit 0
done
echo "tag=$TAG allattempts-failed" | tee $OUT/summary; exit 1
