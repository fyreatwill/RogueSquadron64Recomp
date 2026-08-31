# M5 s3394 — dual-origin phase attribution

The independent retail oracle was run with whole-RDRAM and exact target-span
watches, `0x800078E8/0x800078EC` execution watches, and two 512-wide phase
buckets: `0x006AB000` and `0x006AB400`.

The first 120-second recipe passed the whole-RDRAM positive control (10,000
callbacks, with the target watch left armed) and reached the target 512-wide
route. Its execution rows were under `origin=0x006AB400`; none were under
`origin=0x006AB000`. The process stopped mid-trace at 74.2 seconds and emitted
neither final watch totals nor `pc-hist-phase`/`writer-pc-phase` summaries.

A same-recipe 45-second retry passed the positive-control setup but exited at
32.6 seconds, before the 512-wide phase. It could not supply the missing final
summaries either.

This is an invalid discriminator result, not evidence for either origin: the
exact target-watch total and both final phase histograms are unavailable. The
dual-origin oracle field is closed as unevaluable at this scope. No port
output, audio behavior, or mitigation changed.

Evidence: `scratch/agent/oracle_s3394_dual_origin.log` and
`scratch/agent/oracle_s3394_dual_origin_45s.log`.
