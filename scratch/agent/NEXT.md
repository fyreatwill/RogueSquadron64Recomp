# NEXT work unit — trace the first state-pointer producer

HYPOTHESIS-ID: m5-frequency-state-pointer-producer

Session 3443 selected `H-PortOutputUseGap`: retail's phase-qualified
`0x80001CC8` output values vary under state `s1=0x80194B20`, while both port
arms produce the same sampled `0x2` output with state keys in `0x801BBD..`.
The next bounded unit is to locate the first producer of the retail target
state pointer and compare its entry tuple with the port path.

Before building, ask ground truth with the whole-RDRAM positive control,
both title origins, hangar, and `--watch-pc 0x80001CB8,0x80001CC8`. Add the
candidate caller/entry PCs found from the generated `jal` census and use
`--pc-field-dump` for the selected state pointer. The discriminator is a
phase-qualified `(consumer callsite, s1, pointed state word, output v1)` row
joined to the successful receive:

- `H-StatePointerParity`: retail and port expose the same normalized state
  pointer contents and output family; the gap is later.
- `H-PortStatePointerGap`: the port consumer is live but its state pointer or
  pointed state word diverges before `0x80001CC8`.
- `H-StatePointerUnevaluable`: all state/caller controls are live but no
  like-for-like producer/entry join can be obtained.

Build once and run both silent and Factor 5 image arms concurrently using the
validated route and all existing passive M5 controls:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3442_m5_frequency_output_pair.sh

Keep waits, slots, dispatch, clear behavior, and PCM writeback unchanged.
