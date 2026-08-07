#!/bin/zsh
# s460: confirmation soak for item -292's next slice, `advanceSongRegion`
# (12 sites, SONGTEMPO_TABLE_GUARD family, 0x29C0($reg) -> global 0x801529C0).
# 31/43 total item -292 sites now guarded (19 from s454/s457/s458 +
# advanceSongRegion's 12 this session); only stepActiveSongTracks (12 sites)
# remains. Per-site bail semantics derived by reading the whole function body
# (nested outer-channel-loop/inner-list-walk structure) -- see
# docs/CURRENT-TRUTH.md item -292 / PORTING-STATE.md Session 460 for the full
# per-site derivation. Manual live-verify (this session, s460): 0 [CRASH]
# attributable to the guard, 0 songtempo-table-guard fires, hangarbay-entry
# reached n=2800. The run DID crash late in the schedule but on the
# already-catalogued coalesceFreeHeapBlocks+4424/last-guest-pc=0x8000247c
# background-noise signature (documented since the s354-366 arc) -- no
# funcs_25.c frame in the backtrace, unrelated to this session's patch.
#
# Arms ALL passive breadcrumb/instrument env vars per the standing soak-queue
# rule (never rotate one per soak) -- same list as s459's own recipe.
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
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s460_advancesongregion_confirm_$$" 300 2

RUNLOG="$REPO_ROOT/scratch/agent/soak_results/s460_advancesongregion_confirm_$$/run.log"
if [ ! -f "$RUNLOG" ]; then
  echo "s460_advancesongregion_confirm: no run.log produced -- treat as fail"
  exit 1
fi

if grep -q '\[CRASH\]' "$RUNLOG"; then
  echo "s460_advancesongregion_confirm: CRASHED -- $(grep 'last-guest-pc' "$RUNLOG" | tail -1) -- $RUNLOG"
  exit 1
fi

FIRES=$(grep -c 'songtempo-table-guard' "$RUNLOG" || true)
echo "s460_advancesongregion_confirm: OK, 0 crash, songtempo-table-guard fires=$FIRES -- $RUNLOG"
exit 0
