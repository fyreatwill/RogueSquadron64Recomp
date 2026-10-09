# Next work unit (s4325): qualify descriptor/filter/output payload join

HYPOTHESIS-ID: m5-step9-mort-output

State (s4324): the seeded-save matrix passed the independent MORT reference,
oracle controls, and both VI-512 port controls. Silent and real-image arms
each reached 128 calls at `0x8009D740` (256 call/entry rows total); early
payloads matched but later `a0/a1` and table-used/value sequences diverged.
Both arms then shared the known post-target `do_rom_read` crash.

Competing hypotheses:

- H-same-descriptor-different-filter: both arms consume the same descriptor
  class/rate and source bytes, but the filter table/arguments diverge before
  output.
- H-descriptor-class-divergence: the arms select different descriptor
  type/rate or table classes before the filter call, explaining the payload
  sequence.
- H-output-join: filter inputs are equivalent, but post-filter PCM/output
  bytes diverge at the generated or host boundary.

Discriminator: one phase-scoped table covering all 128 filter calls in each
arm, keyed by ordinal and descriptor identity, with descriptor type/rate,
`a0/a1`, table value, source/output spans and hashes before/after the filter,
and PCM source/consumer hash/count joins. Matching descriptor/type/rate and
source hashes with divergent output selects H-output-join; divergent
descriptor/table rows select H-descriptor-class-divergence; matching rows and
matching output but a consumer mismatch selects the host/PCM join. A missing
row is invalid unless both VI-512 controls and the filter positive control
fire.

Before building, inspect the independent controls and existing row writers:

`sed -n '1,220p' tools/oracle/README.md`

`rg -n 'filter-voice-audit|init-desc|pcm-boundary-(source|consumer)|8009D740|mort_probe' src/main tools scratch/agent/run_s4321_m5_mort_output.sh`

Add the complete table in one batch, preserving the positive controls and
phase budget. Build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run both arms in one matrix with the seeded `build/saves` and existing route
recipe:

`zsh scratch/agent/run_s4321_m5_mort_output.sh`

Require `oracle_gate=1`, the MORT reference verdict, one VI-1024 and one
VI-512 marker in the oracle, and `[m5-port-vi-control]=1` in both arms before
interpreting the payload table. Do not alter RSP dispatch, the decoder, AI
bridge, or add a game-path guard.
