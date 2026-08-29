# NEXT work unit — identify the upstream VI-mode caller in retail

HYPOTHESIS-ID: m5-audio-route-upstream-retail-boundary

## Single work unit

Run one retail oracle capture for the new caller handoff `0x800186C0`, the
`jal 0x8001BB6C` that enters `selectAndApplyViMode` after video-buffer cleanup.
This is distinct from the rejected direct `osViSetMode` callsites
`0x8001B720`, `0x8001B8DC`, `0x8001BB54`, and `0x8001BC28`, and from the closed
consumer/pre-consumer/publication watches.

## Competing hypotheses

- H-NewRetailBoundary: `0x800186C0` executes during title or hangar, directly
  identifying a live upstream caller into the selected-mode path.
- H-RetailBoundaryAbsent: controls pass but `0x800186C0` has zero target-phase
  executions; this caller is not the missing handoff.
- H-RetailControlInvalid: the positive control or title/hangar phase markers
  fail, so the candidate result is unevaluable.

## Discriminating measurement

The oracle run must produce the whole-RDRAM positive-control threshold and VI
phase transitions to title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`.
A target-phase execution row for `0x800186C0` selects H-NewRetailBoundary;
valid controls plus no candidate execution selects H-RetailBoundaryAbsent;
missing controls or either target phase selects H-RetailControlInvalid.

## Exact commands

```
mkdir -p scratch/agent/s3131_m5_retail_186c0
tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 70 --watch-write 0x0:0x800000 --watch-pc 0x800186C0 --pc-phase-log-width 0x00790400:1024 --pc-phase-log-width 0x006AB400:512 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start --hold-ms 150 > scratch/agent/s3131_m5_retail_186c0/oracle.log 2>&1
```

Record the control count, title/hangar rows, and candidate rows. Do not add a
port instrument unless the oracle selects H-NewRetailBoundary.
