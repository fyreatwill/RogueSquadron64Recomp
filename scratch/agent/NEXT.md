# NEXT: attribute the earlier wide title/menu width policy
HYPOTHESIS-ID: g1d-widescreen

s6171 selected H-menu-layout: the existing s6169b control has coherent title
and menu pixels, while the wide arm's early 512-wide dumps are horizontal
scanline garbage; later 796-wide select-level and flight dumps are coherent.
The next single work unit is to identify the earlier-phase writer that leaves
the wide title/menu path at 512, then make the smallest regeneration-safe
opt-in change to use the selected width. Do not change retail behaviour.

Competing hypotheses and discriminator:

- H-early-width-writer: an earlier menu/title video-state or framebuffer
  writer still hardcodes 512, and widening that writer makes the wide guest
  dump coherent.
- H-early-present: the guest framebuffer is coherent but the screen/present
  path corrupts it; an on-screen capture or VI-origin byte comparison differs.
- H-unsupported-asset: the wide guest dump is already corrupt before the
  framebuffer writer because an asset/display-list path assumes 512; the
  first bad RDP/VI join or source buffer identifies it.

Discriminator: use one paired run with a phase-scoped trace of every video
state/framebuffer allocation before phase 5, plus the existing RDP/VI join and
framebuffer dump. If the first bad wide frame has a 512 writer,
H-early-width-writer wins; if the guest dump is coherent but on-screen capture
is bad, H-early-present wins; if both are bad with no 512 writer,
H-unsupported-asset wins. A valid run requires control and wide title/menu
route markers, the `512x340 wv=796` allocation positive control, and no
crash/30-second VI stall. Do not add a mitigation or alter the retail default.

Useful bounded commands:

    rg -n 'partitionFramebufferMemory|buildAndRegisterDefaultMaterial|osViSetMode|ROGUESQ_FB_WIDTH|ROGUESQ_ASPECT' src tools RecompiledFuncs lib/rt64
    rg -n 'ROGUESQ_LOG_FB_ALLOC|\[fbw\]|ROGUESQ_LOG_RDP_ROUTE|phase=5' src tools
    # Build once, then run both arms concurrently with:
    # ROGUESQ_OSMEM_MB=12 ROGUESQ_ASPECT=16:9 ROGUESQ_FB_DUMP_VI=1
    # ROGUESQ_LOG_FB_ALLOC=1 ROGUESQ_LOG_RDP_ROUTE=1

The measurement must include the first wide title/menu framebuffer dump and
the first pre-phase-5 width writer; do not infer from already-valid flight
frames.
