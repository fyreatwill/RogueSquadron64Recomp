# NEXT work unit — mark callback transfers at generated callers

HYPOTHESIS-ID: m5-callback-occupant-caller

Session 3338 proved that `registerSiCallback` receives `0x8009123C` in phase 2,
but generated `$ra` is zero for every entry. The next build must mark the
transfer immediately before each generated call to `0x80007910`, independent
of phase, and join that explicit callsite marker to the entry ordinal.

## Competing hypotheses

- `H-DirectTransfer`: an un-gated transfer marker fires at one of the known
  direct generated callsites and joins to the `0x8009123C` entry.
- `H-IndirectTransfer`: no known direct callsite marker fires, so the target
  arrives through an indirect dispatcher or callback path.
- `H-ContextMarker`: the transfer marker fires but cannot join by ordinal,
  showing that generated context/entry accounting is insufficient.

## Discriminator and exact commands

Retain the independent retail baseline from Session 3335; a fresh oracle rerun
is unavailable because this checkout lacks its debugger-enabled core and Rice
plugin. Add the transfer hook to the regeneration fixup and current generated
direct-call sites, retain the entry/store/census hooks, then run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3333_m5_callback_reachability.sh

The positive-control rows must include host-boundary and task-handoff controls,
and the run must reach title 1024 and hangar 512. A joined transfer/entry row
selects `H-DirectTransfer`; an entry with no direct marker selects
`H-IndirectTransfer`; an unjoinable marker selects `H-ContextMarker`. Missing
controls invalidate the run and require a fixed rerun. No contract change or
mitigation is authorized.
