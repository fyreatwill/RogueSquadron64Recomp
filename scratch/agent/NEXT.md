# NEXT work unit (s2010) — obtain phase-valid generated-tree provenance

HYPOTHESIS-ID: m5-status3-worker-dispatch

## Status at session start

s2009 force-rebuilt the preserved 45-file snapshot and ran the existing
phase-gated control. It published VI 0, 320, and 640, with ongoing VI-enqueue
rows, but never reached VI 1024. The status census remains unevaluable. The
watchdog failed to enforce its nominal timeout; the game was scoped and
SIGKILLed after the VI-640 stall. The phase-valid s2007 generated artifact is
not currently identified in the workspace.

## Competing hypotheses

- **H-current-symbols:** the companion repository's pending symbol-file edits
  changed the generated layout or dispatch registration; the fresh 51-file
  tree is not behaviorally equivalent to the s2007 tree.
- **H-snapshot-stale:** the 45-file snapshot is too old for the current
  runtime/CMake sources, so its VI-640 stall is not a valid status result.
- **H-overlay-pairing:** `recomp_overlays.inl`, `funcs.h`, `lookup.cpp`, and
  the generated C files are from different generations even when the file
  count matches, causing the phase stall.
- **H-build-staleness:** an object or CMake source-list mismatch, rather than
  either generated tree, caused the phase failure. The forced 45-file rebuild
  makes this less likely but does not prove provenance.

## Discriminating measurement

After the human provides the phase-valid s2007 tree or authorizes symbol
reconciliation, build one internally matched generated/overlay artifact after
recording source revisions and forcing every generated object to compile. The
same phase-gated recipe must reach VI 1024 and retain the s2006/s2007 controls.
A clean VI-1024 transition selects a phase-valid baseline; another pre-1024
crash or VI-640 stall keeps the status census blocked; a link failure selects
overlay/header pairing or stale CMake inputs. Do not interpret any
status-writer null until VI 1024 passes.

## Exact commands

```sh
git -C /Users/williambuckley/Documents/Tools/rogue_squadron64 status --short -- symbol_files
git -C /Users/williambuckley/Documents/Tools/N64Recomp status --short -- fixup_game_funcs.py RecompiledFuncs
git -C /Users/williambuckley/Documents/Tools/N64Recomp log -5 --oneline -- fixup_game_funcs.py
rg --files /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -g 'funcs_*.c' | wc -l
rg -n 'section_table|overlay_sections_by_index|slotDispatcherIter' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h src/main/register_overlays.cpp
cmake -S . -B build
find /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -maxdepth 1 -type f -name 'funcs_*.c' -exec touch {} +
cmake --build build --config Debug --target RogueSquadron64Recomp
env PROBES_OVERRIDE="p1:start:5 p2:a:3" ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_THREADS=1 ROGUESQ_LOG_RUNNER_ALL=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_SCHED=1 ROGUESQ_LOG_THREAD_RESUME=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2010-provenance 0 12 > scratch/agent/s2010-provenance.log 2>&1
```

The run must be SIGKILLed, and the required positive control is VI 1024 before
any status-table conclusion. If no internally matched artifact can reach VI
1024, stop and ask for the phase-valid s2007 generated tree or permission to
reconcile the companion symbol snapshot; do not alter status, audio, spin, or
PI behavior.
