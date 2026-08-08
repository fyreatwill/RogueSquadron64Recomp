#!/bin/zsh
# s490 2nd independent confirm of item -317's HEAP_DEQUEUE_DERIVED_PTR_GUARD.
#
# Context: item -317 fixed an unguarded derived-pointer write in
# heapFreeListDequeue (funcs_3.c, site=0x8000D760, "$s0 = $a0+8" then
# MEM_W(0x8, $s0)=...). A FIRST fix attempt this session validated the wrong
# register (ctx->r4, a base register with path-dependent meaning at this
# shared-label site) and false-positived at ~2200/sec (660261 fires, all 4
# related sibling guards at 0) -- caught before commit, reverted, corrected to
# validate ctx->r16 (the pointer actually dereferenced) directly, which is
# correct regardless of which of the two known control-flow paths reaches this
# site. 1st live-verify of the CORRECTED guard (this session, manual): 0 fires
# on the new guard, hangarbay-entry n=31 (positive control), 1 fire on the
# unrelated sibling compose-npc-orient-guard9 (pre-existing family, not this
# fix), crashed on the already-catalogued loadCutsceneAssetsByIndex+1860 /
# last-guest-pc=0x800aafb8 family (same crash s463's own confirm soak hit).
# Same PROBE_KEYS schedule and full sibling-guard env-var set as every prior
# soak in this lineage, plus ROGUESQ_LOG_HEAP_DEQUEUE_DERIVED_PTR_GUARD
# ([heap-dequeue-derived-ptr-guard]).
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
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s490_heap_dequeue_derived_ptr_confirm" 300 2
