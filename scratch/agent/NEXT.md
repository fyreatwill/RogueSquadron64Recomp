# NEXT work unit — cinematicStageAdvancer $v0 producer table

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Resume context

Port Session 3307 selected `H-PortLoopNoExit`: first attract
`cinematicLoopBody` skips early-exit (`0x800A5DD8` `$v0=1`), reaches
loop-head `0x800A6024` and backedge `0x800A64B4` (printed n=150 at
VI `#640`), and keeps exit-gate `0x800A6074` at `$v0=0` (`v0_nz=0`)
through a 121 s run. Silent: `0x800A64BC`, `0x800A65E4`,
`0x800A6618`, title 1024. Retail Session 3306 took `$v0=1` at 48.8 s
after 1002 gate visits. Architecture: the gate `$v0` is
`cinematicStageAdvancer` (`0x800AF550`) after `andi 0xFF`.

A 600 s soak is queued (`scratch/agent/soak_queue/s3307_cine_loop_600s.sh`)
to test whether a longer wall clock ever sets the gate. Do not babysit
it; fold the verdict if present.

## Competing hypotheses

- `H-PtrZeroSkip`: `0x800AF55C` sees `$v1==0` (word at `0x800B0934`)
  and takes `L_800AF604`; the stage/dt path never runs.
- `H-DtBelowThreshold`: the `c.lt.s` at `0x800AF588` (`0x800A5D70`
  vs dt-scaled accumulator) stays false; stage byte `0x800B0938`
  never increments.
- `H-StageNeverHits7`: stage byte increments but `sltiu 0x7` at
  `0x800AF5B0` stays true (`$v0=1` continue); exit `$v0` never
  published.
- `H-CoverageInvalid`: missing mark-all, viewer-return, VI-640,
  cinematic-entry, loop-head, or gate row.

## Discriminator

One regeneration-safe table of `cinematicStageAdvancer` entry,
`0x800AF55C` (`$v1`), `0x800AF590` (fp compare taken),
`0x800AF5B4` (stage<7), and the `$v0` stored into the 6074 gate,
in one build and one ≥120 s run. Log the `0x800B0934` pointer,
`0x800B0938` stage byte, and IEEE bits of `$f0`/`$f2`. Phase-reset
the print budget on VI width changes. Arm a synthetic mark for
every new edge ID. Keep the s3306 loop table.

Ptr-zero rows with silent compare/stage select `H-PtrZeroSkip`.
Compare never-taken with frozen stage byte selects
`H-DtBelowThreshold`. Stage increments and stays `<7` selects
`H-StageNeverHits7`. Missing controls select `H-CoverageInvalid`.

## Exact commands

1. Add `tools/apply_s3307_stage_advancer.py` injecting probes at
   those PCs in `funcs_29.c`. Mirror the transform into
   `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`.
   Reuse `ROGUESQ_LOG_M5_CINE_LOOP` or sibling
   `ROGUESQ_LOG_M5_STAGE_ADV=1`. Do not change guest stores/branches.
2. Build:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run from `build/` with the ROM present, SIGKILL at 120 s, env:
   `ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_M5_POSTVIEWER_EDGE=1 ROGUESQ_M5_POSTVIEWER_MARK_ALL=1 ROGUESQ_LOG_M5_CINE_LOOP=1 ROGUESQ_M5_CINE_LOOP_MARK_ALL=1`
   plus the new mark-all. Require viewer return, VI 640 at
   `0x0066A500`, cinematic entry, loop-head, exit-gate, and every
   new mark ID. If the first launch crashes at VI 320 in
   `spTaskSchedulerThread`, retry the same binary once (s3307).

No M5 Step 3. No audio/output change.
