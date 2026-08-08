#!/bin/zsh
# s492 2nd independent confirm of item -317 step 2's new ORIENTED_FACE_DERIVED_PTR_GUARD.
#
# Context: s491 closed item -317's own heapFreeListDequeue (funcs_3.c)
# remainder and deferred its funcs_4.c sibling (buildOrientedFaceGeometry,
# guest 0x80012E94->0x80012EF0->0x80012F14) pending a dedicated provenance
# trace, per NEXT.md's explicit instruction not to reuse the fix shape
# blindly. s492 did that trace: ctx->r4 is reloaded UNGUARDED from the same
# free-list-cache-head global (0x801163B0) at 0x80012E94, survives untouched
# through four existing sibling guards that read a DIFFERENT register (ctx->r2
# or ctx->r3, never r4) at that point, then gets ADD32'd into ctx->r18 at
# 0x80012EF0 and dereferenced unguarded across an 8-field struct-init block
# (0x80012F14-0x80012F94). The complication flagged by s491 (a second `goto
# L_80012F08` path at guest 0x80012E24 carrying a different-provenance
# ctx->r18) resolved cleanly: `grep -c "goto L_80012F08"` found exactly ONE
# goto into the label plus the natural fallthrough -- a clean 2-entry join --
# so the check validates ctx->r18 itself (the register actually dereferenced,
# not the upstream ctx->r4 proxy) right at the join, before the first deref,
# block-skipping to the existing epilogue label L_80012F98 (pure register
# restore + return, no deref) on invalid. 1st live-verify (this session,
# manual): 0 fires on the new guard, hangarbay-entry n=31 (positive control),
# only 1 fire total on any OTHER guard family (hangar-bay-deref-guard,
# n=0/ra=0x0, printed in the same instant as the crash dump -- an artifact of
# the process already dying, not evidence of a real hazard), crashed on the
# already-catalogued initVec4TripletFromArgs+68/last-guest-pc=0x800ab068
# family (x0/x9=0x0000000300000000 RDRAM-base signature, byte-identical to
# s489/s463/s468's own confirm soaks), unrelated to this guard or any guard
# tested. Same PROBE_KEYS schedule and full sibling-guard env-var set as every
# prior soak in this lineage, plus ROGUESQ_LOG_ORIENTED_FACE_DERIVED_PTR_GUARD.
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
    ROGUESQ_LOG_ORIENTED_FACE_DERIVED_PTR_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s492_oriented_face_derived_ptr_confirm" 300 2
