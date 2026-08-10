#!/bin/zsh
# s618: free-reroll post-force readAccountForSelectionScreen SIGBUS (1× s617 scored)
# + fixed thr11d_post (only destroy of post-hsel 6F2CC thr, not any thr-destroy)
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# s617 fold (scored recovery-active a1):
#   - BASE_CTRL_PASS case5_n0_state=5; force6=1 force_old5=1 hangar 5→6→8
#   - recov768=7952; thr11c_post=1; thr11d_post script=1 was FALSE POSITIVE
#     (destroy id=10 OLD thr11; NEW id=11 never destroyed)
#   - sec4_post=0 thr12=0 cshadow=0; ship_store=1 ship_zero_post=1
#   - scenegraph=0 → H-sg1 SUPPORTED; -382 stays 1× free-reroll soft-park
#   - crash local-symtab said rebuildActiveDisplayObjectList+540 — WRONG
#     nm/atos truth: readAccountForSelectionScreen+604 (guest 0x800B85B4 family)
#     si_addr=0x3811c000e x9=0x811c000e; last-guest-pc=0x80022160 STALE
#     caller: menuControllerInput jump-table case 1 (NOT hangar state 6)
#
# Discriminating (scored path = recovery-active after free-reroll):
#   G) thr11d_new>=1 ∧ sec4_post>=1 ∧ (cshadow|thr12|sec2) — class-D path live
#   H) scenegraph 2nd same host stack — escalate -382
#   J) readacct 2nd same host stack — escalate -383 (site audit / KSEG0 idiom)
#   I) thr11c_post>=1 thr11d_new=0 no crash / other crash — ship/handoff
#   A–D) class-D craft-shadow when guards/thr12 fire
#   mat3inv / matnoise / recovery_silent / scenegraph-1st / readacct-1st — free-reroll
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no recovery-active engagement

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

GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1 ROGUESQ_LOG_SCENE_TRAVERSE=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""
MATERIAL_NOISE_N=0
PRE_ENG_N=0
RECOV_SILENT_N=0
MAT3INV_N=0
SCENEGRAPH_N=0
READACCT_N=0
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

# Free-reroll class for 1× s616 signature (same host stack). 2nd occ scored not rerolled.
is_scenegraph_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  grep -aq 'traverseSceneGraphRecursive' "$log" 2>/dev/null || return 1
  # Prefer host stack match; si_addr 0x38000* is supporting not required
  if grep -aq 'setupCameraMatrices' "$log" 2>/dev/null && grep -aq 'runModelViewerLoop' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
}

# s617 residual: true host is readAccountForSelectionScreen (nm/atos). local-symtab
# often mislabels as rebuildActiveDisplayObjectList+540 — accept either host tag
# when stack is menuControllerInput/runModelViewerLoop and si_addr looks OOB-guest.
is_readacct_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'readAccountForSelectionScreen' "$log" 2>/dev/null; then
    return 0
  fi
  # local-symtab mislabel path: rebuildActiveDisplayObjectList + runModelViewerLoop
  # + menuOverlayInit, WITHOUT rs_free (older heap family)
  if grep -aq 'rebuildActiveDisplayObjectList' "$log" 2>/dev/null \
     && grep -aq 'runModelViewerLoop' "$log" 2>/dev/null \
     && grep -aq 'menuOverlayInit' "$log" 2>/dev/null; then
    # Exclude classic rs_free←rebuild heap family if present as sole signal
    if grep -aq 'rs_free' "$log" 2>/dev/null && ! grep -aq 'readAccount' "$log" 2>/dev/null; then
      return 1
    fi
    return 0
  fi
  return 1
}

score_base_ctrl() {
  local log="$1"
  local c5_bad=0 c5_good=0
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
  local first_at_case5
  first_at_case5=$(grep -E '\[case5-entry\] n=0 state=' "$log" 2>/dev/null | head -1 | sed -E 's/.*state=//')
  echo "ctrl_good=$c5_good ctrl_bad=$c5_bad case5_n0_state=${first_at_case5:--}"
  if [ "$c5_good" -ge 1 ] && [ "$c5_bad" -eq 0 ]; then
    return 0
  fi
  if [ "${first_at_case5:-x}" = "5" ] || [ "${first_at_case5:-x}" = "6" ]; then
    return 0
  fi
  return 1
}

# Numeric grep -c helper: never prints a second zero via || echo 0
gcount() {
  local n
  n=$(grep -cE "$1" "$2" 2>/dev/null) || n=0
  printf '%s' "${n:-0}"
}

