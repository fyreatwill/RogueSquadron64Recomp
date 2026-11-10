# NEXT: owner reports first; otherwise rename the menu "Debris" cell-mesh misnomer family
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7071): placeholder sweep CLOSED (0/2500 placeholder defs, tools/s7071_hot_unnamed.py). Sweep = misnomers only.
Unit: rename the 0x800C7970..0x800C9B8C family in /Users/williambuckley/Documents/Tools/rogue_squadron64/symbol_files/
menu_overlay.txt (rebuildDebrisCellGeometry, emitDebrisCellFaces, buildDebrisCellBitfield, decodeDeltaCellCounts,
buildDebrisMeshFromCells, cloneCellBufferWithAlloc, allocZeroedCellRecord) to glyph-mesh names. First READ each body
(N64Recomp/RecompiledFuncs) so each name says what it does. Update every by-name reference in the same change:
`grep -rln <old> tools src docs/*.md` (tools/fixup_preempt_point.py FUNCS list for sure).
Then regen in order: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake build; boot to title + one menu text
screen (SELECT LEVEL) with 0 crash, and check fixup_preempt_point still reports its patch sites (positive control:
same count as before the rename — record it BEFORE regen).
Hypotheses: H-clean (rename is pure: same site counts, boot clean) vs H-hidden-ref (some fixup/hook matches the old
name silently and its patch count drops). Discriminator: per-fixup applied-site counts before vs after regen.
If rogue_squadron64 is not a git repo you may commit, record the diff in PORTING-STATE instead.
