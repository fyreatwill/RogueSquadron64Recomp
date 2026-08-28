# NEXT work unit (s2948) — route-prepare rejection cause at VI 640

HYPOTHESIS-ID: m5-route-qualification-repair

## Context (what ran in s2946/s2947)

s2946 probed the oracle-qualified candidate `0x80019CD8` in the port with a
regeneration-owned fixture in `tools/fixup_game_funcs.py`. The `[f5-fetch-control]`
positive control fired 8 times (phases 2 and 4, 4 rows each). The candidate hook
fired 0 times. The route stopped at pre-title VI 640 (`0x0066A500`) and never
reached title 1024 or hangar 512.

**s2946 result:** H-RoutePreTitle SELECTED, H-RouteReachesTarget REFUTED for this
recipe. H-RouteState/H-RouteInput are unevaluable until title/hangar is reached.

**s2947** is a checkpoint close-out only — no new experiment. The NEXT is the first
genuine new probe.

## What is unknown

s2905 showed `key_match=1` / `accepted=0` at pre-title VI 640.
s2882 showed `route_valid=0` in all stage-call rows at the same phase.

The route-prepare receives a matching key but is rejected. The specific failing field
(the first route-prepare input that differs from an accepted retail value) is
unknown.

## Competing hypotheses

- H-PrepareFieldBad: one specific input field to the route-prepare is wrong (e.g.
  a counter, overlay ID, or state word is 0 or uninitialized in the port).
- H-PrepareTimingBad: the route-prepare is called in the right key state but a
  time-relative condition (frame counter, prior phase) is wrong.
- H-PrepareLogicBad: the generated route-prepare logic itself is incorrect (a
  fixup-script or N64Recomp translation bug at the prepare site).

## Discriminator

One batched build/run that logs all route-prepare inputs and the rejection flag at
VI 640. Target table: `[route-prep]` rows with phase, key, accepted, and ALL
input fields side-by-side. Compare the accepted=0 port row against the oracle's
s2945 table to identify the first differing field.

No oracle re-run needed — s2945 already ground-truthed `0x80019CD8` state at title
and hangar. No behavior change until the writer is named and shown legitimate.

## Exact work

1. Read `tools/fixup_game_funcs.py` to find the existing `0x80019CD8` candidate
   probe added in s2946.
2. Extend the probe (or add a new one at the route-prepare call site) to log ALL
   input registers and the rejection condition in one `fprintf` line.
3. Build: `N64Recomp/build/N64Recomp rogue_squadron64.elf config.toml &&
   python3 tools/fixup_game_funcs.py && DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
4. Run from `build/` with: `ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1
   ROGUESQ_AUTOPILOT=1 PROBE_PHASE_WIDTH=1024 PROBE_PHASE_TIMEOUT=180
   ROGUESQ_LOG_F5_STATE=1 ./RogueSquadron64Recomp ../rogue_squadron64.z64`
5. Capture to `scratch/agent/s2948_route_prepare_rejection/`.
6. Report the `[route-prep]` rows and identify which input field is zero/wrong.

Outcome table:
- All input fields match retail → H-PrepareLogicBad (check generated code)
- One input field differs → H-PrepareFieldBad SELECTED (name the field)
- Time-relative field differs → H-PrepareTimingBad SELECTED
- No `[route-prep]` rows (probe misfired) → instrument gap, add [f5-fetch-control] in same run
