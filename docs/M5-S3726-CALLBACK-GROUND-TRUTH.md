# M5 s3726 — callback ground-truth request

## Work unit

Ran one independent retail-oracle capture before adding any port
instrumentation. It used the whole-RDRAM positive control, Rice video, the
validated Start schedule, both target 512-wide origins, and execution watches
for `0x80033FCC`, `0x80029E80`, `0x80029F30`, and `0x80094648`. The task dump
was joined to `0x80033FCC` and restricted to audio tasks.

## Result

The whole-RDRAM control reached 10,000 callbacks. Retail reached both target
origins and completed 4,462 VI samples in 75.2 seconds. The watched PCs
produced 2,752, 2,325, 2,324, and 129 execution rows respectively. The
`0x80033FCC` task rows alternated target data pointers: `0x80171E70` at
`0x006AB400` and `0x80173CB0` at `0x006AB800`; both were audio task type 2.

This is independent evidence that the retail target route has active guest
audio-task paths at both target origins. It does not expose host callback
threads, SDL queue ownership, or a retail callback sequence, so it cannot
select among `H-CallbackQueueOwnership`, `H-GuestContractDownstream`, and
`H-SharedQueueState`. The requested host-side ground-truth discriminator is
unavailable from this oracle interface; a port-side table is now justified.

ORIGIN: diagnostic-only oracle execution watches, task dumps, and the existing
whole-RDRAM positive control. No guest or host behavior was changed.

Evidence: `scratch/agent/oracle_s3726_callback_ground_truth/oracle.log`.
