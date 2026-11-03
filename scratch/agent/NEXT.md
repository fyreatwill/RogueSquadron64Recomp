# NEXT: owner frame sheet for the closed G1d radar-region work at 21:9 (lvl9 + lvl17 flight), then ladder G5
HYPOTHESIS-ID: g1d-region-owner-sheet

State (s6855): region-shift scope CLOSED. Under ZGATE+CFLIP+TEXRECT=0 (all defaults) only the radar disc and blip tris
move at 21:9 (lvl9 T7A37B0/T7A3FB0, lvl17 T7965C0); world, sky and world markers (R78E080, R79B270) stay put.
No owner-viewable frame exists for s6854/s6855 (FBDV=1500 dumps landed on menus in s6854).

Unit: one in-flight frame per level for the owner. scratch/s6855/abd.sh with SHIFT=256 and FBDV set so dumps land after
first_objwr (lvl9 ~70 s, lvl17 ~59 s into the run; pick FBDV from the s6855 harness VI counts in scratch/s6855/AB.txt,
e.g. dump every 600 VIs and take the first frame after mission_t). Build a 2x2 contact sheet (lvl9, lvl17 x
TEXRECT=0 / TEXRECT=1 if a marker is in the box, otherwise just the two default frames) into docs/owner_sheet_s6856_*.png.
Expected: disc inside the ring at the right edge, no wedge left behind, no sky/world strip displaced.
If a frame shows a displaced element, that's a datum: name its texture with tools/g1d_zoffobj.py on a KEEPBIN bin.
Then: G1d awaits owner; next ladder rung with open work is G5 (renaming sweep) unless CURRENT-TRUTH Next steps adds one.
