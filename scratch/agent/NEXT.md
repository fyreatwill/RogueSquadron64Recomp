# NEXT (s7678)
HYPOTHESIS-ID: g6c-standin-level-change

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
s7677 fixed the stand-in item map key (generation, not count) and proved it with a planted reorder; the real hangar route only
ever reloads level 15 at the same dat address. Unit: the real LEVEL-CHANGE case, stand-ins on.
Route: forced level select (ROGUESQ_FORCE_UNLOCK + ROGUESQ_FORCE_SAVE_MISSION + ROGUESQ_NO_SAVE_WRITE, s5705-s5720 recipes; copy
the game to its own folder, never touch build/saves), fly level A, PAUSE/ABORT, pick level B, fly; STANDINS=1 LOG=1 dd4 16:9 FPS60.
Measure from `[standins] N objects ... dat X level L` and `[s7677-gen]` lines:
- rebuild fires on the level change (level field changes), gen tally of A has wrong=0, B's handoffs match=item (pos only as fallback).
- H-leak: B's first build still shows A's items (dat unchanged + level unchanged at first submit) -> rebuild trigger needs the
  mission-init edge, not the dat/level pair. Fix there.
- Also check s_first / s_dwin / s_calls (function statics, never reset) do not skew B's spawn early_s numbers (early_s must be
  measured from B's first submit; compare B's early_s against a B-only run of the same level).
Positive control: ROGUESQ_S7677_PLANT=1 with GEN=0 must still show wrong>0 on the second build.
If the forced route cannot change level inside one run, write that down with the evidence and take M6 item 3b (keyed
title->mission hold, log every CRASH/stall) as the datum-producing unit.
One game at a time, SIGKILL only, <=2 CPU-heavy jobs, no repeat-hold soaks.
