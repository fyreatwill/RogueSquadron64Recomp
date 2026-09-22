# M5 session 3729 — retail source payload boundary

Ran one independent retail-oracle capture with Rice video and the validated
Start schedule. The run lasted 75.2 seconds / 4,466 VI and reached both target
phases: 1024-wide `0x00790400` and hangar 512-wide `0x006AB400`/`0x006AB800`.

The whole-RDRAM positive control fired 266,969 writes. The source watch
`0x1797B0..0x179A48` fired 1,830 writes overall, and its target-phase
post-value summary sampled 664 bytes with 90 nonzero bytes. Its writer census
included `0x80007670`, `0x8001E2C0`, the `0x8001F...` family, and the later
`0x800078EC` clear. The task-data watch `0x173CB0..0x173DB0` had a target
snapshot with 106/256 nonzero bytes. The candidate output window
`0x166450..0x169450` was nonzero in its final snapshot but had no target-phase
writer rows; the secondary output window was written outside the target bucket.

This selects `H-RetailSourceNonzero`: retail carries nonzero source/task data
into the image-task phase, unlike the qualified port's zero source payload. It
refutes `H-RetailSourceZero` and makes `H-RetailOutputOnly` insufficient as the
primary explanation. The post-value witness is not a complete byte-for-byte
layout proof; the next experiment must join retail source content and writer
timing to the port's corresponding range.

ORIGIN: diagnostic-only oracle watches, phase histograms, and post-store
summaries. No guest or host behavior changed.
