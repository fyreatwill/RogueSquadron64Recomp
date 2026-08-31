# NEXT work unit — capture the early callback-table store writer

HYPOTHESIS-ID: m5-callback-occupant-store-writer

Session 3336 found no direct generated callsite registering `0x8009123C`, but
the port census saw that value appear at 164 ms. Capture the registry store
itself before target-phase gating.

## Competing hypotheses

- `H-PortEarlyStore`: `0x80007928` stores `0x8009123C` during boot/phase 2;
  an ungated store hook will report the value and its nearest guest marker.
- `H-PortStoreNot9123C`: the store hook sees only `0x80003250` or other
  values, so the census value comes from an alternate writer/loader.
- `H-PortCensusTransient`: the store hook and 1-ms census disagree in timing
  or value, indicating a transient observation or instrumentation race.

## Discriminator and exact commands

First retain the Session 3336 retail oracle command and controls. Then change
`rs64_m5_callback_writer_event` so `pc == 0x80007928` is admitted at every
phase, while keeping its bounded per-bucket rows; retain the two direct
registration callsite marks and full callback census. Run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3334_m5_callback_writer_attribution.sh

The positive-control rows must include the host boundary/task controls and
the run must reach title 1024 and hangar 512. A pre-target store row with
`pc=0x80007928 value=0x8009123C` selects `H-PortEarlyStore`; a clean store
census despite the table transition selects `H-PortStoreNot9123C`; a store
row that disagrees with the adjacent census transition selects
`H-PortCensusTransient`. Missing controls invalidate the run and require a
fixed rerun. No contract change or mitigation is authorized.
