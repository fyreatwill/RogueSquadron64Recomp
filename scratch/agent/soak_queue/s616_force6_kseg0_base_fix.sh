#!/bin/zsh
# s616: verify FORCE_STATE6 KSEG0 base fix (S32-extended gpr) + class-D path.
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# s615 fold: engaged natural ACE80, force always skip (old=255/110/0), 0×76B768.
# Root cause: case5-entry/force used uint32_t base=0x800D0000 with MEM_BU, which
# on 64-bit computes rdram index 0x1000CC3E7 (OOB). hangar-state (gpr S32 base)
# correctly saw state=5 while case5-entry saw garbage. s613 "force 3→6" never
# touched real hangar state (hangar-state stayed 5 after "write").
#
# Discriminating (scored path = recovery-active thr11d+sec4 OR engaged with
# case5-entry state matching hangar):
#   CTRL) case5-entry state ∈ {3,5,6,8} and matches nearby hangar-state — base fix live
#   FAIL_CTRL) case5-entry still 255/110/other garbage while hangar-state=5 — fix dead
#   A) force6 write old=5 + thr11d+sec4 + craft-shadow guard + thr12/sec2
#   B/C/D) class-D A–D as s615 NEXT.md
#   E) eng + recovery_silent (0×76B768) with CTRL pass — silence independent of force base
#   F) eng + recov + thr11 live (class E ship gate)
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no recovery-active engagement, 3 ctrl fail.

set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=560
MAX_ATTEMPTS=8
HOLD_S=180
START_FLOOR_S=80
RECOV_WAIT_S=100
ENGAGE_WAIT_S=90
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""
MATERIAL_NOISE_N=0
PRE_ENG_N=0
RECOV_SILENT_N=0
MAT3INV_N=0
CTRL_FAIL_N=0

kill_game() {
  /usr/bin/pkill -9 -x RogueSquadron64Recomp 2>/dev/null || true
  /usr/bin/pkill -9 -f 'run_mission_keys.sh' 2>/dev/null || true
}

is_mat3inv_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'mat3x3InverseInto' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq '\[mat3inv-abnormal\]' "$log" 2>/dev/null && grep -aq 'Abort trap\|signal 6' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
}

# Positive control: any case5-entry line with plausible hangar state {0..8},
# and not stuck on classic OOB garbage 255/110 for the whole case5 window.
score_base_ctrl() {
  local log="$1"
  local c5_bad=0 c5_good=0
  # sample case5-entry states
  local states
  states=$(grep -oE '\[case5-entry\] n=[0-9]+ state=[0-9]+' "$log" 2>/dev/null | sed -E 's/.*state=//' | head -20)
  if [ -z "$states" ]; then
    echo "ctrl=no_case5_entry"
    return 1
  fi
  local s
  for s in $states; do
    if [ "$s" -eq 255 ] 2>/dev/null || [ "$s" -eq 110 ] 2>/dev/null || [ "$s" -gt 20 ] 2>/dev/null; then
      c5_bad=$((c5_bad + 1))
    else
      c5_good=$((c5_good + 1))
    fi
  done
  # first case5-entry after hangar hits 5 should be 5 (or 6 if already advanced)
  local first_at_case5
  first_at_case5=$(grep -E '\[case5-entry\] n=0 state=' "$log" 2>/dev/null | head -1 | sed -E 's/.*state=//')
  echo "ctrl_good=$c5_good ctrl_bad=$c5_bad case5_n0_state=${first_at_case5:--}"
  if [ "$c5_good" -ge 1 ] && [ "$c5_bad" -eq 0 ]; then
    return 0
  fi
  # allow mixed if first n=0 is 5 or 6 (fix partially live)
  if [ "${first_at_case5:-x}" = "5" ] || [ "${first_at_case5:-x}" = "6" ]; then
    return 0
  fi
  return 1
}

