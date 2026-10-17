# Session 5326 — M4 shared-boundary sampler result

The cxd4 sampler was extended to honor `RS64_RSP_MID_STRIDE` at the actual
instruction loop; the prior callback-only filter left the cadence fixed at
256 instructions. The port M4 probe was extended through the regeneration
fixup with generated Factor 5 PCs: `0x13AC`, `0x16F8`, `0x16FC`, `0x1708`, and
the stage-13 `0x1754`/`0x1770` branch continuations.

The corrected retail control run used stride 1, a whole-RDRAM write watch, and
VI tracing. It produced a 136,872-byte RSM1 stream, 10,000 positive-control
watch callbacks, and 479 VI samples. The instrument is therefore live.

The concurrent driven comparison did not reach the target 512-wide hangar
phase: the retail capture remained at 640/title through its captured window,
and the port remained at phase 3, width 640, origin `0x0066A500`. The port's
actual-PC M4 target table and the retail task/PC table consequently have no
shared target keys. H3 is selected. This rules out only the claim that the
new sampler already provides an aligned M4 comparison; it does not support H1
or H2 and authorizes no accumulator mitigation.
