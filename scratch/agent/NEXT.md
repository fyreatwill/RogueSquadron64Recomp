# NEXT work unit (s2075)

HYPOTHESIS-ID: m5-retail-wait-slot-contract

## Work unit

Run one corrected Rice retail-oracle witness before adding or changing any
port instrumentation. Watch the physical slot/status table at guest
`0x80154620` (`0x154620` physical), read and write it, poll the full status
table, and attribute the wait and status writers by PC while driving the
known title-to-hangar route. The whole-RDRAM watch is the positive control;
title VI 1024, hangar VI 512 at origin `0x006AB400`, and PIF input reads are
the route controls. This is ground-truth capture only: no port build, guest
store change, task-field change, routing change, canary change, wait/guard
change, or mitigation is authorized.

## Competing hypotheses and discriminator

- **H-RetailWaitReadsSlotTable** — the retail wait at `0x80095D54` reads the
  slot table at `0x154620`, and named status writers such as `0x8009B30C` or
  `0x8009B7EC` produce the observed transitions. Select this only if the
  whole-RDRAM control, both route anchors, wait-PC hits, slot read hits, and
  named writer attribution all fire.
- **H-RetailWaitReadsOtherTable** — the wait PC fires on the qualified route,
  but the candidate slot-table read watch stays silent while status polling or
  another watched region moves. This selects a wrong-table/address boundary,
  not a port null.
- **H-RetailStatusOtherWriter** — the candidate slot table is read and
  written on the qualified route, but the writer-PC histogram is dominated by
  PCs other than the named status writers. This selects an unclassified retail
  writer boundary.
- **H-RetailWaitNotReached** — the independent route reaches title/hangar but
  the requested wait PC and candidate-table reads do not fire. This selects a
  call-site/function-address or phase-scope mismatch only if the route and
  whole-RDRAM controls pass; otherwise the run is UNEVALUABLE.

The discriminator is the single oracle table joining whole-RDRAM count,
title/hangar/PIF controls, `waitForAnyAudioSlot` PC hits, slot-table reads,
slot-table write PCs, and `--status-poll` transitions. A missing target row
without all controls is not evidence.

## Exact command

Run from the repository root; the command writes its bounded output to an
absolute capture path:

```sh
mkdir -p scratch/agent/oracle_s2075_wait_slot
tools/oracle/build/rs64_oracle \
  --core /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core/projects/unix/libmupen64plus.dylib \
  --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 \
  --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib \
  --secs 120 \
  --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
  --watch-write 0x0:0x800000 \
  --watch-write 0x154620:0x154630 \
  --watch-read 0x154620:0x154630 \
  --watch-pc 0x80095D54,0x8009B30C,0x8009B7EC,0x8009B2C4 \
  --detail-watch 1 --detail-watch 2 \
  --pc-hist-watch 1 --pc-hist-watch 2 \
  --vi-trace --pif-trace --status-poll \
  > scratch/agent/oracle_s2075_wait_slot/run.log 2>&1
```

Require a whole-RDRAM positive-control count, title `1024 @ 0x00790400`,
hangar `512 @ 0x006AB400`, and PIF reads before interpreting any watch null.
Preserve the output and append the selected table to the next ledger entry.
