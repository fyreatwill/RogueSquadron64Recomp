# NEXT work unit — trace the first output use after frequency consumers

HYPOTHESIS-ID: m5-frequency-output-use-contract

The s3441 consumer witness is positive and selects `H-RetailConsumerParity` at
the observed `0x8010FEE0` receive boundary. The next bounded unit is the first
state/output use after the successful consumers at generated callsites
`0x80001B04` and `0x80001CB8`. Do not treat message zero as corrupt.

Before building, ask ground truth with whole-RDRAM control, both title origins,
hangar, and the first downstream execution/writer candidates obtained from:

    rg -n -A100 '0x80001B04: jal|0x80001CB8: jal' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_0.c

Use one oracle invocation with `--watch-pc` for all selected downstream JAL
sites and `--pc-phase-log-width 0x00790400:1024
--pc-phase-log-width 0x00790800:1024 --pc-phase-log-width 0x006AB400:512
--pc-phase-log-width 0x006AB800:512`, plus `--watch-write 0x0:0x800000`.
Only instrument sites that the oracle proves live in a target phase. Then add
one regeneration-safe port witness at the first live output/state site,
carrying the existing `(queue,msg,callsite,state)` join key and the first
output value. Build once and run the silent/image pair concurrently on the
validated LLE/spin-yield route.

Competing hypotheses and the single discriminating measurement:

- `H-RetailOutputParity`: the first post-consumer output/state value is
  present and equivalent on retail and both port arms; the gap is later.
- `H-PortOutputUseGap`: the port consumer is live, but its first output/state
  value diverges from the retail phase row.
- `H-OutputUnevaluable`: the oracle candidate or port witness is absent despite
  positive whole-RDRAM, phase, and consumer controls.

The measurement is one phase-qualified first-output tuple joined to the
successful receive row. Matching retail/port tuples select parity; a live
receive followed by a divergent first-output tuple selects the port gap; a
missing candidate with live controls selects unevaluable. Do not change waits,
slots, dispatch, clear behavior, or PCM writeback.

Build and run commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3442_m5_frequency_output_pair.sh
