#!/bin/zsh
# s657 complete freelist A/B: ALLOW_WILD_W=1 + ALLOW_FL_HDR=1 with last-line
# copyNativeToRAM HIT_SKIP also gated by ALLOW_FL_HDR (s656 Outcome C fix).
#
# s656 A/B was INVALID for freelist stomp: rs64_writeback_sane allows both
# off, but Framebuffer::copyNativeToRAM still hard-returned on freelist hit
# (HIT_SKIP always). Freelist 0x2/0x60 survived; fb_hit=1 with HIT_SKIP.
# s657 gates that return on ALLOW_FL_HDR; hit logs HIT_WRITE and writes.
#
# Discriminators (engaged = hsel+force6/case6):
#   A) ≥1 recov768 in ≤6 engaged + freelist to_zero 0x2/0x60 may return
#      → H-fl-survive-suppresses-recov SUPPORTED (note thr11d/fail136c)
#   B) 0 recov over ≥5 engaged WITH freelist to_zero 0x2/0x60 LIVE
#      → drought independent of freelist → pure recovery-inject pivot
#   C) freelist still never to_zero + no HIT_WRITE → still incomplete
# Posctrl: ALLOW banners + HIT_WRITE on killer (not HIT_SKIP).
# HYPOTHESIS-ID: m3-post-exit-fs-stall
set -u
ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

BUDGET_S="${BUDGET_S:-1200}"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-12}"
HOLD_S=210
START_FLOOR_S=70
RECOV_WAIT_S=50
ENGAGE_WAIT_S=90
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_ALLOW_WILD_W=1 ROGUESQ_ALLOW_FL_HDR=1 ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1 ROGUESQ_LOG_SCENE_TRAVERSE=1"

SRC=$(ls -t "$ROOT"/scratch/agent/soak_queue/done/s655_allow_wild_w_recov_ab*.sh 2>/dev/null | head -1)
if [ -z "${SRC:-}" ] || [ ! -f "$SRC" ]; then
  # fall back to live harness template
  SRC="$ROOT/scratch/agent/s655_post_fbskip_pipeline_freeroll.sh"
fi
if [ ! -f "$SRC" ]; then
  echo "[s657] missing harness template" >&2
  exit 2
fi
TMP=$(mktemp /tmp/s657_allow_fl_XXXXXX.sh)
sed -e "s|^GAME_EXTRA_ENV_BASE=.*|GAME_EXTRA_ENV_BASE=\"$GAME_EXTRA_ENV_BASE\"|" \
    -e "s|^BUDGET_S=.*|BUDGET_S=$BUDGET_S|" \
    -e "s|^MAX_ATTEMPTS=.*|MAX_ATTEMPTS=$MAX_ATTEMPTS|" \
    -e 's/s655_ab_/s657_flc_/g' \
    -e 's/s655_post_/s657_flc_/g' \
    -e 's/s656_flhdr_/s657_flc_/g' \
    -e 's/tag=s655/tag=s657/g' \
    -e 's/tag=s656/tag=s657/g' \
    "$SRC" >"$TMP"
# Force BUDGET if template uses different form
if ! grep -q '^BUDGET_S=' "$TMP"; then
  sed -i '' "1a\\
BUDGET_S=$BUDGET_S
" "$TMP" 2>/dev/null || true
fi
chmod +x "$TMP"
echo "[s657] harness from $SRC budget=$BUDGET_S"
zsh "$TMP"
RC=$?
rm -f "$TMP"
exit $RC
