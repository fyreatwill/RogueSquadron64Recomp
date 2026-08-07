#!/bin/zsh
# s458: confirmation soak for item -292's next slice of SONGTEMPO_TABLE_GUARD --
# `stepSongModulationLanes` (5 sites), funcs_25.c. Same family/env var as
# s454/s457's already-closed slices (updateSongTempoTickRate 4,
# tickScheduledSongEvents 5, stepSongPitchBendLanes 5) and the same
# `0x29C0($reg)` -> global `0x801529C0` idiom (MusyX song-sequencer
# current-track pointer, reload-then-deref with no range check, same shape as
# the closed `-0x25A4` family). 19/43 total sites of item -292 now fixed.
#
# stepSongModulationLanes (funcs_25.c ~3291-3573, N64Recomp/RecompiledFuncs
# copy): an outer per-lane loop ($s2/r18, stride 0x24, bound 0x900, head
# L_800950A8, bound-check/advance target L_8009521C) wrapping an inner
# per-event loop ($s0/r16 constant per lane, head L_800950C8, exit test
# L_80095210) -- exactly the stepSongPitchBendLanes shape. Site smod1
# (outer-loop head) reuses the game's OWN existing null-lane-skip idiom
# (`s2 += 0x24; goto L_8009521C`) as its bail. Sites smod2-smod5 (inside the
# inner loop's per-event processing for that same lane) reuse the identical
# "abandon this lane, advance to the next" bail, matching
# stepSongPitchBendLanes's own spbl2-spbl5 convention exactly.
#
# Fixup report: `funcs_25.c: stepSongModulationLanes SONGTEMPO_TABLE_GUARD
# patched x5 (of 5 sites)`. Direct grep confirmed 19/19 total songtempo-table-
# guard sites in funcs_25.c (14 existing + 5 new, x2 mentions/site = 38).
# `strings` on the built binary confirmed all 19 distinct guard format
# strings. Full regen/build clean (0 errors, only pre-existing benign
# warnings). Manual live-verify (this session, s458): 0 [CRASH], 0
# songtempo-table-guard fires, 0 dl-list-append-guard fires, hangarbay-entry
# reached n=2600 (full 300s schedule completed) -- see docs/CURRENT-TRUTH.md
# item -295 / PORTING-STATE.md Session 458 for full detail.
#
# NOT fixed, still queued: `advanceSongRegion` (12 sites), `stepActiveSongTracks`
# (12 sites) -- both unusually large and flagged for a possible cross-function
# shared-tail-merge complication, per-site individual verification needed.
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
    ROGUESQ_LOG_SONGTEMPO_TABLE_GUARD=1 ROGUESQ_LOG_DL_LIST_APPEND_GUARD=1 \
    PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180 PROBE_KEYS_FROM_PHASE=1 PROBE_LEAVE_OK=1 \
    PROBE_KEYS="3:start 7:start 11:start 15:a 100:start 130:start 160:a 190:start 220:a 250:start" \
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s458_songtempo_smod_confirm_$$" 300 2

RUNLOG="$REPO_ROOT/scratch/agent/soak_results/s458_songtempo_smod_confirm_$$/run.log"
if [ ! -f "$RUNLOG" ]; then
  echo "s458_songtempo_smod_confirm: no run.log produced -- treat as fail"
  exit 1
fi

if grep -q '\[CRASH\]' "$RUNLOG"; then
  echo "s458_songtempo_smod_confirm: CRASHED -- $(grep 'last-guest-pc' "$RUNLOG" | tail -1) -- $RUNLOG"
  exit 1
fi

FIRES=$(grep -c 'songtempo-table-guard' "$RUNLOG" || true)
echo "s458_songtempo_smod_confirm: OK, 0 crash, songtempo-table-guard fires=$FIRES -- $RUNLOG"
exit 0
