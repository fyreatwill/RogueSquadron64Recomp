# NEXT work unit — capture the caller supplying the early callback target

HYPOTHESIS-ID: m5-callback-occupant-caller

Session 3337 proved that `registerSiCallback` writes `0x8009123C` in phase 2,
but did not identify the caller supplying that value. Capture the callee-entry
return address and argument for every registration, with the existing early
store and census controls.

## Competing hypotheses

- `H-PortRegisterEntryCaller`: an entry probe at `0x80007910` sees
  `$a0=0x8009123C` and a distinct `$ra`/caller marker during phase 2.
- `H-PortKnownCallerAlias`: the entry probe sees `0x8009123C` only from one of
  the already-known generated callsites, indicating the prior callsite mark
  was not aligned with the actual transfer.
- `H-PortStoreEntryMismatch`: the entry probe never sees the argument although
  the exact store hook does, indicating a recomp dispatch/context mismatch or
  an indirect value mutation inside the callee.

## Discriminator and exact commands

First retain the prior independent retail callback-table baseline; a fresh
oracle rerun is unavailable because this checkout lacks its debugger-enabled
core and Rice plugin. Add one entry probe immediately on entry to generated
`registerSiCallback` at `0x80007910`, logging `$a0` and `$ra` in bounded phase
buckets. Keep the early store mark, direct callsite marks, and full census.
Run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3334_m5_callback_writer_attribution.sh

The positive-control rows must include the host boundary/task controls and
the run must reach title 1024 and hangar 512. An entry row with
`a0=0x8009123C` and a stable caller marker selects `H-PortRegisterEntryCaller`;
only a known caller selects `H-PortKnownCallerAlias`; a store row without a
matching entry row selects `H-PortStoreEntryMismatch`. Missing controls
invalidate the run and require a fixed rerun. No contract change or mitigation
is authorized.
