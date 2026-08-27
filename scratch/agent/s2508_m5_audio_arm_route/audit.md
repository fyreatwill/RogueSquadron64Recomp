# s2508 — audio-arm route reachability A/B

The retail oracle was run first with a whole-RDRAM write positive control. Its
log recorded control activity and reached the 1024 title phase; it did not
reach the 512 hangar within 90 seconds, so no retail null was interpreted.
The Debug target rebuilt successfully before the port capture.

The first probe-shell attempt was invalid because duplicate detached probe
processes shared each output directory. A corrected direct driver was run in
one persistent foreground session, launching both arms from the same build
with the same phase-relative key schedule.

| arm | 1024 title | 512 hangar | dispatch / ABI / DMA | image stage | audio return | PCM source / consumer | crash |
|---|---:|---:|---:|---:|---:|---:|---:|
| silent (`ROGUESQ_AUDIO_UCODE=0`) | 1 | 2 | 71 / 1397 / 1397 | 0 | 520 | 96 / 96 | 0 |
| image (`ROGUESQ_AUDIO_UCODE=1`) | 0 | 0 | 48 / 0 / 0 | 0 | 0 | 0 / 0 | 36 |

The silent arm reached title at 48.4 seconds and hangar at 60.1 and 68.4
seconds, passed the 1024-row gate control, and had no crash or abort. The
image arm crashed before title with `last-guest-pc=0x8000B650`; its native
crash symbol was `plume::MetalFramebuffer::MetalFramebuffer(...)+696`.

This selects `H-image-causes-route-stall` over `H-route-independent` and
`H-stub-degenerate` for the tested route. It establishes route reachability
only: the image arm never reached image-stage or PCM controls, so it does not
identify a writer, output contract, or cause of the pre-title renderer crash.
No audio behavior, output mapping, guard, or mitigation changed.
