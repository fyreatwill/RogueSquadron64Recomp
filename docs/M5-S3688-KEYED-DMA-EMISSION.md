# M5 s3688 — keyed DMA emission boundary

The fixed qualified concurrent capture passed the retail whole-RDRAM,
descriptor, source-span, title, hangar, and type-2 controls. The port reached
both target phases with source, stage, ABI, and DMA controls active and no
crash or abort. The oracle recorded 343,162 whole-RDRAM writes, 674 source-span
writes, and 907 phase-matched type-2 task rows.

The port recorded 512 hangar source rows, 2,762 hangar stage rows, and 5,975
per-range DMA rows. Each DMA range now carries the source event, task
generation, and latest route sequence/ordinal/row captured at the DMA observer;
the positive control is visible in rows with nonzero source events and changing
generations/routes. Of 258 hangar source rows without a same-generation stage
row, 257 had no per-range DMA row with the same source event and one had a
contradictory key. The added fields therefore fire, but the output-DMA
emission boundary does not preserve a joinable key for the absent-source
class. This selects `H-DmaKeyStillUnavailable` and does not select
`H-LaterRouteOwnsInput` or `H-StaleInputAcrossReuse`.

The result is single-source port evidence for the key classification; retail
independently validates the driven target phases and watched activity. The
first corrected run was unevaluable because the port crashed before phase
controls in the existing scheduler path and was not included. No guest value
was skipped, rewritten, or guarded.

The next boundary is the input DMA call itself: retain a per-input-DMA event
and task/route snapshot before later output DMAs can overwrite the thread's
last source event, then repeat the same qualified capture.
