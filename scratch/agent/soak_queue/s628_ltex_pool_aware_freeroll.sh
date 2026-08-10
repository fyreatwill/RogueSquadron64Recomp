#!/bin/zsh
# s628 freeroll: s627 offline closed GLOBAL O1 (pool4 free >> need, unselected) and
# size-corruption O3 (all sane). Residual: selected-pool OOM (E8 then 0 for flags=0)
# vs no_fit_mystery (maxfree_sel>=need but null). s628 instrument walks to term
# (cap 256), free-always print, maxfree_sel / reason=no_fit|no_fit_unsel|no_fit_mystery.
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
# Requires binary with s628 heap-diag (maxfree_sel in summary). Gated by
# ROGUESQ_LOG_RS_MALLOC_DIAG=1.
#
# Discriminating (scored class-D with fail136c≥1 ∧ posctrl≥1):
#   O1) reason=no_fit or no_fit_unsel, maxfree_sel < need, free sizes sane → H-ltexOOM-sel
#   O3) reason=no_fit_mystery, maxfree_sel ≥ need → freelist walk / other (H-ltexFree/walk)
#   Same-run control: posctrl shows maxfree_sel >> need + free= lines; fail136c nsel=2
#   freeroll: -387 do_rom_read 1st; sinf/matfree/scene/readacct/recov_silent
#
# Exit: 0 scored+ok, 1 scored+CRASH, 2 no recovery-active engagement

set -u
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=1200
MAX_ATTEMPTS=12
HOLD_S=180
START_FLOOR_S=70
RECOV_WAIT_S=50
ENGAGE_WAIT_S=90
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1 ROGUESQ_LOG_SCENE_TRAVERSE=1"

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
MATFREE_N=0
SINFAPPROX_N=0
LTEXMG_N=0
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

# s618 residual -384: buildMaterialFreeList null freelist-base write during mission
# init. Host stack: advanceVideoFrame / initSceneForMission / cinematicLoopBody.
# Prefer buildMaterialFreeList tag; accept advanceVideoFrame+initSceneForMission
# when freelist tag missing (symbolizer miss) and si_addr is null-guest shape.
is_matfree_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'buildMaterialFreeList' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq 'advanceVideoFrame' "$log" 2>/dev/null \
     && grep -aq 'initSceneForMission' "$log" 2>/dev/null; then
    # Prefer null-guest si_addr shape (0x380000000 family) when present
    if grep -aqE 'si_addr=0x38[0-9a-fA-F]{0,9}' "$log" 2>/dev/null; then
      return 0
    fi
    # Stack-only match still counts if cinematicLoopBody also present
    if grep -aq 'cinematicLoopBody' "$log" 2>/dev/null; then
      return 0
    fi
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



# Free-reroll 1st sinfApprox NAN_CHECK Abort (known freeroll noise s214/s215/s621).
# Host stack: buildPositionAndCallTransformHelper ← runModelViewerLoop.
# 2nd same host on recovery-active scores (escalate residual).
is_sinfapprox_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'sinfApprox' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq 'Assertion failed:.*(ctx->f10.fl == ctx->f10.fl)' "$log" 2>/dev/null \
     && grep -aq 'buildPositionAndCallTransformHelper' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
}


# s620/s622 freeroll noise: trackResourceListWithMappingTables+1228 pre-recovery.
# Guest 0x80065e94; si_addr 0x38000000c family. Always free-reroll (not escalated).
is_trackres_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'trackResourceListWithMappingTables' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq 'last-guest-pc\] pc=0x80065e94' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
}

# s619 residual -385: null rs_malloc in loadLevelTextureCache fill at 0x80048250.
# Guarded s620 as [level-tex-malloc-guard]; this detector is the M2 miss path.
is_ltex_null_malloc_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'loadLevelTextureCache' "$log" 2>/dev/null \
     && grep -aq 'load_cutscene' "$log" 2>/dev/null; then
    return 0
  fi
  # si_addr 0x380001054 family + cinematicLoopBody (symbolizer miss)
  if grep -aqE 'si_addr=0x38000[0-9a-fA-F]+' "$log" 2>/dev/null \
     && grep -aq 'cinematicLoopBody' "$log" 2>/dev/null \
     && grep -aq 'load_cutscene\|loadLevelTextureCache' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
}


