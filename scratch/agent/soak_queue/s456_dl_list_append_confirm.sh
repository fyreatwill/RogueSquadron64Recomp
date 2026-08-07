#!/bin/zsh
# s456: confirmation soak for the DL_LIST_APPEND_GUARD family (57 sites,
# funcs_3.c x26 + funcs_4.c x31) -- item -291's already-designed guard,
# executed this session (s456).
#
# The `-0x5824` global (address 0x8011A7DC, `lui $reg, 0x8012; lw $reg,
# -0x5824($reg)`, reloaded fresh at every use site) is a doubly-linked-list
# head pointer in the display-list emission code (funcs_3.c/funcs_4.c) --
# same "reload a global pointer, then dereference without a range check"
# shape as the closed -0x25A4 family and the sibling 0x801163B0 free-list-
# cache-head family (GENERIC_CACHE_GUARD/CACHE_HEAD_A1_GUARD/
# FREELIST_NEXT_GUARD), but a DIFFERENT global and idiom (unconditional
# append, no existing empty-list check anywhere in this idiom). Unlike the
# "substitute 0" GENERIC_CACHE_GUARD trick, this guard skips the whole
# 4-instruction append tail on an invalid reload -- silent no-op instead of
# a SIGSEGV/SIGBUS, matching the FREELIST_NEXT_GUARD/CACHE_HEAD_A1_GUARD
# precedent. Full detail: fixup_game_funcs.py (N64Recomp repo) comment above
# the DL_LIST_APPEND_GUARD regex, docs/CURRENT-TRUTH.md item -293.
#
# 57/57 sites patched (26 funcs_3.c + 31 funcs_4.c, matches the pre-counted
# expectation exactly). Regen/build clean, strings confirmed 57 distinct
# guard format strings in the binary.
#
# Arms ALL passive breadcrumb/instrument env vars per the standing soak-queue
# rule (never rotate one per soak) -- including this family's own new tag
# (ROGUESQ_LOG_DL_LIST_APPEND_GUARD).
set -e
cd "$(dirname "$0")/../../.."
REPO_ROOT="$(pwd)"
cd "$REPO_ROOT/build"

env ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 \
    ROGUESQ_LLE_SOLO=1 ROGUESQ_STUB_MISSING_FUNCS=1 \
    ROGUESQ_LOG_RUNNER=1 ROGUESQ_LOG_GENERIC_CACHE_GUARD=1 ROGUESQ_LOG_CACHE_HEAD_A1_GUARD=1 \
    ROGUESQ_LOG_FREELIST_NEXT_GUARD=1 ROGUESQ_LOG_HANGARBAY_ENTRY=1 ROGUESQ_LOG_GETDATITEM_GUARD=1 \
    ROGUESQ_LOG_GETDATITEM_REACHED=1 ROGUESQ_LOG_HANGARLIST_REACHED=1 \
    ROGUESQ_LOG_HANGARLIST_GUARD=1 ROGUESQ_LOG_HANGARLIST_GUARD_EARLY=1 \
    ROGUESQ_LOG_HANGARLIST_GUARD_WALK=1 ROGUESQ_LOG_HANGARLIST_GUARD_CLEAR=1 \
    ROGUESQ_LOG_S284_GUARD=1 ROGUESQ_LOG_S285_GUARD=1 ROGUESQ_LOG_S390_H2_GUARD=1 \
    ROGUESQ_LOG_ANIM_TEX_STREAM=1 ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD=1 ROGUESQ_LOG_ANIM_TEX_STREAM_GUARD2=1 \
    ROGUESQ_LOG_HANGAR_BAY_DEREF_GUARD=1 ROGUESQ_LOG_HANGAR_BAY_SCENE_GUARD=1 \
    ROGUESQ_LOG_COMPOSE_NPC_GUARD=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD2=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD3=1 \
    ROGUESQ_LOG_COMPOSE_NPC_GUARD4=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD5=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD6=1 \
    ROGUESQ_LOG_COMPOSE_NPC_GUARD7=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD8=1 ROGUESQ_LOG_COMPOSE_NPC_GUARD9=1 \
    ROGUESQ_LOG_SONGTEMPO_TABLE_GUARD=1 ROGUESQ_LOG_DL_LIST_APPEND_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s456_dl_list_append_confirm_$$" 300 2

RUNLOG="$REPO_ROOT/scratch/agent/soak_results/s456_dl_list_append_confirm_$$/run.log"
if [ ! -f "$RUNLOG" ]; then
  echo "s456_dl_list_append_confirm: no run.log produced -- treat as fail"
  exit 1
fi

if grep -q '\[CRASH\]' "$RUNLOG"; then
  echo "s456_dl_list_append_confirm: CRASHED -- $(grep 'last-guest-pc' "$RUNLOG" | tail -1) -- $RUNLOG"
  exit 1
fi

FIRES=$(grep -c 'dl-list-append-guard' "$RUNLOG" || true)
echo "s456_dl_list_append_confirm: OK, 0 crash, dl-list-append-guard fires=$FIRES -- $RUNLOG"
exit 0
