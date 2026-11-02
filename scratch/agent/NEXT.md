# NEXT: G3 LEVEL DESCRIPTION text on other levels + one retail pixel crop
HYPOTHESIS-ID: g3-ldesc-levels

State: s6802 closed lvl1 LEVEL DESCRIPTION at RDP level (static 150=150) and found CRAFT DESCRIPTION inert in both arms.
Gap: only level 1's text was compared, and the RDP signature cannot see an equal-width glyph swap.
Hypotheses: H-match (every level's description static set equal); H-diff-text (a level's string differs: static rect sets
differ, name the rects); H-diff-select (the port's SELECT LEVEL cursor lands on a different level for the same presses).
Discriminator, ONE pair run: a save with several levels unlocked in BOTH arms (find an existing multi-level .eep under
scratch/ - grep PORTING-STATE for "lvl5.eep\|unlock.*eep" - or ROGUESQ_FORCE_UNLOCK only works port-side, so it must be an
EEPROM file both arms load via SAVE_FROM / --save-dir; g3_menu_pair.sh hardcodes scratch/s6779/r1/lvl1.eep -> add an EEP= var).
PP: 17:start,23:start, then per level: cup, (8 s), cup, right (8 s) ... for 3-4 levels; ND>0 with angrylion VIDEO for a
second run if a pixel crop is wanted (or VIDEO=rdplog for segments). Score: tools/g3_rdp_segments.py + g3_rdp_segcmp.py per
description segment; positive control = lvl1 description (s6802 numbers); cross control = description of level k vs k+1
(must differ in static set).
