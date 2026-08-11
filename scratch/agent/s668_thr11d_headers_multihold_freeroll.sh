#!/bin/zsh
# s668 freeroll: thr11d multi-hold rate under product multi-header restore.
#
# s667 closed fail136c residual (H-headers-fail136); thr11d was 0/2 recovery-
# fired holds (UNEVALUABLE). This run targets ≥5 recovery-fired full HOLDs
# under product defaults (headers restore ON, drop OFF).
#
# Product defaults only — NO DROP_GARBAGE_CIMG, NO FL_HDR_RESTORE=0,
# NO ALLOW_*, NO FL_RESTORE_MODE=body.
# Score per recovery-fired full HOLD: thr11d_new, ship_store max n, [mv-b8-set],
# fail136c (expect 0), next_ok, freelist 0x2/0x60 hb.
#
# Outcomes:
#   A) thr11d_new ≥1 on ≥1/3 recovery-fired → headers product thr11d LIVE
#   B) recovery fires but thr11d=0 and ship n≤2 always → residual is ship/B8
#   C) recovery drought returns → headers regression; bisect vs s667
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
set -u
ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S=${BUDGET_S:-1800}
MAX_ATTEMPTS=${MAX_ATTEMPTS:-16}
HOLD_S=${HOLD_S:-210}
TARGET_RECOV_FULL=${TARGET_RECOV_FULL:-5}
START_FLOOR_S=70
RECOV_WAIT_S=50
ENGAGE_WAIT_S=90
# s660: without case5-entry ENGAGE_WAIT never arms; a hangar-state=3 stall
# burned the whole 1200s budget on att1. Cap each attempt wall-clock.
ATTEMPT_WALL_S=300
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1 ROGUESQ_LOG_SCENE_TRAVERSE=1"

START_EPOCH=$(date +%s)
ATTEMPT=0
SCORED_LOG=""
SCORED_RC=""
MATERIAL_NOISE_N=0
PRE_ENG_N=0
RECOV_SILENT_N=0
RECOV_ACTIVE_N=0
RECOV_FULL_N=0
THR11D_HIT_N=0
ENGAGED_N=0
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

is_scenegraph_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  grep -aq 'traverseSceneGraphRecursive' "$log" 2>/dev/null || return 1
  if grep -aq 'setupCameraMatrices' "$log" 2>/dev/null && grep -aq 'runModelViewerLoop' "$log" 2>/dev/null; then
    return 0
  fi
  return 1
}

is_readacct_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'readAccountForSelectionScreen' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq 'rebuildActiveDisplayObjectList' "$log" 2>/dev/null \
     && grep -aq 'runModelViewerLoop' "$log" 2>/dev/null \
     && grep -aq 'menuOverlayInit' "$log" 2>/dev/null; then
    if grep -aq 'rs_free' "$log" 2>/dev/null && ! grep -aq 'readAccount' "$log" 2>/dev/null; then
      return 1
    fi
    return 0
  fi
  return 1
}

is_matfree_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'buildMaterialFreeList' "$log" 2>/dev/null; then
    return 0
  fi
  if grep -aq 'advanceVideoFrame' "$log" 2>/dev/null \
     && grep -aq 'initSceneForMission' "$log" 2>/dev/null; then
    if grep -aqE 'si_addr=0x38[0-9a-fA-F]{0,9}' "$log" 2>/dev/null; then
      return 0
    fi
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

gcount() {
  local n
  n=$(grep -cE "$1" "$2" 2>/dev/null) || n=0
  printf '%s' "${n:-0}"
}

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

