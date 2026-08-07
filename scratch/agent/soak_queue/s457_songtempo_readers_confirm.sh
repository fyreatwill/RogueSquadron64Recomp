#!/bin/zsh
# s457: confirmation soak for item -292's next slice of SONGTEMPO_TABLE_GUARD --
# `tickScheduledSongEvents` (5 sites) and `stepSongPitchBendLanes` (5 sites),
# funcs_25.c. Same family/env var as s454's `updateSongTempoTickRate` (4
# sites, already closed) and the same `0x29C0($reg)` -> global `0x801529C0`
# idiom (MusyX song-sequencer current-track pointer, reload-then-deref with no
# range check, same shape as the closed `-0x25A4` family).
#
# tickScheduledSongEvents (funcs_25.c:2657-2856): walks a singly-linked list
# of scheduled song events. Site tse1's load happens before the stack
# prologue runs -- bare `return;` (stack-neutral). Sites tse2-tse5 (one per
# list node, at the loop head and three more inside the per-node list-splice
# bookkeeping) all bail via `goto L_80094EC0`, the loop's own
# advance-to-next-node point -- abandon this node's processing, keep walking
# the list, matching the function's own semantics rather than aborting the
# whole tick pass.
#
# stepSongPitchBendLanes (funcs_25.c:2857-3135): a per-lane outer loop
# wrapping a per-event inner loop. Site spbl1 (outer-loop head) reuses the
# game's OWN existing null-lane-skip idiom (`s2 += 0x24; goto L_80095068`) as
# its bail -- the source already treats a null per-lane pointer that way two
# instructions later. Sites spbl2-spbl5 (inside the inner loop's per-event
# processing for that same lane) reuse the identical "abandon this lane,
# advance to the next" bail, since all four feed the same per-lane bookkeeping
# the outer loop already tears down that way on its own exit path.
#
# Fixup report: `funcs_25.c: tickScheduledSongEvents SONGTEMPO_TABLE_GUARD
# patched x5 (of 5 sites)` + `funcs_25.c: stepSongPitchBendLanes
# SONGTEMPO_TABLE_GUARD patched x5 (of 5 sites)`. Direct grep confirmed 14/14
# total songtempo-table-guard sites in funcs_25.c (4 existing + 10 new).
# `strings` on the built binary confirmed all 14 distinct guard format
# strings. Full regen/build clean (0 errors, only pre-existing benign
# warnings). Manual live-verify (this session, s457): see
# docs/CURRENT-TRUTH.md item -294 / PORTING-STATE.md Session 457 for the
# result this recipe is confirming.
#
# NOT fixed, still queued: `stepSongModulationLanes` (5 sites),
# `advanceSongRegion` (12 sites), `stepActiveSongTracks` (12 sites) -- the
# latter two are unusually large and flagged for a possible cross-function
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
    zsh "$REPO_ROOT/tools/probe.sh" "$REPO_ROOT/scratch/agent/soak_results/s457_songtempo_readers_confirm_$$" 300 2

RUNLOG="$REPO_ROOT/scratch/agent/soak_results/s457_songtempo_readers_confirm_$$/run.log"
if [ ! -f "$RUNLOG" ]; then
  echo "s457_songtempo_readers_confirm: no run.log produced -- treat as fail"
  exit 1
fi

if grep -q '\[CRASH\]' "$RUNLOG"; then
  echo "s457_songtempo_readers_confirm: CRASHED -- $(grep 'last-guest-pc' "$RUNLOG" | tail -1) -- $RUNLOG"
  exit 1
fi

FIRES=$(grep -c 'songtempo-table-guard' "$RUNLOG" || true)
echo "s457_songtempo_readers_confirm: OK, 0 crash, songtempo-table-guard fires=$FIRES -- $RUNLOG"
exit 0
