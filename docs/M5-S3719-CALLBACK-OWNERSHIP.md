# M5 s3719 — callback ownership table

The paired run added explicit callback source and host-thread fields to image
and PCM-consumer rows. Both arms reached VI 512 and fired the RSP source
positive control. The real arm emitted 201 image-stage rows and 101
PCM-consumer rows in the target phase; the silent arm emitted 33 consumer rows
and no image rows, as expected for its stubbed RSP arm.

Every sampled real-arm image row identified `callback_source=image_stage` and
host thread `14050803808701975833`; every sampled consumer row identified
`callback_source=queue_samples` and the different host thread
`5506149817041922107`. The streams shared 96 target route ordinals, and all
96 shared ordinals still had different host-thread identities. Source labels,
thread identity, phase-local sequence, queue depth, and route ordinal/row were
present. This remains single-source port evidence because the retail oracle's
debugger-enabled core was unavailable.

This selects `H-CallbackOwnershipBoundary` at the host callback boundary and
refutes `H-SharedCallbackState` as a complete explanation. It does not show a
stale route ordinal: image and consumer rows overlap route ordinals, so the
remaining queue/consumer discrepancy cannot be attributed to route identity
alone. Retail callback/thread parity remains open.