is_ltex_null_malloc_crash() {
  local log="$1"
  [ -f "$log" ] || return 1
  grep -aq '\[CRASH\]' "$log" 2>/dev/null || return 1
  if grep -aq 'loadLevelTextureCache' "$log" 2>/dev/null \
     && grep -aq 'load_cutscene' "$log" 2>/dev/null; then
    return 0
  fi
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
  local thr12_post=0 cshadow_a=0 cshadow_w=0 ltex=0 ship_store=0 ship_zero_post=0 ship_max_n=0 ship_n3=0 mv_b8=0 mv_ship_arm=0
  local force_old5=0 scenegraph=0 readacct=0 matfree=0 ltexmg=0 ltex_null=0
  local diag_pos=0 diag_fail=0 diag_fail136c=0 diag_ok136c=0 diag_reason=none diag_maxfree= diag_maxfree_sel= diag_nfree_sel=0 diag_need=
  local dms_n=0 dms_tgt=0 dms_heap=0 dms_sample=0 flz_to_zero=0 flz_hb=0 flz_ctrl=0 flz_bt=0 flz_bt_frames=0
  local flz_gbt=0 flz_gbt_guest=0 flz_gbt_frames=0 flz_pc_fl=0 flz_pc_dms=0 flz_pc_other=0 flz_pc_fl_evt=0 msfl_n=0 flz_fault_n=0 flz_fault_hdr=0 flz_fault_late=0 flz_fault_arm_fl=0 flz_fault_sym="" flz_busy_rearm=0 flz_tz_corr=0 flz_tz_corr_inhdr=0 flz_ring_n=0 flz_ring_inhdr=0 flz_ring_near=0 adlb_n=0 adlb_tgt=0 adlb_near=0 ssnr_n=0 ssnr_tgt=0 ssnr_near=0 fb_n=0 fb_hit=0 skip_wild=0 skip_fl=0

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
    dms_n=$(grep -c '\[drain-mesh-stomp\]' "$log" 2>/dev/null || true)
    dms_n=${dms_n:-0}
    dms_tgt=$(grep -c '\[drain-mesh-stomp\].* TARGET' "$log" 2>/dev/null || true)
    dms_tgt=${dms_tgt:-0}
    dms_heap=$(grep -c '\[drain-mesh-stomp\].* HEAPLIKE' "$log" 2>/dev/null || true)
    dms_heap=${dms_heap:-0}
    dms_sample=$(grep -c '\[drain-mesh-stomp\].* sample' "$log" 2>/dev/null || true)
    dms_sample=${dms_sample:-0}
    flz_to_zero=$(grep -c '\[fl-zero-poll\].*event=to_zero' "$log" 2>/dev/null || true)
    flz_to_zero=${flz_to_zero:-0}
    flz_hb=$(grep -c '\[fl-zero-poll\].*event=heartbeat' "$log" 2>/dev/null || true)
    flz_hb=${flz_hb:-0}
    flz_ctrl=$(grep -c '\[fl-zero-watch\].*event=control' "$log" 2>/dev/null || true)
    flz_ctrl=${flz_ctrl:-0}
    flz_bt=$(grep -c '\[fl-zero-poll-bt\] n=' "$log" 2>/dev/null || true)
    flz_bt=${flz_bt:-0}
    flz_bt_frames=$(grep -c '\[fl-zero-poll-bt\]   \[' "$log" 2>/dev/null || true)
    flz_bt_frames=${flz_bt_frames:-0}
    flz_gbt=$(grep -c '\[fl-zero-poll-gbt\] n=.*to_zero_n=' "$log" 2>/dev/null || true)
    flz_gbt=${flz_gbt:-0}
    # thr_with_guest from summary line (last one wins)
    flz_gbt_guest=$(grep '\[fl-zero-poll-gbt\].*event=summary' "$log" 2>/dev/null \
      | tail -1 | sed -n 's/.*thr_with_guest=\([0-9]*\).*/\1/p')
    flz_gbt_guest=${flz_gbt_guest:-0}
    flz_gbt_frames=$(grep -c '\[fl-zero-poll-gbt\]   thr=' "$log" 2>/dev/null || true)
    flz_gbt_frames=${flz_gbt_frames:-0}
    flz_pc_fl=0; flz_pc_dms=0; flz_pc_other=0; flz_pc_fl_evt=0
    msfl_n=$(grep -c '\[memset-fl-dest\]' "$log" 2>/dev/null || true)
    msfl_n=${msfl_n:-0}
    flz_fault_n=$(grep -c '\[fl-zero-fault\] n=' "$log" 2>/dev/null || true)
    flz_fault_n=${flz_fault_n:-0}
    flz_fault_hdr=$(grep -c 'in_hdr=1' "$log" 2>/dev/null || true)
    flz_fault_hdr=${flz_fault_hdr:-0}
    flz_fault_late=$(grep -c 'late=1' "$log" 2>/dev/null || true)
    flz_fault_late=${flz_fault_late:-0}
    flz_fault_arm_fl=$(grep -c 'event=arm_freelist' "$log" 2>/dev/null || true)
    flz_fault_arm_fl=${flz_fault_arm_fl:-0}
    # last in_hdr=1 fault symbol (writer of freelist header if present)
    flz_fault_sym=$(grep '\[fl-zero-fault\] n=.*in_hdr=1' "$log" 2>/dev/null | tail -1 \
      | sed -n 's/.*sym=\([^ ]*\).*/\1/p')
    flz_fault_sym=${flz_fault_sym:-none}
    flz_busy_rearm=$(grep -c 'event=busy_rearm' "$log" 2>/dev/null || true)
    flz_busy_rearm=${flz_busy_rearm:-0}
    flz_tz_corr=$(grep -c 'event=to_zero_correlate' "$log" 2>/dev/null || true)
    flz_tz_corr=${flz_tz_corr:-0}
    flz_tz_corr_inhdr=$(grep 'event=to_zero_correlate' "$log" 2>/dev/null | grep -c 'last_in_hdr=1' || true)
    flz_tz_corr_inhdr=${flz_tz_corr_inhdr:-0}
    adlb_n=$(grep -c '\[adlb-fl-stomp\]' "$log" 2>/dev/null || true)
    adlb_n=${adlb_n:-0}
    adlb_tgt=$(grep '\[adlb-fl-stomp\].* TARGET' "$log" 2>/dev/null | wc -l | tr -d ' ')
    adlb_tgt=${adlb_tgt:-0}
    adlb_near=$(grep '\[adlb-fl-stomp\].* NEAR' "$log" 2>/dev/null | wc -l | tr -d ' ')
    adlb_near=${adlb_near:-0}
    flz_ring_n=$(grep -c 'event=fault_ring' "$log" 2>/dev/null || true)
    flz_ring_n=${flz_ring_n:-0}
    flz_ring_inhdr=$(grep 'event=fault_ring' "$log" 2>/dev/null | grep -c 'in_hdr=1' || true)
    flz_ring_inhdr=${flz_ring_inhdr:-0}
    flz_ring_near=$(grep 'event=fault_ring' "$log" 2>/dev/null | grep -c 'near_hdr=1' || true)
    flz_ring_near=${flz_ring_near:-0}
    ssnr_n=$(grep -c '\[ssnr-hdr-zero\]' "$log" 2>/dev/null || true)
    ssnr_n=${ssnr_n:-0}
    ssnr_tgt=$(grep '\[ssnr-hdr-zero\].* TARGET' "$log" 2>/dev/null | wc -l | tr -d ' ')
    ssnr_tgt=${ssnr_tgt:-0}
    ssnr_near=$(grep '\[ssnr-hdr-zero\].* NEAR' "$log" 2>/dev/null | wc -l | tr -d ' ')
    ssnr_near=${ssnr_near:-0}
    fb_n=$(grep -c '\[fb-fl-writeback\]' "$log" 2>/dev/null || true)
    fb_n=${fb_n:-0}
    fb_hit=$(grep '\[fb-fl-writeback\].* HIT' "$log" 2>/dev/null | wc -l | tr -d ' ')
    fb_hit=${fb_hit:-0}
    skip_wild=$(grep -c '\[ost-wb\] SKIP_WILD_W' "$log" 2>/dev/null || true)
    skip_wild=${skip_wild:-0}
    skip_fl=$(grep -c '\[ost-wb\] SKIP_FL_HDR' "$log" 2>/dev/null || true)
    skip_fl=${skip_fl:-0}
    allow_wfl=$(grep -c '\[ost-wb\] ALLOW_WILD_FL' "$log" 2>/dev/null || true)
    allow_wfl=${allow_wfl:-0}
    hit_wr=$(grep -c 'HIT_WRITE_RESTORE' "$log" 2>/dev/null || true)
    hit_wr=${hit_wr:-0}
    restore_ok=$(grep '\[fb-fl-hdr-restore\]' "$log" 2>/dev/null | grep -c 'match=1' || true)
    restore_ok=${restore_ok:-0}
    restore_next_ok=$(grep '\[fb-fl-hdr-restore\]' "$log" 2>/dev/null | grep -c 'next_ok=1' || true)
    restore_next_ok=${restore_next_ok:-0}
    restore_snap=$(grep '\[fb-fl-hdr-restore\]' "$log" 2>/dev/null | tail -1 | sed -n 's/.*snap=\(0x[0-9A-Fa-f]*\).*/\1/p')
    restore_snap=${restore_snap:-0}
    zero_node=$(grep -c '\[fl-zero-watch\] event=zero_node' "$log" 2>/dev/null || true)
    zero_node=${zero_node:-0}
    prod_banner=$(grep -c 'product restore=.*mode=' "$log" 2>/dev/null || true)
    prod_banner=${prod_banner:-0}
    if [ -f "$log" ]; then
      eval $(python3 - "$log" <<'PY'
import re,sys
log=sys.argv[1]
FL=[
 (0x80001acc,0x80001c94),
 (0x80001c98,0x80001f88),
 (0x800078e0,0x80007904),
 (0x800079f0,0x80007cb4),
 (0x80001f8c,0x8000214c),
]
DMS=0x8000834C
fl=dms=other=fl_evt=0
for line in open(log,errors="replace"):
    if "[fl-zero-poll]" not in line or "event=to_zero" not in line:
        continue
    m=re.search(r"guest_pc=(0x[0-9A-Fa-f]+)", line)
    if not m: continue
    pc=int(m.group(1),16)
    prev=re.search(r"prev_f=(0x[0-9A-Fa-f]+) prev_sz=(0x[0-9A-Fa-f]+)", line)
    freelist = bool(prev and prev.group(1)=="0x2" and prev.group(2)=="0x60")
    in_fl=any(lo<=pc<=hi for lo,hi in FL)
    if in_fl:
        fl+=1
        if freelist: fl_evt+=1
    elif pc==DMS:
        dms+=1
    else:
        other+=1
print(f"flz_pc_fl={fl}")
print(f"flz_pc_dms={dms}")
print(f"flz_pc_other={other}")
print(f"flz_pc_fl_evt={fl_evt}")
PY
)
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
    thr11d_post=$(printf '%s\n' "$post" | grep -cE '\[thr-destroy\] id=' || true)
    thr11d_post=${thr11d_post:-0}
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
    ship_max_n=$(printf '%s\n' "$post" | grep '\[ship-store\]' | sed -n 's/.*n=\([0-9]*\).*/\1/p' | sort -n | tail -1)
    ship_max_n=${ship_max_n:-0}
    ship_n3=$(printf '%s\n' "$post" | grep -c '\[ship-store\] n=3' || true)
    ship_n3=${ship_n3:-0}
    mv_b8=$(printf '%s\n' "$post" | grep -c '\[mv-b8-set\]' || true)
    mv_b8=${mv_b8:-0}
    mv_ship_arm=$(printf '%s\n' "$post" | grep -c '\[mv-ship-arm\]' || true)
    mv_ship_arm=${mv_ship_arm:-0}
  else
    ship_max_n=0; ship_n3=0; mv_b8=0; mv_ship_arm=0
  fi

  local ctrl_line ctrl_rc=1
  ctrl_line=$(score_base_ctrl "$log") && ctrl_rc=0 || ctrl_rc=1

  local class_hint=unknown
  if [ "$recov" -eq 0 ] && [ "$hsel" -eq 1 ]; then
    class_hint=E_recovery_silent
  elif [ "${ltex_null:-0}" -eq 1 ]; then
    class_hint=M2_ltex_null_unguarded
  elif [ "${ltexmg:-0}" -gt 0 ] && [ "$thr12_post" -gt 0 ]; then
    class_hint=M1_ltexmg_thr12
  elif [ "${ltexmg:-0}" -gt 0 ]; then
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

  echo "[fast-retry] SCORE force6=$force6 force_old5=$force_old5 force_skip=$force_skip case6=$case6 hsel=$hsel ace80=$ace80 recov768=$recov crash=$crash scenegraph=$scenegraph readacct=$readacct matfree=$matfree ltexmg=$ltexmg ltex_null=$ltex_null thr11c=$thr11c thr11c_post=$thr11c_post thr11d_post=$thr11d_post thr11d_new=$thr11d_new sec4=$sec4 sec4_post=$sec4_post sec2=$sec2 sec2_post=$sec2_post thr12_post=$thr12_post cshadow_a=$cshadow_a cshadow_w=$cshadow_w ltex=$ltex ship_store=$ship_store ship_zero_post=$ship_zero_post ship_max_n=$ship_max_n ship_n3=$ship_n3 mv_b8=$mv_b8 mv_ship_arm=$mv_ship_arm diag_pos=$diag_pos diag_fail=$diag_fail diag_fail136c=$diag_fail136c diag_ok136c=$diag_ok136c diag_reason=$diag_reason diag_maxfree=$diag_maxfree diag_maxfree_sel=$diag_maxfree_sel diag_nfree_sel=$diag_nfree_sel diag_need=$diag_need dms_n=$dms_n dms_tgt=$dms_tgt dms_heap=$dms_heap dms_sample=$dms_sample flz_to_zero=$flz_to_zero flz_hb=$flz_hb flz_ctrl=$flz_ctrl flz_bt=$flz_bt flz_bt_frames=$flz_bt_frames flz_gbt=$flz_gbt flz_gbt_guest=$flz_gbt_guest flz_gbt_frames=$flz_gbt_frames flz_pc_fl=$flz_pc_fl flz_pc_dms=$flz_pc_dms flz_pc_other=$flz_pc_other flz_pc_fl_evt=$flz_pc_fl_evt msfl_n=$msfl_n flz_fault_n=$flz_fault_n flz_fault_hdr=$flz_fault_hdr flz_fault_late=$flz_fault_late flz_fault_arm_fl=$flz_fault_arm_fl flz_fault_sym=$flz_fault_sym flz_busy_rearm=$flz_busy_rearm flz_tz_corr=$flz_tz_corr flz_tz_corr_inhdr=$flz_tz_corr_inhdr flz_ring_n=$flz_ring_n flz_ring_inhdr=$flz_ring_inhdr flz_ring_near=$flz_ring_near adlb_n=$adlb_n adlb_tgt=$adlb_tgt adlb_near=$adlb_near ssnr_n=$ssnr_n ssnr_tgt=$ssnr_tgt ssnr_near=$ssnr_near fb_n=$fb_n fb_hit=$fb_hit skip_wild=$skip_wild skip_fl=$skip_fl allow_wfl=$allow_wfl hit_wr=$hit_wr restore_ok=$restore_ok restore_next_ok=$restore_next_ok restore_snap=$restore_snap zero_node=$zero_node prod_banner=$prod_banner $ctrl_line ctrl_rc=$ctrl_rc class_hint=$class_hint"
  if [ -f "$log" ] && [ "${diag_fail136c:-0}" -gt 0 ]; then
    echo "[fast-retry] === fail136c block (event+nodes+summary, last cluster) ==="
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
  if [ -f "$log" ]; then
    echo "[fast-retry] === drain-mesh-stomp / fl-zero-poll (s644) ==="
    grep '\[drain-mesh-stomp\]' "$log" 2>/dev/null | head -20 || true
    if [ "${dms_tgt:-0}" -gt 0 ] || [ "${dms_heap:-0}" -gt 0 ]; then
      echo "[fast-retry] --- stomp TARGET/HEAPLIKE (all) ---"
      grep -E '\[drain-mesh-stomp\].*(TARGET|HEAPLIKE)' "$log" 2>/dev/null | head -40 || true
    fi
    grep '\[fl-zero-poll\].*event=to_zero' "$log" 2>/dev/null | head -10 || true
    grep '\[fl-zero-watch\].*event=zero_node' "$log" 2>/dev/null | head -8 || true
    echo "[fast-retry] === fl-zero-poll-bt (s644) ==="
    grep '\[fl-zero-poll-bt\]' "$log" 2>/dev/null | head -40 || true
    echo "[fast-retry] === fl-zero-fault / mprotect (s646) ==="
    grep '\[fl-zero-fault\]' "$log" 2>/dev/null | head -40 || true
    echo "[fast-retry] === memset-fl-dest / BREADCRUMB19 (s645) ==="
    grep -a '\[memset-fl-dest\]' "$log" 2>/dev/null | head -20 || true
    echo "[fast-retry] === fl-zero-poll-gbt (s644) ==="
    grep '\[fl-zero-poll-gbt\]' "$log" 2>/dev/null | head -120 || true
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
  TAG="s668_thr11d_${ATTEMPT}_$(date +%Y%m%d%H%M%S)"
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
    # Per-attempt wall: stuck hangar-state=3 never emits case5-entry
    if [ $(( NOW2 - NOW )) -ge "$ATTEMPT_WALL_S" ] && [ "$HSEL_T" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=attempt_wall
      echo "[fast-retry] attempt $ATTEMPT ATTEMPT_WALL expired (${ATTEMPT_WALL_S}s, 0 hangar-sel) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    [ -f "$LOG" ] || continue
    if [ "$C5_T" -eq 0 ] && grep -aq '\[case5-entry\]' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT case5-entry seen at +$((NOW2-NOW))s — ENGAGE_WAIT_S=${ENGAGE_WAIT_S}"
    fi
    # Fallback: hangar-state=5 is equivalent engage signal if case5 log missing
    if [ "$C5_T" -eq 0 ] && grep -aq '\[hangar-state\].*state=5' "$LOG" 2>/dev/null; then
      C5_T=$NOW2
      echo "[fast-retry] attempt $ATTEMPT hangar-state=5 seen at +$((NOW2-NOW))s — ENGAGE_WAIT_S=${ENGAGE_WAIT_S}"
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
    if is_scenegraph_crash "$LOG" && [ "$SCENEGRAPH_N" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=scenegraph
      echo "[fast-retry] attempt $ATTEMPT scenegraph SIGBUS mid-run (1st) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
    if is_readacct_crash "$LOG" && [ "$READACCT_N" -eq 0 ]; then
      EARLY_KILL=1
      EARLY_REASON=readacct
      echo "[fast-retry] attempt $ATTEMPT readacct SIGBUS mid-run (1st) — SIGKILL free reroll"
      kill_game
      wait "$LAUNCH_PID" 2>/dev/null || true
      break
    fi
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
    ENGAGED_N=$(( ENGAGED_N + 1 ))
    # s660: do NOT free-reroll thr11d_new=0 recovery — freelist-intact product
    # path expects thr11d_new=0 fail136c=0 (s658 0/3); rate is the metric.
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
    if [ "$SINFAPPROX" -eq 1 ] && [ "$SINFAPPROX_N" -eq 0 ]; then
      SINFAPPROX_N=$(( SINFAPPROX_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but sinfApprox 1st (early=$EARLY_REASON) — free reroll (sinf_n=$SINFAPPROX_N)"
      continue
    fi
    if is_trackres_crash "$LOG"; then
      echo "[fast-retry] attempt $ATTEMPT engaged but trackResourceList freeroll noise (early=$EARLY_REASON) — free reroll"
      continue
    fi
    if [ "$RECOV768" -eq 0 ]; then
      RECOV_SILENT_N=$(( RECOV_SILENT_N + 1 ))
      echo "[fast-retry] attempt $ATTEMPT engaged but recovery-silent (recov768=0 early=$EARLY_REASON crash=$CRASH) — free reroll (silent_n=$RECOV_SILENT_N)"
      continue
    fi
    # multi-engagement: score every recovery-active; continue for rate
    RECOV_ACTIVE_N=$(( RECOV_ACTIVE_N + 1 ))
    SCORED_LOG="$LOG"
    SCORED_RC=$RC
    # Full HOLD = recovery fired AND attempt not killed early by budget/trackres mid-hold
    FULL_HOLD=1
    if [ "$EARLY_REASON" = "budget" ] || [ "$EARLY_REASON" = "trackres" ]; then
      FULL_HOLD=0
    fi
    # extract thr11d_new / ship_max_n from just-printed SCORE via re-score fields
    T11D=0 SHIPN=0 B8=0 FAIL136=0
    T11D=$(grep -E '\[fast-retry\] SCORE' "$ROOT/scratch/agent/s668_logs/wrapper.stdout" 2>/dev/null | tail -1 | sed -n 's/.*thr11d_new=\([0-9]*\).*/\1/p')
    # re-parse from this log directly (more reliable)
    hsel_line=$(grep -n '\[hangar-sel\]' "$LOG" 2>/dev/null | head -1 | cut -d: -f1)
    if [ -n "${hsel_line:-}" ]; then
      post=$(sed -n "${hsel_line},\$p" "$LOG")
      create_ids=$(printf '%s\n' "$post" | grep -E '\[thr-create\].*entry=0x8006F2CC' | sed -E 's/.*id=([0-9]+).*/\1/' | sort -u)
      T11D=0
      for cid in $create_ids; do
        if printf '%s\n' "$post" | grep -qE "\[thr-destroy\] id=${cid} "; then
          T11D=$(( T11D + 1 ))
        fi
      done
      SHIPN=$(printf '%s\n' "$post" | grep '\[ship-store\]' | sed -n 's/.*n=\([0-9]*\).*/\1/p' | sort -n | tail -1)
      SHIPN=${SHIPN:-0}
      B8=$(printf '%s\n' "$post" | grep -c '\[mv-b8-set\]' || true)
      B8=${B8:-0}
      FAIL136=$(grep -c 'event=fail136c' "$LOG" 2>/dev/null || true)
      FAIL136=${FAIL136:-0}
    fi
    if [ "$FULL_HOLD" -eq 1 ]; then
      RECOV_FULL_N=$(( RECOV_FULL_N + 1 ))
      if [ "${T11D:-0}" -gt 0 ]; then
        THR11D_HIT_N=$(( THR11D_HIT_N + 1 ))
      fi
      echo "[fast-retry] attempt $ATTEMPT recovery-FULL #$RECOV_FULL_N thr11d_new=$T11D ship_max_n=$SHIPN mv_b8=$B8 fail136c=$FAIL136 — continue (target=$TARGET_RECOV_FULL)"
      if [ "$RECOV_FULL_N" -ge "$TARGET_RECOV_FULL" ]; then
        echo "[fast-retry] hit TARGET_RECOV_FULL=$TARGET_RECOV_FULL — stop"
        break
      fi
    else
      echo "[fast-retry] attempt $ATTEMPT recovery-active but NOT full HOLD (early=$EARLY_REASON) thr11d_new=$T11D ship_max_n=$SHIPN — continue (budget)"
    fi
    continue
  fi

  if [ "$EARLY_REASON" = "budget" ]; then
    echo "[fast-retry] attempt $ATTEMPT died pre-engagement -- fast reroll"
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
    continue
  fi
  if [ "$EARLY_REASON" = "engage_timeout" ] || [ "$EARLY_REASON" = "attempt_wall" ]; then
    PRE_ENG_N=$(( PRE_ENG_N + 1 ))
    echo "[fast-retry] attempt $ATTEMPT $EARLY_REASON -- free reroll"
    continue
  fi
  PRE_ENG_N=$(( PRE_ENG_N + 1 ))
  echo "[fast-retry] attempt $ATTEMPT pre-eng or unscored -- free reroll"
done

kill_game

echo "[fast-retry] === s668 thr11d multi-hold freeroll summary ==="
echo "[fast-retry] discard_stats pre_eng=$PRE_ENG_N matnoise=$MATERIAL_NOISE_N recov_silent=$RECOV_SILENT_N recov_active=$RECOV_ACTIVE_N engaged=$ENGAGED_N mat3inv=$MAT3INV_N scenegraph=$SCENEGRAPH_N readacct=$READACCT_N matfree=$MATFREE_N sinfapprox=$SINFAPPROX_N ltexmg=$LTEXMG_N ctrl_fail=$CTRL_FAIL_N attempts=$ATTEMPT"
# Aggregate product restore markers across all attempt logs this session
echo "[fast-retry] === product-path aggregate (all attempt logs) ==="
for d in "$ROOT"/scratch/s73_post_a_scene/s668_thr11d_*; do
  [ -d "$d" ] || continue
  lg="$d/run.log"
  [ -f "$lg" ] || continue
  bn=$(basename "$d")
  hit_wr=$(grep -c 'HIT_WRITE_RESTORE' "$lg" 2>/dev/null || true)
  allow_wfl=$(grep -c 'ALLOW_WILD_FL' "$lg" 2>/dev/null || true)
  restore_n=$(grep -c '\[fb-fl-hdr-restore\]' "$lg" 2>/dev/null || true)
  restore_ok=$(grep '\[fb-fl-hdr-restore\]' "$lg" 2>/dev/null | grep -c 'match=1' || true)
  restore_next_ok=$(grep '\[fb-fl-hdr-restore\]' "$lg" 2>/dev/null | grep -c 'next_ok=1' || true)
  restore_snap=$(grep '\[fb-fl-hdr-restore\]' "$lg" 2>/dev/null | tail -1 | sed -n 's/.*snap=\(0x[0-9A-Fa-f]*\).*/\1/p')
  zero_node=$(grep -c '\[fl-zero-watch\] event=zero_node' "$lg" 2>/dev/null || true)
  fail136c=$(grep -c 'event=fail136c' "$lg" 2>/dev/null || true)
  thr11d_new_n=0
  # cheap thr11d_new proxy: thr-create 0x8006F2CC post-hsel that later destroy
  fl_tz=$(grep '\[fl-zero-poll\].*event=to_zero' "$lg" 2>/dev/null | grep -c 'prev_f=0x2 prev_sz=0x60' || true)
  recov=$(grep -c 'addr=0x0076B768' "$lg" 2>/dev/null || true)
  thr11d=$(grep -c '\[thr-destroy\]' "$lg" 2>/dev/null || true)
  hsel=$(grep -c '\[hangar-sel\]' "$lg" 2>/dev/null || true)
  prod_banner=$(grep -c 'product restore=.*mode=' "$lg" 2>/dev/null || true)
  thr12=$(grep -c 'entry=0x800495FC' "$lg" 2>/dev/null || true)
  echo "[agg] $bn hsel=$hsel recov768=$recov hit_wr=$hit_wr allow_wfl=$allow_wfl restore_n=$restore_n restore_ok=$restore_ok next_ok=$restore_next_ok snap=$restore_snap zero_node=$zero_node fail136c=$fail136c thr12=$thr12 fl_tz_0x2_0x60=$fl_tz prod_banner=$prod_banner"
done

echo "[fast-retry] thr11d multi-hold: recov_full=$RECOV_FULL_N thr11d_hit=$THR11D_HIT_N recov_active=$RECOV_ACTIVE_N engaged=$ENGAGED_N"

if [ -z "$SCORED_LOG" ]; then
  echo "[fast-retry] === no recovery-active scored attempt ==="
  if [ "$ENGAGED_N" -ge 6 ] && [ "$RECOV_ACTIVE_N" -eq 0 ]; then
    echo "[fast-retry] VERDICT: Outcome C (recovery drought under headers, engaged=$ENGAGED_N)"
    exit 3
  fi
  exit 2
fi

echo "[fast-retry] === last recovery-active scored attempt: $SCORED_LOG ==="
score_attempt "$SCORED_LOG"

# thr11d multi-hold verdicts (need ≥3 full HOLDs for A/B; ≥5 preferred)
if [ "$RECOV_FULL_N" -ge 3 ]; then
  # thr11d rate ≥1/3 of full HOLDs → Outcome A
  if [ $(( THR11D_HIT_N * 3 )) -ge "$RECOV_FULL_N" ]; then
    echo "[fast-retry] VERDICT: Outcome A (thr11d_hit=$THR11D_HIT_N / recov_full=$RECOV_FULL_N ≥1/3) — headers product thr11d LIVE"
    exit 0
  fi
  echo "[fast-retry] VERDICT: Outcome B (recovery fires thr11d_hit=$THR11D_HIT_N / recov_full=$RECOV_FULL_N <1/3; ship/B8 residual likely)"
  exit 0
fi
if [ "$RECOV_ACTIVE_N" -gt 0 ]; then
  echo "[fast-retry] VERDICT: INCONCLUSIVE thr11d multi-hold (recov_full=$RECOV_FULL_N <3; need more full HOLDs)"
  exit 0
fi
if [ "${SCORED_RC:-1}" -eq 0 ] && ! grep -aq '\[CRASH\]' "$SCORED_LOG" 2>/dev/null; then
  exit 0
fi
exit 1
