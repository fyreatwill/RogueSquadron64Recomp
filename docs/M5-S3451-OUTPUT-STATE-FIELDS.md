# M5 s3451 — output/state field schema witness

The batched build added `rs64_m5_output_state_fields` at guest PCs
`0x80001C98`, `0x80001CB8`, `0x80001CC8`, and `0x80001F84`. It records the
oracle-compatible fields `(s0, s1, source_word, branch_selector, source_byte,
branch_state)` plus output registers, `state_word`, phase, and PC. The hook is
phase-gated to title origin `0x00790400`/`0x00790800` and emits an explicit
positive-control marker.

Build: `cmake --build build --config Debug --target RogueSquadron64Recomp`.
Run: `scratch/agent/run_s3449_m5_state_tuple_context.sh`, 80 seconds each,
silent and Factor 5 image arms, SIGKILL teardown.

Results:

- Silent arm: positive control 1, 2,048 schema rows; target counts were
  `0x80001C98=514`, `0x80001CB8=510`, `0x80001CC8=510`, and
  `0x80001F84=514`. Early title rows used `s1=0x80110000`, then
  `0x80110ECC`, unlike the first retail rows.
- Image arm: zero new schema rows and no positive-control marker. Its existing
  frequency consumer/output hooks still reached title and proved
  `0x80001CB8`/`0x80001CC8` activity, so this is a hook-path control failure,
  not evidence that the target PCs were absent.
- Retail control: `scratch/agent/s3450_oracle_fixed.log` had all four target
  PCs live at title origin, including varied source/output fields.

The field divergence is single-source because only the silent arm emitted the
new schema. No output/state contract conclusion is promoted until the image
arm's positive control is repaired and both arms join on phase and ordinal.
