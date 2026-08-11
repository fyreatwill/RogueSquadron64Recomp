#!/bin/zsh
# s656 freelist-survival residual A/B: ALLOW_WILD_W=1 + ALLOW_FL_HDR=1 re-opens
# freelist writeback stomp (both product guards off).
#
# s656 Outcome B: H-skip-suppresses-recov REFUTED for SKIP_WILD_W alone —
# 0/6 recovery-active engaged under ALLOW_WILD_W (SKIP_FL_HDR still blocked
# killer CIMG; freelist 0x2/0x60 survived). Drought independent of SKIP_WILD_W.
#
# Residual H-fl-survive-suppresses-recov (ACTIVE):
#   A) ≥1 recov768 in ≤6 engaged with both allows → freelist survival was
#      co-factor of drought; expect freelist to_zero 0x2/0x60 may return
#   B) 0 recov over ≥5 engaged with freelist to_zero LIVE → drought independent
#      of freelist state; pure recovery-inject pivot (why 0x76B768 never fires)
# Posctrl: "[ost-wb] ALLOW_WILD_W=1" AND "[ost-wb] ALLOW_FL_HDR=1" must fire;
#   skip_wild=0 skip_fl=0; fb_hit may return on killer.
# Passive: arm_fl, freelist to_zero, thr11d, fail136c, 1F0D74, recov768.
# HYPOTHESIS-ID: m3-post-exit-fs-stall
#
set -u
ROOT="/Users/williambuckley/Documents/Tools/RogueSquadron64Recomp"
cd "$ROOT" || exit 2
export DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer

# Prefer longer freeroll when possible; loop hard-caps at 600s so expect ~2-3
# engaged per soak — re-queue or in-session if sample size short.
BUDGET_S=1200
MAX_ATTEMPTS=12
HOLD_S=210
START_FLOOR_S=70
RECOV_WAIT_S=50
ENGAGE_WAIT_S=90
POLL_S=3

GAME_EXTRA_ENV_BASE="ROGUESQ_ALLOW_WILD_W=1 ROGUESQ_ALLOW_FL_HDR=1 ROGUESQ_LOG_FL_ZERO_WATCH=1 ROGUESQ_FORCE_STATE6_AFTER=40 ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1 ROGUESQ_LOG_RS_MALLOC_DIAG=1 ROGUESQ_LOG_DL_SYNC=1 ROGUESQ_LOG_FS_SLOT=1 ROGUESQ_LOG_RDP_FULLSYNC=1 ROGUESQ_LOG_AUDIO_DRAIN=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_COALESCE_HEAP_GUARD=1 ROGUESQ_LOG_COALESCE_HEAP_R2_GUARD=1 ROGUESQ_LOG_BEGINFRAME_S0_GUARD=1 ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 ROGUESQ_LOG_MAT3INV=1 ROGUESQ_LOG_SCENE_TRAVERSE=1"

# Reuse the s655 A/B freeroll harness body (identical scoring).
# Source the done recipe's harness by exec'ing a rewritten copy with our env.
# Inline: call the same fast-retry structure via the previous script after
# swapping GAME_EXTRA_ENV — simplest: copy-paste runner from s655 done script
# with our GAME_EXTRA_ENV_BASE above already set, then source shared body.

# Extract and run the harness from the done s655 script with env override by
# writing a temp wrapper that only changes GAME_EXTRA_ENV_BASE... instead just
# duplicate the essential loop by invoking the s655 script path after sed.

# Practical approach: run the s655 done script after exporting env that the
# script's GAME_EXTRA_ENV_BASE would override — so we cannot. Run a local
# clone of the loop with our env (heredoc script).

# Minimal: patch-env by re-execing a sed'd copy in /tmp
SRC="$ROOT/scratch/agent/soak_queue/done/s655_allow_wild_w_recov_ab_20260810-181017.sh"
if [ ! -f "$SRC" ]; then
  # fall back to any s655 allow wild done
  SRC=$(ls -t "$ROOT"/scratch/agent/soak_queue/done/s655_allow_wild_w_recov_ab*.sh 2>/dev/null | head -1)
fi
if [ -z "${SRC:-}" ] || [ ! -f "$SRC" ]; then
  echo "[s656] missing s655 harness template" >&2
  exit 2
fi
TMP=$(mktemp /tmp/s656_allow_fl_hdr_XXXXXX.sh)
# Replace GAME_EXTRA_ENV_BASE assignment and tag prefix
sed -e "s|^GAME_EXTRA_ENV_BASE=.*|GAME_EXTRA_ENV_BASE=\"$GAME_EXTRA_ENV_BASE\"|" \
    -e 's/s655_ab_/s656_flhdr_/g' \
    -e 's/tag=s655/tag=s656/g' \
    "$SRC" >"$TMP"
chmod +x "$TMP"
zsh "$TMP"
RC=$?
rm -f "$TMP"
exit $RC
