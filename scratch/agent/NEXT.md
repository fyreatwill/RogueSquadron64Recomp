# NEXT: audit hard-coded heap-address tests in our host patches (idiom class)
HYPOTHESIS-ID: g1d-heap-address-heuristic-audit

Why: s6860 lvl10 HUD fault came from a fixed address bound (0x80300000) applied to heap objects, validated on one level. Other
patches may make the same assumption, and the frame sheet was the only thing that caught this one.
Hypotheses: H-none (remaining address literals name static data or fixed tables) / H-more (another test compares a heap pointer with a
level-dependent location; its effect differs on lvl10, the low-loading level) / H-mode (a bound depends on OSMEM or RAMTOP, so it moves with aspect or dd).
Method, offline first: grep tools/apply_s*.py, tools/fixup_*.py, src/main, src/rsp for comparisons of guest pointers against 0x80[1-9A-F]xxxxx literals;
classify each site static / heap / layout-dependent, using load_level_hmp d4 per level (scratch/s6860/flight.py) for the heap range. Guard or prove dead.
Also list vp 0x80138D20 elements on two more levels with ROGUESQ_HUD_LOG=1 to check nothing projected sits in 0x80110000..0x80300000.
Outcomes: H-none -> close the class with a table in docs; H-more -> same-build A/B per site, frame check on lvl10 and lvl1.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png.
