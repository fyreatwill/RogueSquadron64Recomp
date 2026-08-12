#!/bin/zsh
# s670 freeroll: item -421, Arm B (H-menu-return-input vs guest-teardown).
#
# Reuses the proven s668 engage/recovery retry loop (force6+inject to reach
# hangar-sel -> recovery 76B768 -> thr11 -> sec4 -> thr12 -> sec2), then hands
# off to scratch/agent/s670_run_mission_keys_postsec2.sh, which log-phase-gates
# a synthetic Start pulse on the REAL "[overlay] start-match: section 2" line
# (not a wall-clock guess) and holds POST_PULSE_HOLD_S longer so the outcome
# lands in the log.
#
# Product defaults only (headers restore ON, drop OFF) -- same config as s668/
# s669 so this is directly comparable to the s669 baseline (packTlut=0,
# section-3 return, thr12/id=13 lifetime ~195-200s post-sec2, no input).
#
# Outcomes (per scratch/agent/NEXT.md item -421):
#   C) pulse prevents section-3 return or fires packTlut -> H-menu-return-input
#      SUPPORTED; residual is input schedule, not FS
#   D) pulse changes nothing (still section-3 return, packTlut=0, thr12
#      lifetime ~= baseline) -> guest-side thr12->sec3 teardown is
#      unconditional; instrument the destroy call site next
# HYPOTHESIS-ID: m3-post-exit-fs-stall
set -u
ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=${BUDGET_S:-2400}
MAX_ATTEMPTS=${MAX_ATTEMPTS:-10}
TARGET_PULSED=${TARGET_PULSED:-2}
START_FLOOR_S=70
RECOV_WAIT_S=50
ENGAGE_WAIT_S=90
ATTEMPT_WALL_S=300
POLL_S=3

SEC2_SETTLE_S=${SEC2_SETTLE_S:-8}
POST_PULSE_HOLD_S=${POST_PULSE_HOLD_S:-180}
MAX_HOLD_S=${MAX_HOLD_S:-500}
SEC2_PULSE_KEYS=${SEC2_PULSE_KEYS:-"start start"}

# Same instrumentation set as s668/s669 (product headers restore + FS inject +
# recovery diagnostics) so this run is directly comparable to that baseline.
# s671: +ROGUESQ_LOG_DL_SYNC2=1 (item -421 E9-alignment discriminator — the
# six-command-aware walker now also counts e9_aligned in [dl-sync-probe2]).
GAME_EXTRA_ENV_BASE="ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_DL_SYNC2=1 ROGUESQ_LOG_E9_DISPATCH=1 ROGUESQ_LOG_RDP_ADVANCE=1 ROGUESQ_LOG_E9_PROVENANCE=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1 ROGUESQ_LOG_SCENE_TRAVERSE=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
PRE_ENG_N=0
RECOV_SILENT_N=0
ENGAGED_N=0
MATERIAL_NOISE_N=0
PULSED_N=0
SEC3_AFTER_PULSE_N=0
PACKTLUT_N=0
SCORED_LOGS=()

kill_game() {
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  /usr/bin/pkill -9 -f 's670_run_mission_keys_postsec2.sh' 2>/dev/null || true
}