score_attempt() {
  local log="$1"
  local force6=0 force_skip=0 case6=0 hsel=0 ace80=0 recov=0 crash=0
  local thr11c=0 thr11c_post=0 thr11d_post=0 thr11d_new=0
  local sec4=0 sec4_post=0 sec2=0 sec2_post=0
  local thr12_post=0 cshadow_a=0 cshadow_w=0 ltex=0 ship_store=0 ship_zero_post=0
  local force_old5=0 scenegraph=0 readacct=0 matfree=0 ltexmg=0 ltex_null=0
  local diag_pos=0 diag_fail=0 diag_fail136c=0 diag_ok136c=0 diag_reason=none diag_maxfree= diag_maxfree_sel= diag_nfree_sel=0 diag_need=

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
  is_matfree_crash "$log" && matfree=1
  if [ -f "$log" ]; then
    ltexmg=$(grep -c '\[level-tex-malloc-guard\]' "$log" 2>/dev/null || true)
    ltexmg=${ltexmg:-0}
    diag_pos=$(grep -c '\[rs-malloc-diag\] event=posctrl' "$log" 2>/dev/null || true)
    diag_pos=${diag_pos:-0}
    diag_fail=$(grep -cE '\[rs-malloc-diag\] event=fail( |$)' "$log" 2>/dev/null || true)
    diag_fail=${diag_fail:-0}
    diag_fail136c=$(grep -c '\[rs-malloc-diag\] event=fail136c' "$log" 2>/dev/null || true)
    diag_fail136c=${diag_fail136c:-0}
    diag_ok136c=$(grep -c '\[rs-malloc-diag\] event=ok136c' "$log" 2>/dev/null || true)
    diag_ok136c=${diag_ok136c:-0}
    # s628: summary line carries reason/maxfree_sane; event line has need
    local fline sline
    fline=$(grep '\[rs-malloc-diag\] event=fail136c' "$log" 2>/dev/null | tail -1 || true)
    sline=$(grep '\[rs-malloc-diag\] summary event=fail136c' "$log" 2>/dev/null | tail -1 || true)
    if [ -n "${fline:-}" ]; then
      diag_need=$(printf '%s\n' "$fline" | sed -n 's/.*need=\(0x[0-9A-Fa-f]*\).*/\1/p')
    fi
    if [ -n "${sline:-}" ]; then
      diag_reason=$(printf '%s\n' "$sline" | sed -n 's/.*reason=\([^ ]*\).*/\1/p')
      diag_maxfree=$(printf '%s\n' "$sline" | sed -n 's/.*maxfree_sane=\(0x[0-9A-Fa-f]*\).*/\1/p')
      diag_maxfree_sel=$(printf '%s\n' "$sline" | sed -n 's/.*maxfree_sel=\(0x[0-9A-Fa-f]*\).*/\1/p')
      diag_nfree_sel=$(printf '%s\n' "$sline" | sed -n 's/.*nfree_sel=\([0-9]*\).*/\1/p')
      diag_nfree_sel=${diag_nfree_sel:-0}
    fi
  fi
  is_ltex_null_malloc_crash "$log" && ltex_null=1

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
  elif [ "${ltex_null:-0}" -eq 1 ]; then
    # Unguarded null-malloc residual (-385) — binary stale or guard miss
    class_hint=M2_ltex_null_unguarded
  elif [ "${ltexmg:-0}" -gt 0 ] && [ "$thr12_post" -gt 0 ]; then
    class_hint=M1_ltexmg_thr12
  elif [ "${ltexmg:-0}" -gt 0 ]; then
    # Guard LIVE; thr12 still skipped because early-return is before registerServiceWorker
    class_hint=M1_ltexmg_no_thr12
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
  elif [ "$matfree" -eq 1 ] && [ "$thr11d_new" -gt 0 ]; then
    class_hint=K_matfree_post_thr11d
  elif [ "$matfree" -eq 1 ]; then
    class_hint=K_matfree_other
  elif [ "$scenegraph" -eq 1 ]; then
    class_hint=H_scenegraph_pre_thr11d
  elif [ "$readacct" -eq 1 ]; then
    class_hint=J_readacct_pre_thr11d
  elif [ "$thr11c_post" -gt 0 ] && [ "$thr11d_new" -eq 0 ] && [ "$crash" -eq 0 ]; then
    class_hint=I_thr11_live_no_destroy
  elif [ "$thr11c_post" -gt 0 ] && [ "$thr11d_new" -eq 0 ] && [ "$crash" -eq 1 ]; then
    class_hint=I_thr11_live_other_crash
  elif [ "$thr11d_new" -gt 0 ] && [ "$sec4_post" -gt 0 ] && [ "$crash" -eq 0 ]; then
    class_hint=L_thr11d_hold_no_crash
  elif [ "$crash" -eq 1 ] && [ "$hsel" -eq 1 ]; then
    class_hint=D_other_crash
  fi

  echo "[fast-retry] SCORE force6=$force6 force_old5=$force_old5 force_skip=$force_skip case6=$case6 hsel=$hsel ace80=$ace80 recov768=$recov crash=$crash scenegraph=$scenegraph readacct=$readacct matfree=$matfree ltexmg=$ltexmg ltex_null=$ltex_null thr11c=$thr11c thr11c_post=$thr11c_post thr11d_post=$thr11d_post thr11d_new=$thr11d_new sec4=$sec4 sec4_post=$sec4_post sec2=$sec2 sec2_post=$sec2_post thr12_post=$thr12_post cshadow_a=$cshadow_a cshadow_w=$cshadow_w ltex=$ltex ship_store=$ship_store ship_zero_post=$ship_zero_post diag_pos=$diag_pos diag_fail=$diag_fail diag_fail136c=$diag_fail136c diag_ok136c=$diag_ok136c diag_reason=$diag_reason diag_maxfree=$diag_maxfree diag_maxfree_sel=$diag_maxfree_sel diag_nfree_sel=$diag_nfree_sel diag_need=$diag_need $ctrl_line ctrl_rc=$ctrl_rc class_hint=$class_hint"
  # Dump fail136c / posctrl event+nodes+summary for offline (bounded)
  if [ -f "$log" ] && [ "${diag_fail136c:-0}" -gt 0 ]; then
    echo "[fast-retry] === fail136c block (event+nodes+summary, last cluster) ==="
    # Print from last fail136c event through following summary (≤80 lines)
    local fln
    fln=$(grep -n '\[rs-malloc-diag\] event=fail136c' "$log" 2>/dev/null | tail -1 | cut -d: -f1)
    if [ -n "${fln:-}" ]; then
      sed -n "${fln},$((fln+40))p" "$log" | head -40
    fi
  fi
  if [ -f "$log" ] && [ "${diag_pos:-0}" -gt 0 ]; then
    echo "[fast-retry] === posctrl sample (first event + nodes, first cluster) ==="
    local pln
    pln=$(grep -n '\[rs-malloc-diag\] event=posctrl' "$log" 2>/dev/null | head -1 | cut -d: -f1)
    if [ -n "${pln:-}" ]; then
      sed -n "${pln},$((pln+25))p" "$log" | head -25
    fi
  fi
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
  TAG="s628_ltex_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
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
    # Free-reroll first buildMaterialFreeList null-base crash; 2nd scores
    if is_matfree_crash "$LOG" && [ "$MATFREE_N" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=matfree
      echo "[fast-retry] attempt $ATTEMPT matfree SIGBUS mid-run (1st) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    if is_sinfapprox_crash "$LOG" && [ "$SINFAPPROX_N" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=sinfapprox
      echo "[fast-retry] attempt $ATTEMPT sinfApprox Abort mid-run (1st) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    if is_trackres_crash "$LOG"; then
      EARLY_KILL=1
      EARLY_REASON=trackres
      echo "[fast-retry] attempt $ATTEMPT trackResourceList freeroll noise mid-run — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
  done
  wait "$LAUNCH_PID" 2>/dev/null || true
  RC=$?
  if [ "$EARLY_KILL" -eq 1 ]; then RC=137; fi

  FORCE6=0; FORCE_SKIP=0; CASE6=0; HSEL=0; ACE80=0; RECOV768=0; CRASH=0; MATNOISE=0; MAT3INV=0; SCENEGRAPH=0; READACCT=0; MATFREE=0; SINFAPPROX=0; LTEXMG=0; LTEX_NULL=0
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
    is_matfree_crash "$LOG" && MATFREE=1
    is_sinfapprox_crash "$LOG" && SINFAPPROX=1
    LTEXMG=$(grep -c '\[level-tex-malloc-guard\]' "$LOG" 2>/dev/null || true)
    LTEXMG=${LTEXMG:-0}
    is_ltex_null_malloc_crash "$LOG" && LTEX_NULL=1
    if [ "$LTEXMG" -gt 0 ]; then LTEXMG_N=$(( LTEXMG_N + LTEXMG )); fi
  fi
  DUR=$(( $(date +%s) - NOW ))
  echo "[fast-retry] attempt $ATTEMPT done rc=$RC dur=${DUR}s force6=$FORCE6 force_skip=$FORCE_SKIP case6=$CASE6 hangar_sel=$HSEL ace80=$ACE80 recov768=$RECOV768 crash=$CRASH matnoise=$MATNOISE mat3inv=$MAT3INV scenegraph=$SCENEGRAPH readacct=$READACCT matfree=$MATFREE ltexmg=$LTEXMG ltex_null=$LTEX_NULL early=$EARLY_REASON log=$LOG"

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
    # s628: freeroll recovery-active without thr11d_new (class I) — we need
    # class-D / ltex path for H-ltexOOM. Still require recov768>0 (H-freeroll1).
    if [ "$RECOV768" -eq 1 ] && [ "$LTEXMG" -eq 0 ]; then
      # thr11d_new / ltex: recompute quickly from log (no `local` — top-level while)
      _hsel_l=$(grep -n '\[hangar-sel\]' "$LOG" 2>/dev/null | head -1 | cut -d: -f1)
      _thr11d_new=0
      _ltex=0
      if [ -n "${_hsel_l:-}" ]; then
        _post=$(sed -n "${_hsel_l},\$p" "$LOG")
        _cids=$(printf '%s\n' "$_post" | grep -E '\[thr-create\].*entry=0x8006F2CC' | sed -E 's/.*id=([0-9]+).*/\1/' | sort -u)
        for _cid in $_cids; do
          if printf '%s\n' "$_post" | grep -qE "\[thr-destroy\] id=${_cid} "; then
            _thr11d_new=$(( _thr11d_new + 1 ))
          fi
        done
        _ltex=$(printf '%s\n' "$_post" | grep -c 'level-tex-cache' || true)
        _ltex=${_ltex:-0}
      fi
      if [ "$_thr11d_new" -eq 0 ] || [ "$_ltex" -eq 0 ]; then
        echo "[fast-retry] attempt $ATTEMPT recovery-active but no class-D ltex (thr11d_new=$_thr11d_new ltex=$_ltex ltexmg=0) — free reroll for H-ltexOOM"
        continue
      fi
    fi
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
    if [ "$MATFREE" -eq 1 ] && [ "$EARLY_REASON" = "matfree" ]; then
      MATFREE_N=$(( MATFREE_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but matfree 1st — free reroll (mf_n=$MATFREE_N)"
      continue
    fi
    # Freeroll 1st sinfApprox whether mid-run early-kill or natural Abort
    # completed before poll (same bug class as s620 recovery_silent EARLY_REASON).
    if [ "$SINFAPPROX" -eq 1 ] && [ "$SINFAPPROX_N" -eq 0 ]; then
      SINFAPPROX_N=$(( SINFAPPROX_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but sinfApprox 1st (early=$EARLY_REASON) — free reroll (sinf_n=$SINFAPPROX_N)"
      continue
    fi
    if is_trackres_crash "$LOG"; then
      echo "[fast-retry] attempt $ATTEMPT engaged but trackResourceList freeroll noise (early=$EARLY_REASON) — free reroll"
      continue
    fi
    # s621 fix: freeroll ANY eng+hsel with recov768=0 (not only EARLY_REASON=
    # recovery_silent). Mid-HOLD crashes that die before RECOV_WAIT fires were
    # wrongly scored as "HOLD complete" in s620 (trackResourceList freeroll noise).
    if [ "$RECOV768" -eq 0 ]; then
      RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but recovery-silent (recov768=0 early=$EARLY_REASON crash=$CRASH) — free reroll (silent_n=$RECOV_SILENT_N)"
      continue
    fi
    # recovery-active only
    SCORED_LOG="$LOG"
    SCORED_RC=$RC
    echo "[fast-retry] attempt $ATTEMPT recovery-active engagement -- scoring, no further rerolls"
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
  echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N scenegraph=$SCENEGRAPH_N readacct=$READACCT_N matfree=$MATFREE_N sinfapprox=$SINFAPPROX_N ltexmg=$LTEXMG_N ctrl_fail=$CTRL_FAIL_N attempts=$ATTEMPT"
  exit 2
fi

echo "[fast-retry] === scored attempt analysis: $SCORED_LOG ==="
echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N mat3inv=$MAT3INV_N scenegraph=$SCENEGRAPH_N readacct=$READACCT_N matfree=$MATFREE_N sinfapprox=$SINFAPPROX_N ltexmg=$LTEXMG_N ctrl_fail=$CTRL_FAIL_N attempts=$ATTEMPT"
score_attempt "$SCORED_LOG"

if [ "${SCORED_RC:-1}" -eq 0 ] && ! grep -aq '\[CRASH\]' "$SCORED_LOG" 2>/dev/null; then
  exit 0
fi
exit 1
