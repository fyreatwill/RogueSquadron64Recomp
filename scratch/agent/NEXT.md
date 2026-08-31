# NEXT work unit — mark callback transfers at generated callers (RESUME)

HYPOTHESIS-ID: m5-callback-occupant-caller

## What has run and what artifacts exist

Session 3338 proved that `registerSiCallback` receives `0x8009123C` in
phase 2, but every captured `$ra` was zero. The entry probe is
regeneration-surviving and already in the fixup scripts. The existing
reachability script at `scratch/agent/run_s3333_m5_callback_reachability.sh`
passes host-boundary, task-handoff, title-1024, and hangar-512 controls.

Session 3339 was a checkpoint close-out: the iteration died before doing any
work. No build, no run, no code change occurred.

## Competing hypotheses

- `H-DirectTransfer`: an un-gated transfer marker fires at one of the known
  direct generated callsites and joins to the `0x8009123C` entry.
- `H-IndirectTransfer`: no known direct callsite marker fires, so the target
  arrives through an indirect dispatcher or callback path.
- `H-ContextMarker`: the transfer marker fires but cannot join by ordinal,
  showing that generated context/entry accounting is insufficient.

## Exact next commands

Add a transfer marker immediately before each generated call to `0x80007910`
(registerSiCallback), independent of phase. The probe must survive
regeneration — add it to the fixup script, not directly to generated code.
Then:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3333_m5_callback_reachability.sh

The positive-control rows must include host-boundary and task-handoff
controls, and the run must reach title 1024 and hangar 512. A joined
transfer/entry row selects `H-DirectTransfer`; an entry with no direct marker
selects `H-IndirectTransfer`; an unjoinable marker selects `H-ContextMarker`.
Missing controls invalidate the run and require a fixed rerun. No contract
change or mitigation is authorized.
