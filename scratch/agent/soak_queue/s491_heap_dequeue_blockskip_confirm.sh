#!/bin/zsh
# s491 2nd independent confirm of item -317's EXTENDED HEAP_DEQUEUE_DERIVED_PTR_GUARD.
#
# Context: s490 fixed the FIRST unguarded derived-pointer write in
# heapFreeListDequeue (funcs_3.c, site=0x8000D760) but left 9+ more unguarded
# ctx->r16 derefs plus a second-generation ctx->r5=ADD32(ctx->r16,0x10)
# pointer exposed later in the same straight-line block (a post-session
# classification pass found these; see docs/CURRENT-TRUTH.md item -317).
# s491 direct-traced the whole span (guest 0x8000D75C-0x8000D8A8): a SINGLE
# straight-line block with exactly one external entry point (the L_8000D75C
# label, reached by the two paths s490 already characterized) and no other
# goto-in hazard. Extended the existing check to `goto L_8000D8A8` (skip the
# ENTIRE rest of the block, an existing label, itself pure arithmetic) instead
# of only skipping its own write -- same goto-skip shape as the s487
# AUDIO_VOICE_BASEPTR_LOOP_GUARD precedent. 1st live-verify (this session,
# manual): 0 fires on the guard, 0 fires on any of ~20 sibling guard families,
# hangarbay-entry n=31 (positive control), crashed on the already-catalogued
# BREADCRUMB6/buildPositionAndCallTransformHelper near-zero-guest-pointer
# family (si_addr=0x380000010, last-guest-pc=0x80065acc -- same exact crash as
# s451's own confirm soak hit), unrelated to this guard or any guard tested.
# Same PROBE_KEYS schedule and full sibling-guard env-var set as every prior
# soak in this lineage.
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
    ROGUESQ_LOG_DL_LIST_RESET_GUARD=1 ROGUESQ_LOG_DL_BUFFER_POOL_GUARD=1 \
    ROGUESQ_LOG_NODE_LIST_HEAD_GUARD=1 ROGUESQ_LOG_NODE_LIST_HEAD_WRITE_GUARD=1 \
    ROGUESQ_LOG_TEXDATA_TABLE_GUARD=1 ROGUESQ_LOG_TEXDATA_PTR_ARRAY_GUARD=1 ROGUESQ_LOG_MATERIAL_ARRAY_PTR_GUARD=1 \
    ROGUESQ_LOG_DL_LIST_APPEND_RWRITE_GUARD=1 \
    ROGUESQ_LOG_AUDIO_SLOT_ACTIVE_GUARD=1 ROGUESQ_LOG_AUDIO_VOICE_BASEPTR_GUARD=1 \
    ROGUESQ_LOG_AUDIO_VOICE_BASEPTR_LOOP_GUARD=1 \
    ROGUESQ_LOG_S315_RESET_R4_GUARD=1 ROGUESQ_LOG_DL_LIST_RESET_RNODE_GUARD=1 \
    ROGUESQ_LOG_DL_ALLOC_PROPAGATION_GUARD=1 ROGUESQ_LOG_HEAP_DEQUEUE_DERIVED_PTR_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s491_heap_dequeue_blockskip_confirm" 300 2
