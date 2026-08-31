# NEXT work unit — locate the first retail state-pointer producer

HYPOTHESIS-ID: m5-frequency-state-pointer-producer

Ground truth for this iteration passed the whole-RDRAM control (10,000 before
removal), reached both target 512 origins, and positively fired the field dump.
Retail's `s1=0x80194B20` rows show varying source words and branch state at
both `0x006AB400` and `0x006AB800`; the exact producer remains unobserved.

Competing hypotheses and discriminator:

- `H-StatePointerParity`: the port and retail expose the same normalized state
  pointer contents and output family; the gap is later.
- `H-PortStatePointerGap`: the port consumer is live but its state pointer or
  pointed state word diverges before `0x80001CC8`.
- `H-StatePointerProducerAbsent`: retail's producer/entry PC fires in the
  target phase while the corresponding port call chain does not.
- `H-StatePointerUnevaluable`: controls fire, but no like-for-like producer /
  entry join can be formed.

The discriminating measurement is one phase-qualified join table:
`(consumer callsite, s1, pointed state word, output v1, producer/entry PC)`
joined to the successful receive. Retail must use `--pc-field-dump` and the
port must use the existing producer/entry/caller witnesses in the same run.

Session 3444 selected `H-PortStatePointerGap`: retail's phase-qualified
`s1=0x80194B20` rows vary, while both qualified port arms use `0x801BBD..`
state pointers with pointed word zero and output `0x2`. The next bounded unit
is to locate the first producer of the retail target state-pointer family and
compare its entry tuple with the port path.

Session 3443 selected `H-PortOutputUseGap`: retail's phase-qualified
`0x80001CC8` output values vary under state `s1=0x80194B20`, while both port
arms produce the same sampled `0x2` output with state keys in `0x801BBD..`.
The next bounded unit is to locate the first producer of the retail target
state pointer and compare its entry tuple with the port path.

Before building, ask ground truth with the whole-RDRAM positive control,
both title origins, hangar, and `--watch-pc 0x80001CB8,0x80001CC8`. Enumerate
all generated `jal` callers/entry candidates for the producer and add them to
one oracle watch set; use `--pc-field-dump` for the selected state pointer.
Then add the corresponding regeneration-safe port witness in the one paired
build/run. The discriminator is a phase-qualified
`(consumer callsite, s1, pointed state word, output v1, producer/entry PC)`
row joined to the successful receive:

- `H-StatePointerParity`: retail and port expose the same normalized state
  pointer contents and output family; the gap is later.
- `H-PortStatePointerGap`: the port consumer is live but its state pointer or
  pointed state word diverges before `0x80001CC8`.
- `H-StatePointerProducerAbsent`: retail producer/entry fires while the
  corresponding port call chain does not.
- `H-StatePointerUnevaluable`: all state/caller controls are live but no
  like-for-like producer/entry join can be obtained.

Build once and run both silent and Factor 5 image arms concurrently using the
validated route and all existing passive M5 controls:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    env zsh scratch/agent/run_s3442_m5_frequency_output_pair.sh

Keep waits, slots, dispatch, clear behavior, and PCM writeback unchanged.