score_attempt() {
  local log="$1"
  local force6=0 force_skip=0 case6=0 hsel=0 ace80=0 recov=0 crash=0
  local thr11c=0 thr11c_post=0 thr11d_post=0 thr11d_new=0
  local sec4=0 sec4_post=0 sec2=0 sec2_post=0
  local thr12_post=0 cshadow_a=0 cshadow_w=0 ltex=0 ship_store=0 ship_zero_post=0
  local force_old5=0 scenegraph=0 readacct=0

  grep -aq '\[case5-force-state6\]' "$log" 2>/dev/null && force6=1
  grep -aq '\[case5-force-state6-skip\]' "$log" 2>/dev/null && force_skip=1
  grep -aq 'old=5 new=6' "$log" 2>/dev/null && force_old5=1
  grep -aq '\[case6-force-start\]' "$log" 2>/dev/null && case6=1
  grep -aq '\[hangar-sel\]' "$log" 2>/dev/null && hsel=1
  grep -aq 'site=0x800ACE80' "$log" 2>/dev/null && ace80=1
  recov=$(gcount 'addr=0x0076B768' "$log")
  grep -aq '\[CRASH\]' "$log" 2>/dev/null && crash=1
  is_scenegraph_crash "$log" && scenegraph=1
  is_readacct_crash "$log" && readacct=1

  thr11c=$(gcount '\[thr-create\].*entry=0x8006F2CC' "$log")
  sec4=$(gcount 'start-match: section 4' "$log")
  sec2=$(gcount 'start-match: section 2' "$log")

  local hsel_line
  hsel_line=$(grep -n '\[hangar-sel\]' "$log" 2>/dev/null | head -1 | cut -d: -f1)
  if [ -n "${hsel_line:-}" ]; then
    local post
    post=$(sed -n "${hsel_line},\$p" "$log")
    thr11c_post=$(printf '%s\n' "$post" | grep -cE '\[thr-create\].*entry=0x8006F2CC' || true)
    thr11c_post=${thr11c_post:-0}
    # thr11d_post (LEGACY, s617-buggy): any thr-destroy after hsel — inflated by
    # destroy of pre-hsel thr11. Kept for continuity only.
    thr11d_post=$(printf '%s\n' "$post" | grep -cE '\[thr-destroy\] id=' || true)
    thr11d_post=${thr11d_post:-0}
    # thr11d_new (s618): destroy of an id that was thr-created post-hsel with
    # entry=0x8006F2CC. This is the real thr11d pipeline metric.
    thr11d_new=0
    local create_ids destroy_line cid
    create_ids=$(printf '%s\n' "$post" | grep -E '\[thr-create\].*entry=0x8006F2CC' | sed -E 's/.*id=([0-9]+).*/\1/' | sort -u)
    for cid in $create_ids; do
      if printf '%s\n' "$post" | grep -qE "\[thr-destroy\] id=${cid} "; then
        thr11d_new=$(( thr11d_new + 1 ))
      fi
    done
    sec4_post=$(printf '%s\n' "$post" | grep -c 'start-match: section 4' || true)
    sec4_post=${sec4_post:-0}
    sec2_post=$(printf '%s\n' "$post" | grep -c 'start-match: section 2' || true)
    sec2_post=${sec2_post:-0}
    thr12_post=$(printf '%s\n' "$post" | grep -cE 'entry=0x800495FC' || true)
    thr12_post=${thr12_post:-0}
    cshadow_a=$(printf '%s\n' "$post" | grep -c 'craft-shadow-asset-guard' || true)
    cshadow_a=${cshadow_a:-0}
    cshadow_w=$(printf '%s\n' "$post" | grep -c 'craft-shadow-walk-guard' || true)
    cshadow_w=${cshadow_w:-0}
    ltex=$(printf '%s\n' "$post" | grep -c 'level-tex-cache' || true)
    ltex=${ltex:-0}
    ship_store=$(printf '%s\n' "$post" | grep -c '\[ship-store\]' || true)
    ship_store=${ship_store:-0}
    ship_zero_post=$(printf '%s\n' "$post" | grep -c '\[ship-zero\]' || true)
    ship_zero_post=${ship_zero_post:-0}
  fi

  local ctrl_line ctrl_rc=1
  ctrl_line=$(score_base_ctrl "$log") && ctrl_rc=0 || ctrl_rc=1

  local class_hint=unknown
  if [ "$recov" -eq 0 ] && [ "$hsel" -eq 1 ]; then
    class_hint=E_recovery_silent
  elif [ "$sec2_post" -gt 0 ]; then
    class_hint=A_sec2
  elif [ "$cshadow_a" -gt 0 ] || [ "$cshadow_w" -gt 0 ]; then
    if [ "$thr12_post" -gt 0 ] && [ "$sec2_post" -eq 0 ]; then
      class_hint=B_D_guard_thr12_no_sec2
    elif [ "$thr12_post" -eq 0 ]; then
      class_hint=C_D_guard_no_thr12
    else
      class_hint=A_D_guard_thr12
    fi
  elif [ "$scenegraph" -eq 1 ]; then
    class_hint=H_scenegraph_pre_thr11d
  elif [ "$readacct" -eq 1 ]; then
    class_hint=J_readacct_pre_thr11d
  elif [ "$thr11c_post" -gt 0 ] && [ "$thr11d_new" -eq 0 ] && [ "$crash" -eq 0 ]; then
    class_hint=I_thr11_live_no_destroy
  elif [ "$thr11c_post" -gt 0 ] && [ "$thr11d_new" -eq 0 ] && [ "$crash" -eq 1 ]; then
    class_hint=I_thr11_live_other_crash
  elif [ "$crash" -eq 1 ] && [ "$hsel" -eq 1 ]; then
    class_hint=D_other_crash
  fi

  echo "[fast-retry] SCORE force6=$force6 force_old5=$force_old5 force_skip=$force_skip case6=$case6 hsel=$hsel ace80=$ace80 recov768=$recov crash=$crash scenegraph=$scenegraph readacct=$readacct thr11c=$thr11c thr11c_post=$thr11c_post thr11d_post=$thr11d_post thr11d_new=$thr11d_new sec4=$sec4 sec4_post=$sec4_post sec2=$sec2 sec2_post=$sec2_post thr12_post=$thr12_post cshadow_a=$cshadow_a cshadow_w=$cshadow_w ltex=$ltex ship_store=$ship_store ship_zero_post=$ship_zero_post $ctrl_line ctrl_rc=$ctrl_rc class_hint=$class_hint"
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
  TAG="s618_ra_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
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
    # Free-reroll first scenegraph crash; 2nd occ (SCENEGRAPH_N>=1 already) scores
    if is_scenegraph_crash "$LOG" && [ "$SCENEGRAPH_N" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=scenegraph
      echo "[fast-retry] attempt $ATTEMPT scenegraph SIGBUS mid-run (1st) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    # Free-reroll first readAccount (or local-symtab rebuild mislabel) crash
    if is_readacct_crash "$LOG" && [ "$READACCT_N" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=readacct
      echo "[fast-retry] attempt $ATTEMPT readacct SIGBUS mid-run (1st) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
  done
  wait "$LAUNCH_PID" 2>/dev/null || true
  RC=$?
  if [ "$EARLY_KILL" -eq 1 ]; then RC=137; fi

  FORCE6=0; FORCE_SKIP=0; CASE6=0; HSEL=0; ACE80=0; RECOV768=0; CRASH=0; MATNOISE=0; MAT3INV=0; SCENEGRAPH=0; READACCT=0
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
    is_scenegraph_crash "$LOG" && SCENEGRAPH=1
    is_readacct_crash "$LOG" && READACCT=1
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 force_skip=$FORCE_SKIP case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 recov768=$RECOV768 crash=$CRASH matnoise=$MATNOISE mat3inv=$MAT3INV scenegraph=$SCENEGRAPH readacct=$READACCT early=$EARLY_REASON log=$LOG"

  if [ -f "$LOG" ]; then
    score_attempt "$LOG"
  fi

  if [ -f "$LOG" ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
    if ! score_base_ctrl "$LOG" >/dev/null; then
      CTRL_FAIL_N=$(( CTRL_FAIL_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT BASE_CTRL_FAIL"
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
    if [ "$SCENEGRAPH" -eq 1 ] && [ "$EARLY_REASON" = "scenegraph" ]; then
      SCENEGRAPH_N=$(( SCENEGRAPH_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but scenegraph 1st — free reroll (sg_n=$SCENEGRAPH_N)"
      continue
    fi
    if [ "$READACCT" -eq 1 ] && [ "$EARLY_REASON" = "readacct" ]; then
      READACCT_N=$(( READACCT_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but readacct 1st — free reroll (ra_n=$READACCT_N)"
      continue
    fi
    if [ "$RECOV768" -eq 0 ] && [ "$EARLY_REASON" = "recovery_silent" ]; then
      RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but recovery-silent — free reroll (silent_n=$RECOV_SILENT_N)"
      continue
    fi
    if [ "$RECOV768" -eq 1 ]; then
      # 2nd scenegraph on recovery-active: score, do not reroll
      SCORED_LOG="$LOG"
      SCORED_RC=$RC
      echo "[fast-retry] attempt $ATTEMPT recovery-active engagement -- scoring, no further rerolls"
      break
    fi
    SCORED_LOG="$LOG"
    SCORED_RC=$RC
    echo "[fast-retry] attempt $ATTEMPT engaged HOLD complete -- scoring"
    break
  fi

  if [ "$EARLY_REASON" = "budget" ]; then
    echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll"
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
    continue
  fi
  if [ "$EARLY_REASON" = "engage_timeout" ]; then
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
    echo "[fast-retry] attempt $ATTEMPT engage_timeout -- free reroll"
    continue
  fi
  # default: pre-eng crash / other
  PRE_ENG_N=$(( PRE_ENG_N + 1 ))
  echo "[fast-retry] attempt $ATTEMPT pre-eng or unscored -- free reroll"
done

kill_game

if [ -z "$SCORED_LOG" ]; then
  echo "[fast-retry] === no recovery-active scored attempt ==="
  echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N scenegraph=$SCENEGRAPH_N readacct=$READACCT_N ctrl_fail=$CTRL_FAIL_N attempts=$ATTEMPT"
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N scenegraph=$SCENEGRAPH_N readacct=$READACCT_N ctrl_fail=$CTRL_FAIL_N attempts=$ATTEMPT"
score_attempt "$SCORED_LOG"

if [ "${SCORED_RC:-1}" -eq 0 ] && ! grep -aq '\[CRASH\]' "$SCORED_LOG" 2>/dev/null; then
  exit 0
fi
exit 1
