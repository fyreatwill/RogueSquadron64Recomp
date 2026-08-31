# NEXT work unit — ground-truth the divergent state-pointer writer

HYPOTHESIS-ID: m5-state-pointer-producer

Session 3471 qualified the existing port tuple witness. Retail and port both
passed positive controls and reached title, but the first consumer tuple
diverges at `s1`/source fields: retail has `s1=0x801B1590` and the port has
`s1=0x80110000`. Exact writer attribution is still open.

Competing hypotheses and discriminating outcomes:

- `H-RetailStateWriter`: retail writes the qualified `0x801B1590` state family
  and the port's producer/state route differs.
- `H-PortPointerSelection`: retail and port use equivalent producer values,
  but the port selects a different state pointer before the consumer.
- `H-ObservationInvalid`: the physical watch or phase/control schema does not
  fire, so writer attribution remains unevaluable.

Discriminating measurement: before changing the port, run the independent
retail oracle with whole-RDRAM control plus a physical watch over the known
state-pointer/table span, title-gated to origin `0x00790400`, and retain
writer-PC attribution. A control and writer/value rows select
`H-RetailStateWriter`; control plus matching retail/port writer values but a
different port pointer selects `H-PortPointerSelection`; missing control or
writer rows selects `H-ObservationInvalid`.

Work unit: ask ground truth with one oracle run only. Do not build port
instrumentation until the oracle schema fires. Do not compare sequential
animated arms. Do not alter audio waits, slots, status handling, consumer
dispatch, clear behavior, or PCM writeback.

Exact preparation command:

`tools/oracle/build/rs64_oracle --core /Users/williambuckley/Documents/Tools/rs64-oracle/iter974-armB/projects/unix/libmupen64plus.dylib --rom /Users/williambuckley/Documents/Tools/rogue_squadron64/rogue_squadron.z64 --video /opt/homebrew/lib/mupen64plus/mupen64plus-video-rice.dylib --secs 40 --watch-write 0x0:0x800000 --watch-write <physical-state-span> --pc-phase-log-width 0x00790400:1024 --pc-hist-watch 1 --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start --hold-ms 150`

Replace `<physical-state-span>` only after resolving the exact target span from
the existing Session 3468/3471 evidence; the span must be physical and have a
same-run whole-RDRAM control.

Expected outcomes: writer/value rows on the qualified state span select
`H-RetailStateWriter`; no target rows with a live control selects
`H-ObservationInvalid`; a matched writer/value but different selected pointer
selects `H-PortPointerSelection`. No mitigation or runtime behavior change is
authorized by this unit.

Evidence baseline: `scratch/agent/s3471_retail_tuple.log`,
`scratch/agent/s3471_m5_port_tuple/run.log`, and
`docs/M5-S3471-OUTPUT-STATE-TUPLE.md`.
