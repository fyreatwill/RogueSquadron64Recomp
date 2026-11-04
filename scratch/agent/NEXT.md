# NEXT: audit hard-coded heap-address tests in host patches as a class
HYPOTHESIS-ID: g1d-heap-address-tests

Why: s6860 lvl10 HUD bug was a fixed address bound (0x80300000) applied to a heap table. s6861 closed the pause-window item. Same idiom may hide in other host patches.
Unit: grep tools/apply_s*.py, src/main, src/rsp for comparisons of guest pointers against literal 0x80xxxxxx bounds, classify each site: static-data bound (fine), heap-dependent (bug class), or dead.
Hypotheses: H-clean (no other heap-dependent bound) / H-more (some gate depends on where the heap lands, so it differs per level or per OSMEM/spill layout).
Discriminator: per site, is the compared address from static data or from rs_malloc? Runtime check for any heap-dependent one: ROGUESQ_HUD_LOG=1 on two more levels, list vp 0x80138D20 elements, confirm nothing projected sits in 0x80110000..0x80300000. Control: lvl1 and lvl10 tables must appear in the same log.
Outcomes: H-more -> fix by class with a same-build A/B and frame check (scratch/s6860/ring.py misses dim rings: use scratch/s6861/score.py). H-clean -> write the table to the ledger, take the next ladder rung.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
