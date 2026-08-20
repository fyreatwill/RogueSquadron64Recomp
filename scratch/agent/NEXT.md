# NEXT work unit (s2012) — obtain phase-valid generated-tree provenance

HYPOTHESIS-ID: m5-status3-worker-dispatch

## Work unit

M5 phase-valid generated-tree provenance repair. This is the only next unit;
do not run the status-writer census until its VI-1024 positive control passes.
Human input is required: provide the phase-valid s2007 generated tree, or
explicitly authorize reconciling the four pending companion symbol files.
The s2011 read-only check found only the 45-file current tree, uncommitted
companion/symbol edits, and a provenance retry that died before VI 1024. Do
not build or reconcile until that input is supplied.

## Competing hypotheses and discriminator

- **H-current-symbols:** pending companion symbol edits changed generated
  layout/dispatch, so the current 51-file tree is not behaviorally equivalent
  to s2007.
- **H-snapshot-stale:** the preserved 45-file tree is too old for the current
  runtime/CMake sources and its VI-640 stall is not a valid status result.
- **H-overlay-pairing:** `recomp_overlays.inl`, `funcs.h`, `lookup.cpp`, and
  generated C files are from different generations even when file count
  matches.
- **H-build-staleness:** an object or source-list mismatch caused the phase
  failure; a forced full rebuild should remove it.

The discriminating measurement is one internally matched generated/overlay
artifact with every generated object forced to compile. VI 1024 plus the
s2006/s2007 controls selects a phase-valid baseline. A pre-1024 crash or a
VI-640 live stall keeps the status census blocked. A link/source mismatch
selects overlay pairing or stale CMake inputs. Do not interpret a status-writer
null without VI 1024 in the same run.

## Exact commands after the required human input

```sh
git -C /Users/williambuckley/Documents/Tools/rogue_squadron64 status --short -- symbol_files
git -C /Users/williambuckley/Documents/Tools/N64Recomp status --short -- fixup_game_funcs.py RecompiledFuncs
git -C /Users/williambuckley/Documents/Tools/N64Recomp log -5 --oneline -- fixup_game_funcs.py
rg --files /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -g 'funcs_*.c' | wc -l
rg -n 'section_table|overlay_sections_by_index|slotDispatcherIter' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/recomp_overlays.inl /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h src/main/register_overlays.cpp
cmake -S . -B build
find /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs -maxdepth 1 -type f -name 'funcs_*.c' -exec touch {} +
cmake --build build --config Debug --target RogueSquadron64Recomp
env PROBES_OVERRIDE="p1:start:5 p2:a:3" ROGUESQ_SPIN_YIELD=1 ROGUESQ_LOG_ALL=1 ROGUESQ_LOG_THREADS=1 ROGUESQ_LOG_RUNNER_ALL=1 ROGUESQ_LOG_SPBOOT=1 ROGUESQ_LOG_SCHED=1 ROGUESQ_LOG_THREAD_RESUME=1 ROGUESQ_LOG_AUDIOTICK_TRACE=1 zsh scratch/s73_post_a_scene/run_mission_keys.sh s2011-provenance 0 12 > scratch/agent/s2011-provenance.log 2>&1
```

The run must be scoped and SIGKILLed. Positive control is VI 1024; VI-enqueue
rows alone are insufficient. If no internally matched artifact reaches VI
1024, stop and request the phase-valid s2007 tree or permission to reconcile
the companion symbol snapshot. Do not alter status, audio, spin, or PI
behavior in that case.