score_attempt() {
  local log="$1"
  local force6=0 force_skip=0 case6=0 hsel=0 ace80=0 recov=0 crash=0
  local thr11d=0 thr11c=0 sec4=0 sec4_post=0 sec2=0 sec2_post=0
  local thr12=0 cshadow_a=0 cshadow_w=0 ltex=0 ship_store=0
  local force_old5=0

  grep -aq '\[case5-force-state6\]' "$log" 2>/dev/null && force6=1
  grep -aq '\[case5-force-state6-skip\]' "$log" 2>/dev/null && force_skip=1
  grep -aq 'old=5 new=6' "$log" 2>/dev/null && force_old5=1
  grep -aq '\[case6-force-start\]' "$log" 2>/dev/null && case6=1
  grep -aq '\[hangar-sel\]' "$log" 2>/dev/null && hsel=1
  grep -aq 'site=0x800ACE80' "$log" 2>/dev/null && ace80=1
  recov=$(grep -cE 'addr=0x0076B768' "$log" 2>/dev/null || echo 0)
  grep -aq '\[CRASH\]' "$log" 2>/dev/null && crash=1

  thr11c=$(grep -cE '\[thr-create\].*entry=0x8006F2CC' "$log" 2>/dev/null || echo 0)
  # post-hsel thr11 destroy: thr with entry 6F2CC destroyed after hangar-sel
  local hsel_line
  hsel_line=$(grep -n '\[hangar-sel\]' "$log" 2>/dev/null | head -1 | cut -d: -f1)
  if [ -n "${hsel_line:-}" ]; then
    # thr11 create then destroy after hsel
    local post
    post=$(sed -n "${hsel_line},\$p" "$log")
    thr11d=$(printf '%s\n' "$post" | grep -cE '\[thr-destroy\]' || true)
    # better: look for destroy of thr that was created with 6F2CC — approximate via
    # thr-create 6F2CC before hsel still live, and any thr-destroy of high ids after
    sec4_post=$(printf '%s\n' "$post" | grep -c 'start-match: section 4' || true)
    sec2_post=$(printf '%s\n' "$post" | grep -c 'start-match: section 2' || true)
    thr12=$(printf '%s\n' "$post" | grep -cE 'entry=0x800495FC' || true)
    cshadow_a=$(printf '%s\n' "$post" | grep -c 'craft-shadow-asset-guard' || true)
    cshadow_w=$(printf '%s\n' "$post" | grep -c 'craft-shadow-walk-guard' || true)
    ltex=$(printf '%s\n' "$post" | grep -c 'level-tex-cache' || true)
    ship_store=$(printf '%s\n' "$post" | grep -c '\[ship-store\]' || true)
  fi
  sec4=$(grep -c 'start-match: section 4' "$log" 2>/dev/null || echo 0)
  sec2=$(grep -c 'start-match: section 2' "$log" 2>/dev/null || echo 0)

  local ctrl_line
  ctrl_line=$(score_base_ctrl "$log"; echo "ctrl_rc=$?")

  local class_hint=unknown
  if [ "$recov" -eq 0 ] && [ "$hsel" -eq 1 ]; then
    class_hint=E_recovery_silent
  elif [ "$recov" -gt 0 ] && [ "$sec2_post" -gt 0 ]; then
    class_hint=A_sec2
  elif [ "$cshadow_a" -gt 0 ] || [ "$cshadow_w" -gt 0 ]; then
    if [ "$thr12" -gt 0 ] && [ "$sec2_post" -eq 0 ]; then
      class_hint=B_D_guard_thr12_no_sec2
    elif [ "$thr12" -eq 0 ]; then
      class_hint=C_D_guard_no_thr12
    else
      class_hint=A_D_guard_thr12
    fi
  elif [ "$crash" -eq 1 ] && [ "$hsel" -eq 1 ]; then
    class_hint=D_shadow_or_other_crash
  fi

  echo "[fast-retry] SCORE force6=$force6 force_old5=$force_old5 force_skip=$force_skip case6=$case6 hsel=$hsel ace80=$ace80 recov768=$recov crash=$crash thr11c=$thr11c sec4=$sec4 sec4_post=$sec4_post sec2=$sec2 sec2_post=$sec2_post thr12_post=$thr12 cshadow_a=$cshadow_a cshadow_w=$cshadow_w ltex=$ltex ship_store=$ship_store $ctrl_line class_hint=$class_hint"
}

