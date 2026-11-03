# NEXT: 21:9 abort last-hold soft strip (cosmetic residual of s6845)
HYPOTHESIS-ID: g3-wide-abort-hold

State (s6845): the bright ~0.25 s post-wipe hold at 21:9 is FIXED (our s6156 HUD anchor shifted the full-screen wipe
glyph -256 px; apply_s6845_hudwipe gates it on x scale <= 8; rect_wrap now wraps texrects at ul.x 0). Same-build A/B
3 vs 0 bright frames. Residual: the LAST hold frame at 21:9 is drawn with the soft-edge combiner cc 119623 at ul 1.0 px
(RDP E4FFF700 00004000 S 0), where 4:3 draws the flat-black cc 11FE23 at ul 0.5 px. The window shows a ~68 px soft
bright strip at the far left for ~0.3 s (scratch/s6845/b21on w_0113.68..113.93; sheet docs/owner_sheet_s6845_abort_hold_21x9.png row 3).

Hypotheses:
- H-thresh: drawSubtitleText / the wipe update picks the flat-black glyph state when the wipe x (ox, or base x in 10.2)
  is below a retail-sized constant. At 21:9 ox ends at -512 + 1.024 (4:3: -256 + 0.5), so the doubled step lands past it.
- H-timing: the combiner alternates by frame parity / wipe timer, and the 4:3 run happened to land on 11FE23 (w43 run
  had 119623 ul 17 then 11FE23 x2; b43 11FE23 x2). Then 4:3 can also show the strip on some runs.
- H-anchor2: another of our G1d x patches (s6144 FP_XSCALE, s6104 frustum) scales ox for the wipe object, and the
  1.024 offset is ours.

Discriminator (one build, two runs: 21:9 + 4:3, route scratch/s6845/port_abort.sh <tag> "<env> ROGUESQ_WIPE_SCAN=6712:6760"):
extend the s6845 `[glyph]` probe (tools/apply_s6845_glyph_probe.py + rs64_s6845_glyph in src/main/main.cpp) to also log
the text object's flag word (obj+0x14, which selects the FA prim-colour path at 0x80016010), obj+0x2C..0x2F (prim
colour), and the combine word the caller emits for that glyph (find the FC writer in drawSubtitleText: the static
combine table at 0x038060 holds both FC11FE23 and FC119623 entries). Then read the selector: if it is an ox/x
threshold -> H-thresh, fix by scaling the constant with the G1d x scale in a fixup (or gate in the wipe updater);
if it is a timer/parity -> H-timing, check a second 4:3 run and stop if 4:3 shows the strip too (retail behaviour);
if ox's 1.024 comes from an FP_XSCALE-style patch -> H-anchor2.
Positive control: the probe must show cc 11FE23 for the 4:3 hold frames (b43 VI 6745/6747).
Budget: this is iteration 2 of 2 for g3-wide-abort-hold. If unresolved, park (0.3 s, left 7% of the screen) and take
the next ladder rung.
