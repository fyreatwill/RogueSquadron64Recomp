#!/bin/zsh
# s459: confirmation soak for the fresh SIBLING_PTR_WRITE_GUARD idiom-class
# audit (-0x23A8 -> global 0x8011DC58, the sibling s454 explicitly scoped OUT
# of DL_LIST_APPEND_GUARD as "no clean byte-identical shape found"). A fresh
# systematic re-scan found 118/119 sites DO share one shape after all
# (`MEM_W(OFF, ctx->rN) = VAL;`, an unconditional field write through a
# never-range-checked reloaded pointer, OFF in {0x0 x116, 0x4 x1, 0x8 x2}) --
# same risk class as DL_LIST_APPEND_GUARD/FREELIST_NEXT_GUARD. All 119 sites
# patched via individual literal-anchor patches (funcs_3.c x65, funcs_4.c
# x54), same remediation precedent ("skip the write, nothing downstream
# depends on it happening"). Full regen/build clean (0 errors, only
# pre-existing benign warnings), `strings` confirmed 119/119 distinct guard
# format strings. Manual live-verify (this session, s459): 0 [CRASH], 0
# sibling-ptr-write-guard fires -- see docs/CURRENT-TRUTH.md item -296 /
# PORTING-STATE.md Session 459 for full detail.
#
# Notable: this idiom touches submitSceneNodeRender (10 sites) -- the SAME
# function named in items -293/-294's still-open "wait-for-recurrence
# breadcrumb" (2 independent single-occurrence crashes in its call subtree,
# s456/s457). This guard is a discriminating instrument for that breadcrumb:
# watch for fires here specifically, not just the aggregate count.
#
# Arms ALL passive breadcrumb/instrument env vars per the standing soak-queue
# rule (never rotate one per soak).
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
    ROGUESQ_LOG_SONGTEMPO_TABLE_GUARD=1 ROGUESQ_LOG_DL_LIST_APPEND_GUARD=1 ROGUESQ_LOG_SIBLING_PTR_WRITE_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s459_sibling_ptr_write_confirm_$$" 300 2

RUNLOG="$REPO_ROOT/scratch/agent/soak_results/s459_sibling_ptr_write_confirm_$$/run.log"
if [ ! -f "$RUNLOG" ]; then
  echo "s459_sibling_ptr_write_confirm: no run.log produced -- treat as fail"
  exit 1
fi

if grep -q '\[CRASH\]' "$RUNLOG"; then
  echo "s459_sibling_ptr_write_confirm: CRASHED -- $(grep 'last-guest-pc' "$RUNLOG" | tail -1) -- $RUNLOG"
  exit 1
fi

FIRES=$(grep -c 'sibling-ptr-write-guard' "$RUNLOG" || true)
echo "s459_sibling_ptr_write_confirm: OK, 0 crash, sibling-ptr-write-guard fires=$FIRES -- $RUNLOG"
exit 0
