# Session 3058 — retail VI request attribution

## Work unit

Ran the retail oracle with the whole-RDRAM positive control, Rice video,
validated Start schedule, VI trace, and execution watches for `osViSetMode`
and `__osViSwapContext`. No port behavior or instrumentation changed.

## Evidence

- Positive control: whole-RDRAM watch reached 10,000 writes and was removed.
- Retail reached the title transition `640 -> 1024` at about 17.2 seconds,
  then the hangar transition `1024 -> 512` at about 38.4 seconds.
- `osViSetMode` execution watch: 153 calls total.
- `exec-prev` attribution for `osViSetMode`:
  - `prev=0x8001B8DC`, 142 calls
  - `prev=0x8001B720`, 6 calls
  - `prev=0x8001BB54`, 5 calls
- The companion symbol file and project symbol map identify
  `0x8001B8DC` as the direct callsite in `applyPendingViChanges`
  (`0x8001B7F0`, size `0x2AC`). The generated port body and overlay table
  contain the corresponding `applyPendingViChanges` function and callsite.
- The same-build port capture in s3056 recorded only widths 320, 2, 640,
  and 640, with no width-1024 request.

## Classification

`H-RequestDescriptor` is selected for this capture: the retail 1024 request
comes through the shared `applyPendingViChanges` callsite, while the port has
the corresponding path but submits a non-1024 descriptor in the tested run.
This rejects the narrow missing-caller hypothesis and does not require an
overlay-dispatch explanation for this edge.

The oracle attribution and the generated/port callsite mapping are two
independent lines of evidence. The port width comparison relies on the prior
s3056 capture because this work unit intentionally did not add a port probe.

Raw capture: `oracle.log` in this directory.
