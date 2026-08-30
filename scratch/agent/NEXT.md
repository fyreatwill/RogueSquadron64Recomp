# NEXT work unit — port cinematic loop/exit edge table

HYPOTHESIS-ID: m5-osvimode-postviewer-continuation

## Resume context

Retail Session 3306 selected `H-RetailFiniteLoop`: first attract
`cinematicLoopBody` enters at 6.5 s (`prev_pc=0x8003E10C`, `$a0=0x13`),
skips early-exit (`0x800A5DD8` `$v0=1`), reaches loop-head `0x800A6024`
at 10.4 s, takes the `0x800A64B4` backedge 1002 times with exit-gate
`0x800A6074` `$v0=0`, then `$v0=1` at 48.8 s into `0x800A64BC`,
epilogue, `0x800A6618`, and caller `0x8003E114`. Port Session 3305
entered `0x800A5D80` and never reached `0x800A6618` in a ~120 s run.

## Competing hypotheses

- `H-PortPrologueStall`: entry fires; `0x800A5DD8` is `$v0=1` or
  silent; loop-head `0x800A6024` never runs.
- `H-PortLoopNoExit`: loop-head and backedge are live; `0x800A6074`
  stays `$v0=0`; `0x800A64BC` / `0x800A6618` stay silent through 120 s.
- `H-PortExitNoReturn`: `0x800A6074` `$v0=1` and `0x800A64BC` fire;
  `0x800A6618` / `0x8003E114` stay silent.
- `H-CoverageInvalid`: missing viewer-return, cinematic-entry, VI-640,
  SP-completion, or mark-all control; no null is interpretable.

## Discriminator

One regeneration-safe table covering all seven internal edges plus the
existing entry/return, in one build and one ≥120 s run. Phase-reset the
print budget on VI width changes. Arm a synthetic mark for every new
edge ID.

Entry + silent 6024 selects `H-PortPrologueStall`. 6024/64B4 live and
6074 always `$v0=0` with silent 64BC/6618 selects `H-PortLoopNoExit`.
64BC live and silent 6618/E114 selects `H-PortExitNoReturn`. Missing
controls select `H-CoverageInvalid`.

## Exact commands

1. Add `tools/apply_s3306_cinematic_loop.py` injecting probes at
   `0x800A5DD8` (log `$v0`), `L_800A6024`, `0x800A6074` (log `$v0`),
   `0x800A64B4`, `L_800A64BC`, `L_800A65E4`. Mirror the same transform
   into `/Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`
   so the next regen keeps it. Reuse the s3305 helper/env
   (`ROGUESQ_LOG_M5_POSTVIEWER_EDGE`) or a sibling
   `ROGUESQ_LOG_M5_CINE_LOOP=1`. Do not change guest stores/branches.
2. Build:
   `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --config Debug --target RogueSquadron64Recomp`
3. Run from `build/` with the ROM present, SIGKILL at 120 s, env:
   `ROGUESQ_LOG_PHASE=1 ROGUESQ_LOG_M5_POSTWAIT=1 ROGUESQ_LOG_M5_POSTVIEWER_EDGE=1 ROGUESQ_M5_POSTVIEWER_MARK_ALL=1`
   plus the new cine-loop mark-all. Require viewer return, VI 640 at
   `0x0066A500`, cinematic entry, and every new mark ID.

No M5 Step 3. No audio/output change.
