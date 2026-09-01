# M5 session 3584 — retail source-buffer writer boundary

The prescribed 60-second retail-oracle capture ran from `build/`; complete
output is preserved at `/tmp/rs64_source_buffer_writer.log`.

All controls were live. The whole-RDRAM watch recorded 11,274 writes, the
`0x1797B0..0x179930` image-task span recorded 674 writes, and the qualified
source-buffer watch `0x0065FA30..0x0065FA4C` recorded 600 writes. The run
completed after 9,149,882 execution-watch hits and 3,563 VIs. The 512-wide
transition occurred at VI 2804 (47.4 seconds, origin `0x006AB800`); the first
exact `0x006AB400` VI was 2865 (48.4 seconds).

The phase-gated source-buffer writer histogram had 176 hits at `0x800078EC`,
18 at `0x8002958C`, 13 at `0x80029590`, 6 at `0x80029A8C`, 5 each at
`0x80001EE4` and `0x80001F10`, and smaller counts at the remaining PCs. The
full histogram had 408 `0x800078EC` hits and 28 `0x8001F5E4` hits among the
600 writes. No non-`0x800078EC` PC was a stable dominant constructor or a
separately identified DMA writer.

Post-value sampling recorded 527 samples, 64 unique values, 72 overflowed
rows, and 11 nonzero words in the final 28-byte snapshot. Target-phase rows
included zero values at `0x0065FA30` and nonzero intermediate values such as
`0x00010004`, `0x00000004`, `0x00050000`, and `0x00040000`; the target
post-value PC table attributed the observed target rows to `0x800078EC`.

This selects H-RetailNoStableSourceWriter for the current oracle: the
earlier-constructor boundary is unavailable, not disproven. H-RetailCopyOrDma
is not selected because no stable distinct DMA/copy PC appeared. The exact
DMA-versus-writer ordering remains open because this capture exposed no DMA
event identifier. The positive controls and target phase rule out
H-CaptureInvalid.

ORIGIN: diagnostic-only retail source-buffer qualification. No mitigation was
added.
