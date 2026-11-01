# NEXT: G1d wide-aspect menu sweep (after the s6720 title fix)
HYPOTHESIS-ID: g1d-menu-sweep

s6720 fixed the title at 16:9/21:9. The interlaced 512x448 VI mode (width 1024 = 2x512, xScale 0x333) is now widened
to 2*fbw, and while it is live (rs64_g1d_title_vi) dpc_bridge zeroes each wide colour image once and clamps the
full-width scissor to the centre 512 columns. Other screens that use this mode or a sibling state have not been looked
at wide.

## Hypotheses
- H-ok: every other 512x448 screen (title OPTIONS submenu, controller/sound settings, pause menu, debrief, game-over)
  is drawn centred like the title and now displays clean.
- H-full: some menu draws full-width content (extra width wanted, e.g. a 3D backdrop) that the s6720 centre-512
  scissor clamp now clips; that screen needs the clamp off.
- H-other-mode: a menu uses a different VI mode that still carries 512-based stride/xScale (same garble as pre-s6720).
## Discriminator (one build, ONE batch of boot runs)
scratch/s6720/title.sh with an autopilot schedule that opens OPTIONS (10:start, then dpad down + A at the title) and a
forced-route run that pauses in flight (start at t~100) - window captures at 21:9, 16:9, 4:3. Log [osViSetMode #],
[fbw] title-vi, [g1d-title-clear] and ROGUESQ_LOG_G1D_RECT=1 (rect x extents per swap: a full-width screen shows
rects outside 256..768 before clamping). Compare each screen with its 4:3 frame. A garbled screen -> name its mode
from the log and extend the rule. A clipped screen -> narrow the clamp to the title state.
Secondary (single-source, s6719): why a wider terrain footprint changes the LucasArts logo shape.