while :; do
  NOW=$(date +%s)
  ELAPSED=$(( NOW - START_EPOCH ))
  REMAIN=$(( BUDGET_S - ELAPSED ))
  if [ "$REMAIN" -lt "$START_FLOOR_S" ]; then
    echo "[fast-retry] budget exhausted (${ELAPSED}s used of ${BUDGET_S}s, remain=${REMAIN}<${START_FLOOR_S}), stopping"
    break
  fi
  ATTEMPT=$(( ATTEMPT + 1 ))
  if [ "$ATTEMPT" -gt "$MAX_ATTEMPTS" ]; then
    echo "[fast-retry] hit MAX_ATTEMPTS=$MAX_ATTEMPTS, stopping"
    break
  fi
  TAG="s616_kseg0_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
  OUT="$ROOT/scratch/s73_post_a_scene/$TAG"
  LOG="$OUT/run.log"
  kill_game
  sleep 0.3
  echo "[fast-retry] attempt $ATTEMPT starting, ${REMAIN}s left, HOLD_S=$HOLD_S RECOV_WAIT_S=$RECOV_WAIT_S ENGAGE_WAIT_S=$ENGAGE_WAIT_S tag=$TAG"
  mkdir -p "$OUT"
  env PROBE_MODE=start_only HOLD_S=$HOLD_S STICK_SCHEDULE="999:sr" \
    GAME_EXTRA_ENV="$GAME_EXTRA_ENV_BASE" \
    zsh "$ROOT/scratch/s73_post_a_scene/run_mission_keys.sh" "$TAG" 5 12 \
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
      EARLY_KILL=1
      EARLY_REASON=budget
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    [ -f "$LOG" ] || continue
    if [ "$C5_T" -eq 0 ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT case5-entry seen at +$((NOW2-NOW))s — ENGAGE_WAIT_S=${ENGAGE_WAIT_S}"
    fi
    if [ "$C5_T" -gt 0 ] && [ "$HSEL_T" -eq 0 ]; then
      if [ $(( NOW2 - C5_T )) -ge "$ENGAGE_WAIT_S" ]; then
        EARLY_KILL=1
        EARLY_REASON=engage_timeout
        echo "[fast-retry] attempt $ATTEMPT ENGAGE_WAIT expired (${ENGAGE_WAIT_S}s post case5-entry, 0 hangar-sel) — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    if [ "$HSEL_T" -eq 0 ] && grep -aq '\[hangar-sel\]' "$LOG" 2>/dev/null; then
      HSEL_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT hangar-sel seen at +$((NOW2-NOW))s — starting RECOV_WAIT_S=${RECOV_WAIT_S}"
    fi
    if [ "$HSEL_T" -gt 0 ] && [ "$RECOV_SEEN" -eq 0 ]; then
      if grep -aqE '\[rdp-fullsync\].*0x0076B768|addr=0x0076B768' "$LOG" 2>/dev/null; then
        RECOV_SEEN=1
        echo "[fast-retry] attempt $ATTEMPT recovery 76B768 seen at +$((NOW2-NOW))s — letting HOLD finish"
      elif [ $(( NOW2 - HSEL_T )) -ge "$RECOV_WAIT_S" ]; then
        EARLY_KILL=1
        EARLY_REASON=recovery_silent
        echo "[fast-retry] attempt $ATTEMPT RECOV_WAIT expired (${RECOV_WAIT_S}s post hangar-sel, 0×76B768) — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" 2>/dev/null || \
       grep -aq 'findOrCreateMaterial+' "$LOG" 2>/dev/null; then
      if grep -aq '\[CRASH\]' "$LOG" 2>/dev/null; then
        EARLY_KILL=1
        EARLY_REASON=matnoise
        echo "[fast-retry] attempt $ATTEMPT material-noise crash mid-run — SIGKILL free reroll"
        kill_game
        wait "$LAUNCH_PID" 2>/dev/null || true
        break
      fi
    fi
    if is_mat3inv_crash "$LOG"; then
      EARLY_KILL=1
      EARLY_REASON=mat3inv
      echo "[fast-retry] attempt $ATTEMPT mat3inv Abort mid-run — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
  done
  wait "$LAUNCH_PID" 2>/dev/null || true
  RC=$?
  if [ "$EARLY_KILL" -eq 1 ]; then RC=137; fi

  FORCE6=0; FORCE_SKIP=0; CASE6=0; HSEL=0; ACE80=0; RECOV768=0; CRASH=0; MATNOISE=0; MAT3INV=0
  if [ -f "$LOG" ]; then
    grep -aq '\[case5-force-state6\]' "$LOG" && FORCE6=1
    grep -aq '\[case5-force-state6-skip\]' "$LOG" && FORCE_SKIP=1
    grep -aq '\[case6-force-start\]' "$LOG" && CASE6=1
    grep -aq '\[hangar-sel\]' "$LOG" && HSEL=1
    grep -aq 'site=0x800ACE80' "$LOG" && ACE80=1
    grep -aqE 'addr=0x0076B768' "$LOG" && RECOV768=1
    grep -aq '\[CRASH\]' "$LOG" && CRASH=1
    if grep -aqi 'last-guest-pc\] pc=0x8000e29c' "$LOG" || grep -aq 'findOrCreateMaterial+' "$LOG"; then
      [ "$CRASH" -eq 1 ] && MATNOISE=1
    fi
    is_mat3inv_crash "$LOG" && MAT3INV=1
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 force_skip=$FORCE_SKIP case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 recov768=$RECOV768 crash=$CRASH matnoise=$MATNOISE mat3inv=$MAT3INV early=$EARLY_REASON log=$LOG"

  if [ -f "$LOG" ]; then
    score_attempt "$LOG"
  fi

  # Always score base ctrl on any run that reached case5-entry
  if [ -f "$LOG" ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
    if ! score_base_ctrl "$LOG" >/dev/null; then
      CTRL_FAIL_N=$(( CTRL_FAIL_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT BASE_CTRL_FAIL (case5-entry still OOB garbage) — continue but flag"
    else
      echo "[fast-retry] attempt $ATTEMPT BASE_CTRL_PASS"
    fi
  fi

  if [ "$CASE6" -eq 1 ] && [ "$HSEL" -eq 1 ]; then
    if [ "$MATNOISE" -eq 1 ]; then
      MATERIAL_NOISE_N=$(( MATERIAL_NOISE_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but material-noise — free reroll (noise_n=$MATERIAL_NOISE_N)"
      continue
    fi
    if [ "$MAT3INV" -eq 1 ]; then
      MAT3INV_N=$(( MAT3INV_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but mat3inv — free reroll (mat3inv_n=$MAT3INV_N)"
      continue
    fi
    if [ "$RECOV768" -eq 0 ] && [ "$EARLY_REASON" = "recovery_silent" ]; then
      RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but recovery-silent (0×76B768) -- free reroll (silent_n=$RECOV_SILENT_N)"
      continue
    fi
    if [ "$RECOV768" -eq 1 ]; then
      SCORED_LOG="$LOG"
      SCORED_RC=$RC
      echo "[fast-retry] attempt $ATTEMPT recovery-active engagement -- scoring, no further rerolls"
      break
    fi
    # engaged with recov not seen but HOLD finished without early recovery_silent
    SCORED_LOG="$LOG"
    SCORED_RC=$RC
    echo "[fast-retry] attempt $ATTEMPT engaged HOLD complete -- scoring"
    break
  fi

  if [ "$EARLY_REASON" = "budget" ]; then
    echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll (pre_eng_n budget)"
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
    continue
  fi
  if [ "$HSEL" -eq 0 ]; then
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
    echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll (pre_eng_n=$PRE_ENG_N)"
    continue
  fi
done

kill_game

if [ -n "$SCORED_LOG" ]; then
  echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
  echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N ctrl_fail=$CTRL_FAIL_N attempts=$ATTEMPT"
  score_attempt "$SCORED_LOG"
  if [ "$CTRL_FAIL_N" -gt 0 ] && ! score_base_ctrl "$SCORED_LOG" >/dev/null; then
    echo "[fast-retry] VERDICT=ctrl_fail"
    exit 3
  fi
  if grep -aq '\[CRASH\]' "$SCORED_LOG" 2>/dev/null; then
    exit 1
  fi
  exit 0
fi

echo "[fast-retry] no recovery-active engagement within budget (attempts=$ATTEMPT pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N ctrl_fail=$CTRL_FAIL_N)"
# If we saw case5 and ctrl consistently failed, exit 3
if [ "$CTRL_FAIL_N" -gt 0 ] && [ "$PRE_ENG_N" -lt "$ATTEMPT" ]; then
  exit 3
fi
exit 2
