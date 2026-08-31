# NEXT work unit — close the retail value-level output join

HYPOTHESIS-ID: m5-frequency-output-value-join

Session 3442 proved the retail load sites and both port first-output witnesses
are live, but the oracle did not expose a value-level `(queue,msg,callsite,
state)` join. The next bounded unit is to add that missing retail value join.
Do not treat message zero as corrupt.

Before building, ask ground truth with whole-RDRAM control, both title origins,
hangar, and the first downstream execution/writer candidates obtained from:

    rg -n -A100 '0x80001B04: jal|0x80001CB8: jal' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c

Use one oracle invocation with `--watch-pc 0x80001C0C,0x80001CC8` and
`--pc-field-dump 0x80001C0C,0x80001CC8`, plus
`--pc-phase-log-width 0x00790400:1024
--pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512
--pc-phase-log-width 0x006AB800:512`, plus `--watch-write 0x0:0x800000`.
Use the proven live sites to select the retail state/output fields and add one
regeneration-safe port witness that records the same field tuple and first
output value. Build once and run the silent/image pair concurrently on the
validated LLE/spin-yield route.

Competing hypotheses and the single discriminating measurement:

- `H-RetailOutputParity`: the first post-consumer output/state value is
  present and equivalent on retail and both port arms; the gap is later.
- `H-PortOutputUseGap`: the port consumer is live, but its first output/state
  value diverges from the retail phase row.
- `H-OutputValueJoinUnevaluable`: field/value joins remain absent despite
  positive whole-RDRAM, phase, and consumer/output controls.

The measurement is one phase-qualified first-output tuple joined to the
successful receive row. Matching retail/port tuples select parity; a live
receive followed by a divergent first-output tuple selects the port gap; a
missing candidate with live controls selects unevaluable. Do not change waits,
slots, dispatch, clear behavior, or PCM writeback.

Build and run commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3442_m5_frequency_output_pair.sh
