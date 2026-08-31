# NEXT work unit — join the port target-field input to publication

HYPOTHESIS-ID: m5-port-field348-input-join

Session 3409 closed the `0x800052C4` candidate: it is live in the port but
does not target `0x801797B0` or `0x801798B0`. The remaining measured port
target is the `0x8008F2CC` zero-fill, reached after the slot read at
`0x8008F2C8`; stage 3 then copies zero DMEM to `0x801798B0`.

Competing hypotheses:

- `H-PortField348InputMismatch`: the port slot/input value differs from
  retail at the target phase and causes a legitimate alternate clear.
- `H-PortField348ClearIsExpected`: the slot value and clear are equivalent to
  retail, so the missing nonzero producer is downstream of the clear.
- `H-PortField348JoinGap`: the existing host witnesses do not join the slot
  read, clear, and stage-3 publication in one route/ordinal.

Discriminator: first use the existing completion-safe oracle checkpoint as
ground truth, then add one phase-scoped port witness for the `0x8008F2C8`
slot read, `0x8008F2CC` memset, and stage-3 row keyed by route ordinal. Build
once and run silent/image arms together with whole-RDRAM, title/hangar,
image/DMA, and PCM controls. Matching slot values plus a joined zero clear
selects `H-PortField348ClearIsExpected`; a port-only or mismatched value
selects `H-PortField348InputMismatch`; live controls with no ordinal join
selects `H-PortField348JoinGap`.

Run from the repo root:

`python3 tools/apply_s2447_m5_static_calls.py && python3 tools/apply_s2448_m5_static_callers.py`

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Then run the same qualified route as
`scratch/agent/run_s3409_m5_052c4_join.sh`, with only the new input/join
witness added. Do not change waits, slots, dispatch, clear behavior, or PCM
writeback.
