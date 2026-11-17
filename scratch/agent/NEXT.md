# NEXT (s7499)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7498_ew_levels (tools/s7498_ew_recipe.zsh; `s7498_ew_levels ew arm=` rows in its out.txt):
partial=0 free=0 ctl=ok on L1 dd8 21:9 / L7 / L10 / L12 dd4 -> EW CLOSED 6 levels.

Work unit: class EX, cross-image overlap in the non-heap top region. s7498: every writeback range is inside one used heap block or in
[arena top, RAM top) (dd1 [751E00,800000), dd8 [B20000,C00000)); several images share that region (colour 751E00..800000 at dd1 spans
the 76A000 depth extent; z-clear idiom sets colour = Z base). EW cannot see one image's writeback landing on ANOTHER image.
Hypotheses: H-ex-disjoint (no writeback of image A covers bytes of an image B, B != A's own base, set in the same swap) / H-ex-zclear
(the only overlaps are colour==depth same-base z-clear pairs, benign by design) / H-ex-clobber (a writeback of A covers a live B: name
A, B, rows, and whether the guest/RDP reads B after it).
Instrument, ONE build: in main.cpp s7498_wb, keep per swap the set of images (base, width, kind) from rs64_s7493_img; for each writeback
range list every other image whose [base, base + width*rows_set*bpp) intersects; classify same-base / disjoint / cross. Rows `[s7499] x`,
`[s7499] sum`. Control: ROGUESQ_S7499_CTL=<n> registers a fake image at the n-th writeback's phys+bytes/2 -> must count cross.
Run: `env XC=ROGUESQ_S7499_EX=1+ROGUESQ_S7499_CTL=20 zsh tools/s7498_ew_recipe.zsh` (L4 dd1, L15 dd8 21:9).