score_log() {
  local log="$1"
  # s670 bugfix (found scoring attempt 5 by hand): [sec2-pulse] lines are
  # printed by the WRAPPER script to launcher.stdout, not to the game's own
  # run.log -- grepping run.log for the pulse marker always reads 0. Also,
  # thr-create/destroy for entry=0x800495FC recurs across earlier section-3/
  # section-4 cycles (ids 5, 12, ... before the final id post-sec2), so the
  # FIRST occurrence in the whole file is the wrong one; must scope to lines
  # at/after sec2_ln, same as scratch/agent/s669_postsec2_offline_score.py.
  local launcher_log="${log%/run.log}/launcher.stdout"
  local sec2 sec3 pack pulsed sec2_ln sec3_ln pulse_ln thr13c thr13d
  sec2=$(grep -ac '\[overlay\] start-match: section 2' "$log" 2>/dev/null || true); sec2=${sec2:-0}
  sec3=$(grep -ac '\[overlay\] start-match: section 3' "$log" 2>/dev/null || true); sec3=${sec3:-0}
  pack=$(grep -ac 'packTlut' "$log" 2>/dev/null || true); pack=${pack:-0}
  pulsed=$(grep -ac '\[sec2-pulse\] fired' "$launcher_log" 2>/dev/null || true); pulsed=${pulsed:-0}
  sec2_ln=$(grep -n '\[overlay\] start-match: section 2' "$log" 2>/dev/null | head -1 | cut -d: -f1)
  sec3_ln=""
  pulse_ln=$(grep -n '\[sec2-pulse\] fired' "$launcher_log" 2>/dev/null | head -1 | cut -d: -f1)
  thr13c=""
  thr13d=""
  if [ -n "${sec2_ln:-}" ]; then
    sec3_ln=$(sed -n "${sec2_ln},\$p" "$log" | grep -n '\[overlay\] start-match: section 3' | head -1 | cut -d: -f1)
    thr13c=$(sed -n "${sec2_ln},\$p" "$log" | grep -n '\[thr-create\].*0x800495FC' | head -1 | cut -d: -f1)
    if [ -n "${thr13c:-}" ]; then
      thr13c=$(( thr13c + sec2_ln - 1 ))
      thr13d=$(sed -n "${thr13c},\$p" "$log" | grep -n '\[thr-destroy\] id=' | head -1 | cut -d: -f1)
    fi
  fi
  echo "[s670-score] log=$log sec2_n=$sec2 sec3_n=$sec3 pack_n=$pack pulsed_n=$pulsed sec2_ln=${sec2_ln:-none} sec3_after_pulse=${sec3_ln:+yes} pulse_ln=${pulse_ln:-none} thr13c_post_sec2=${thr13c:-none} thr13d_post_sec2=${thr13d:-none(still-alive)}"
  if [ "$pulsed" -gt 0 ]; then
    PULSED_N=$(( PULSED_N + 1 ))
    if [ -n "${sec3_ln:-}" ]; then SEC3_AFTER_PULSE_N=$(( SEC3_AFTER_PULSE_N + 1 )); fi
    if [ "$pack" -gt 0 ]; then PACKTLUT_N=$(( PACKTLUT_N + 1 )); fi
  fi
}

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  if [ "$REMAIN" -lt "$START_FLOOR_S" ]; then
    echo "[s670] budget exhausted (${ELAPSED}s used of ${BUDGET_S}s), stopping"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[s670] hit MAX_ATTEMPTS=$MAX_ATTEMPTS, stopping"
    break
  fi
  TAG="s670_postsec2_pulse_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  LOG="$OUT/run.log"
  kill_game
  sleep 0.3
  echo "[s670] attempt $ATTEMPT starting, ${REMAIN}s left, tag=$TAG"
  mkdir -p "$OUT"
  env PROBE_MODE=start_only SEC2_PULSE=1 SEC2_SETTLE_S=$SEC2_SETTLE_S \
    POST_PULSE_HOLD_S=$POST_PULSE_HOLD_S MAX_HOLD_S=$MAX_HOLD_S \
    SEC2_PULSE_KEYS="$SEC2_PULSE_KEYS" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/agent/s670_run_mission_keys_postsec2.sh" "$TAG" 5 12 \
    >"$OUT/launcher.stdout" 2>"$OUT/launcher.stderr" &
  LAUNCH_PID=$!

  HSEL_T=0
  C5_T=0
  RECOV_SEEN=0
  EARLY_KILL=0
  EARLY_REASON=""
  while kill -0 "$LAUNCH_PID" 2>/dev/null; do
    sleep "$POLL_S"
    NOW2=$(date +%s)
    if [ $(( NOW2 - START_EPOCH )) -ge "$BUDGET_S" ]; then
      EARLY_KILL=1; EARLY_REASON=budget
      kill_game; wait "$LAUNCH_PID" 2>/dev/null || true; break
    fi
    if [ $(( NOW2 - NOW )) -ge "$ATTEMPT_WALL_S" ] && [ "$HSEL_T" -eq 0 ]; then
      EARLY_KILL=1; EARLY_REASON=attempt_wall
      echo "[s670] attempt $ATTEMPT ATTEMPT_WALL expired (0 hangar-sel) — reroll"
      kill_game; wait "$LAUNCH_PID" 2>/dev/null || true; break
    fi
    [ -f "$LOG" ] || continue
    if grep -aq 'SDL_Init failed: The video driver did not add any displays' "$LOG" 2>/dev/null; then
      echo "[s670] SDL has no display; aborting instead of rerolling"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      exit 3
    fi
    if [ "$C5_T" -eq 0 ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
    fi
    if [ "$C5_T" -eq 0 ] && grep -aq '\[hangar-state\].*state=5' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
    fi
    if [ "$C5_T" -gt 0 ] && [ "$HSEL_T" -eq 0 ] && [ $(( NOW2 - C5_T )) -ge "$ENGAGE_WAIT_S" ]; then
      EARLY_KILL=1; EARLY_REASON=engage_timeout
      echo "[s670] attempt $ATTEMPT ENGAGE_WAIT expired — reroll"
      kill_game; wait "$LAUNCH_PID" 2>/dev/null || true; break
    fi
    if [ "$HSEL_T" -eq 0 ] && grep -aq '\[hangar-sel\]' "$LOG" 2>/dev/null; then
      HSEL_T=$NOW2
      echo "[s670] attempt $ATTEMPT hangar-sel seen at +$((NOW2-NOW))s"
    fi
    if [ "$HSEL_T" -gt 0 ] && [ "$RECOV_SEEN" -eq 0 ]; then
      if grep -aqE 'addr=0x0076B768' "$LOG" 2>/dev/null; then
        RECOV_SEEN=1
        echo "[s670] attempt $ATTEMPT recovery 76B768 seen at +$((NOW2-NOW))s — letting pulse-hold run"
      elif [ $(( NOW2 - HSEL_T )) -ge "$RECOV_WAIT_S" ]; then
        EARLY_KILL=1; EARLY_REASON=recovery_silent
        echo "[s670] attempt $ATTEMPT RECOV_WAIT expired (0×76B768) — reroll"
        kill_game; wait "$LAUNCH_PID" 2>/dev/null || true; break
      fi
    fi
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" 2>/dev/null || grep -aq 'findOrCreateMaterial+' "$LOG" 2>/dev/null; then
      if grep -aq '\[CRASH\]' "$LOG" 2>/dev/null; then
        EARLY_KILL=1; EARLY_REASON=matnoise
        echo "[s670] attempt $ATTEMPT material-noise crash mid-run — reroll"
        kill_game; wait "$LAUNCH_PID" 2>/dev/null || true; break
      fi
    fi
  done
  wait "$LAUNCH_PID" 2>/dev/null || true
  RC=$?
  if [ "$EARLY_KILL" -eq 1 ]; then RC=137; fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[s670] attempt $ATTEMPT done rc=$RC dur=${DUR}s hsel=$([ $HSEL_T -gt 0 ] && echo 1 || echo 0) recov=$RECOV_SEEN early=$EARLY_REASON log=$LOG"

  if [ "$EARLY_REASON" = "matnoise" ]; then
    MATERIAL_NOISE_N=$(( MATERIAL_NOISE_N + 1 )); continue
  fi
  if [ "$HSEL_T" -eq 0 ]; then
    PRE_ENG_N=$(( PRE_ENG_N + 1 )); continue
  fi
  ENGAGED_N=$(( ENGAGED_N + 1 ))
  if [ "$RECOV_SEEN" -eq 0 ]; then
    RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
    echo "[s670] attempt $ATTEMPT engaged but recovery-silent — reroll (silent_n=$RECOV_SILENT_N)"
    continue
  fi

  if [ -f "$LOG" ]; then
    score_log "$LOG"
    SCORED_LOGS+=("$LOG")
  fi

  if [ "$PULSED_N" -ge "$TARGET_PULSED" ]; then
    echo "[s670] hit TARGET_PULSED=$TARGET_PULSED — stop"
    break
  fi
done

kill_game

echo "[s670] === s670 post-sec2 pulse freeroll summary ==="
echo "[s670] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N engaged=$ENGAGED_N attempts=$ATTEMPT"
echo "[s670] pulsed_n=$PULSED_N sec3_after_pulse_n=$SEC3_AFTER_PULSE_N packtlut_n=$PACKTLUT_N"
for lg in "${SCORED_LOGS[@]:-}"; do
  [ -n "$lg" ] && score_log "$lg"
done

if [ "$PULSED_N" -eq 0 ]; then
  echo "[s670] VERDICT: INCONCLUSIVE — sec2 never reached / pulse never fired in any recovery-active attempt"
  exit 2
fi
if [ "$PACKTLUT_N" -gt 0 ]; then
  echo "[s670] VERDICT: Outcome C-strong (packTlut fired $PACKTLUT_N/$PULSED_N post-pulse) — H-menu-return-input SUPPORTED"
  exit 0
fi
if [ "$SEC3_AFTER_PULSE_N" -lt "$PULSED_N" ]; then
  echo "[s670] VERDICT: Outcome C-partial ($((PULSED_N - SEC3_AFTER_PULSE_N))/$PULSED_N pulsed attempts did NOT return to section-3) — H-menu-return-input SUPPORTED (partial)"
  exit 0
fi
echo "[s670] VERDICT: Outcome D (section-3 return in $SEC3_AFTER_PULSE_N/$PULSED_N pulsed attempts, packTlut=0) — H-menu-return-input REFUTED; guest-side thr12->sec3 teardown unconditional"
exit 0
