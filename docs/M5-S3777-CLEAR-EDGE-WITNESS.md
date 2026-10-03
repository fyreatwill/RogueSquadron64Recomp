# M5-S3777 — clear-edge witness remained unevaluable

The Debug target built successfully, then the prescribed image-only capture ran
beside the retail oracle using the repaired writer-setup witness.

The oracle whole-RDRAM positive control fired. The image arm passed all six
family-store controls, emitted the writer-setup input control, and reached both
target phases: title `0x00790400` / width 1024 and hangar `0x006AB400` / width
512. It emitted two `[m5-writer-setup]` rows, both at edge `0x8008F2CC`, but
neither row identified a clear object: `clear_obj=0`, `alloc_len=0`, and the
observed `a2` was zero. No `[m5-family-edge]` row appeared. The summary counts
were `oracle_positive=1`, `family_store_control=6`, `image_title=5983`,
`image_hangar=837`, and `family_edge=0`.

This is the qualified H3 outcome. The positive controls prove the run reached
the relevant phases and that the store and writer-setup instrumentation was
active; the missing clear-object and family-edge rows therefore make the join
unevaluable, not evidence that the stores belong to a legitimate alternate
object. The next probe must repair the witness at the actual clear/allocator
boundary and retain the family-edge control. No mitigation, value injection,
audio-gate change, or writer suppression was made.
