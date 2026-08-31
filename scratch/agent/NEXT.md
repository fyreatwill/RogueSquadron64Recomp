# NEXT work unit — retail ground truth for M5 consumer reachability

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3350 completed a bounded M3 message-queue API guard audit. The
internal `do_send`/`do_recv` guard did not protect public entry points because
`osSendMesg`, `osJamMesg`, `osRecvMesg`, and `osCreateMesgQueue` could call
`TO_PTR` first. Those entry points now reject out-of-KSEG0 queue pointers;
the existing valid queue path is unchanged.

Competing hypotheses for the next M5 ground-truth unit:

- `H-ConsumerIndirect`: retail executes the service/accumulator bodies through
  an indirect callback edge, while the port has a reachability gap.
- `H-ConsumerGate`: retail enters the bodies but a status/slot predicate gates
  the named stores, and the port differs at that predicate.
- `H-ConsumerWrongNames`: the retail PCs do not represent the corresponding
  consumer route despite the generated bodies.

Discriminator: run the retail oracle with a whole-RDRAM positive control and
phase-gated exact execution watches for `0x8009B5A8`, `0x8009BD7C`,
`0x8009B600`, `0x8009B85C`, and `0x8009BDE8`, retaining each watch's
`prev_pc` and hangar origin `0x006AB400`. Retail entry plus named stores with
an indirect previous-PC chain selects `H-ConsumerIndirect`; entry with stores
absent and a live status/slot predicate selects `H-ConsumerGate`; no
corresponding retail entry/store activity selects `H-ConsumerWrongNames`. An
absent hangar phase or absent whole-RDRAM control is invalid, not a null.

Exact command shape from the repo root (substitute the documented debug-core,
retail-ROM, and Rice-plugin paths):

    tools/oracle/build/rs64_oracle --core <debug-core.dylib> --rom <retail.z64> --secs 180 --video <rice.dylib> --watch-write 0x0:0x800000 --watch-pc 0x8009B5A8 --watch-pc 0x8009BD7C --watch-pc 0x8009B600 --watch-pc 0x8009B85C --watch-pc 0x8009BDE8 --pc-phase-log-width 0x006AB400:512 --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start

Do not build or add a port instrument until the oracle positive control and
hangar phase both pass. Capture output to a non-dot final path and use SIGKILL
if the frontend needs stopping.
