# NEXT: measure terrain-grid bbox width/depth at dd1/2/3 (H-grid64)
HYPOTHESIS-ID: g1c-dd8-limit
Lead (s6472, static, single-source): binPolygonIntoTerrainGrid 0x8004286C fills fixed 64x64 tables (0x80130DB0, 0x80131DB0 bytes; 0x80132DC0 word ptrs ending at terrain struct 0x80136DC0). bbox width/depth at 0x80132DB4/0x80132DBC scale with dd radius: predicted ~29/58/87 cells at dd1/2/3.
Hypotheses: H-grid64 (width or depth >64 at dd3 -> overflow/dropped cells), H-cap (record cap lhu 0x80130C4C at 0x80042DDC hit), H-real (neither: bbox <=64 at dd3).
Work: add a fprintf in the fixup script (tools/apply_s6036_dd.py style, after the 0x8004286C bbox stores) logging width, depth, 0x80130C4C and record index max per frame; regen order make_elf->N64Recomp->fixup->cmake; one run each dd1/dd2/dd3 (soak queue). 
Outcomes: dd3 width/depth >64 while dd2 <=64 -> fix by enlarging/relocating tables (or splitting bbox into 64-wide tiles); cap hit -> raise cap; neither -> H-real.
