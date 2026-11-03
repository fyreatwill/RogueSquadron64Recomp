# NEXT: 16:9 TV bundle (ASPECT 16:9 + FPS60 + dd4) under the region-gate defaults
HYPOTHESIS-ID: g1d-region-fps60-bundle-169

Why: s6857 closed the 21:9 bundle (H-ok). The owner's 65" TV runs 16:9, where the box is 520..630, shift 142, pad 25
(s6853, lvl1 only, 30 Hz dd1). Nobody has run the 16:9 gate with FPS60 + dd4.
Hypotheses: H-ok (disc 100% shifted, non-disc 0) / H-latch60 (disc kept >0 at 60 Hz) / H-dd4 (non-disc shifted >0) /
H-crash (side-effect datum, root-cause it).
Discriminator: copy scratch/s6857/abd.sh to scratch/s6858/abd.sh with ROGUESQ_ASPECT=16:9, MISSION_WIDTH=796, SHIFT from the
s6853 recipe (grep '^## Session 6853' PORTING-STATE.md for its abd.sh path and box/shift env), frame glob _w796. Run lvl1 and
lvl9 sequentially, HOLD_S=300, FBDV=600. Totals: python3 scratch/s6857/tot.py <dir>/zgate.txt (add the lvl1 disc textures
43DBF0/43E3F0 to DISC). Check FPS60 live via swaps/VI (~1.0+ vs 0.5). Sheet: tools/owner_sheet_s6856.py needs a width/box
argument for 796 (crop box ~x 500..796). Outcomes: all clean -> H-ok, close, add the 16:9 bundle line to OWNER-OPT-INS;
non-disc shifted >0 -> tools/g1d_zoffobj.py on a KEEPBIN bin; disc kept >0 -> H-latch60.
