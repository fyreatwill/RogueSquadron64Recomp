# NEXT work unit — capture the scheduler message handoff with positive controls

HYPOTHESIS-ID: retail-scheduler-message-handoff

Run one independent retail-oracle capture, phase-gated through title and
hangar, watching both `0x80019CCC` and `0x80019CD0` with the supported field
dump. Do not repeat the unavailable local `PatchesLib` target; guard
validation is parked until the configured Windows/MIPS host or generated
patch artifacts are available.

## Competing hypotheses

- `H-MessageFieldsExposed`: the handoff exposes an accepted message pointer,
  type, and `89F/28D44` fields at target-origin rows.
- `H-MessageFieldsUnavailable`: adjacent-PC detail still exposes only stable
  queue/context registers, leaving mutation, task type, and identity
  unresolved.
- `H-NoTargetCorrelation`: positive controls or target origins fail, making
  the field result unevaluable rather than absent.

## Discriminator

A whole-RDRAM positive-control hit plus target-origin rows in the same run is
required. Exposed accepted-message identity selects `H-MessageFieldsExposed`;
target rows with only the stable register set select
`H-MessageFieldsUnavailable`; failure to correlate target origins selects
`H-NoTargetCorrelation` and leaves the handoff unresolved.

## Exact command

From the repository root, with the configured debugger-enabled Mupen core
available at the documented path:

```sh
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 180 --watch-write 0x0:0x800000 --hit-cap 10000 \
  --watch-pc 0x80019CCC,0x80019CD0 \
  --pc-phase-log 0x00790400,0x00790800,0x006AB400 \
  --pc-field-dump 0x80019CCC,0x80019CD0 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```

Record positive-control count, VI origins, both PC counts, and the bounded
field rows. Do not add a port field or change audio behavior.
