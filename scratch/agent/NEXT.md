# NEXT: 21:9 owner bundle (ASPECT 21:9 + FPS60 + dd4) under the s6852-s6855 region-gate defaults
HYPOTHESIS-ID: g1d-region-fps60-bundle

Why: the owner plays at 21:9; ZGATE/CFLIP latch on "first z_cmp-on prim" / "Z clear" / "colour-buffer flip". FPS60
adds render frames (60 Hz split) and dd4 changes frame density, so the latch-reset pattern can differ from the dd1/30 Hz
runs s6852-s6856 measured. Nobody has run the gate under FPS60 or dd4.
Hypotheses:
- H-ok: disc/blips 100% shifted, non-disc 0 shifted, same as dd1.
- H-latch60: FPS60 extra frames have no Z clear/flip before the HUD -> disc kept (disc left at 4:3 position) or sky shifted.
- H-dd4: dd4 terrain/far prims draw z_cmp-off after the latch -> world shifted in the box.
- H-crash: the bundle at 21:9 stalls/crashes (side-effect datum, root-cause it).
Discriminator, one recipe, arms sequential: scratch/s6856/abd.sh with XENV adding ROGUESQ_FPS60=1 ROGUESQ_DRAW_DISTANCE=4
(copy to scratch/s6857/abd.sh), SHIFT=256 FBDV=600 HOLD_S=300, lvl9 and lvl17 (and lvl1 if time). Read [region-zgate]
totals (disc vs non-disc, python one-liner from s6856 entry), summary stalls/crash, and build a sheet with
tools/owner_sheet_s6856.py (pick flight idx frames; check w1024 only). Outcomes: non-disc shifted >0 -> name texture with
tools/g1d_zoffobj.py on a KEEPBIN bin and fix the latch; disc kept >0 -> H-latch60; all clean -> H-ok, close and add
the 21:9 bundle line to docs/OWNER-OPT-INS.md if missing.
