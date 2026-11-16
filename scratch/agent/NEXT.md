# NEXT (s7485)
HYPOTHESIS-ID: m3-guest-uaf-loads

s7484 landed the EI load watch (tools/apply_s7484_loadwatch.py + upstream_compat.cpp s7484_*, recipe tools/s7484_uafload_recipe.zsh);
L4/L15 H-load-clean with in-flight load plant DETECTED. Queued soak s7484_uafload_levels (L1 dd8 21:9, L7/L10/L12 dd4).

1. Fold s7484_uafload_levels from SOAK-RESULTS.md / scratch/s7484_uafload_levels/out.txt: score=0 with load_plant=1 and load_ctl=1 on
   every arm -> close class EI in CURRENT-TRUTH (6 levels). score=1 -> read the `[s7484] uaf-load ... loc=F` rows + load-bt/free-bt,
   name the reader and the freeing caller (that is the work unit). score=3 -> fix the control (plant tries/timeout) first.
2. Then the next idiom class: the EI side datum, byte over-reads past the rs_malloc request (class EJ): swizzleTextureRowsToTmem
   0x800248CC..F0 and decodeJpegScanToImage 0x800C96AC..; decide per site whether the over-read is bounded by retail alignment
   (texture row padding / JPEG bit-reader lookahead = H-benign) or reads a neighbour block's data into output (H-overread). Discriminator:
   the request size vs the loop bound in each function (offline disasm in build RecompiledFuncs), plus whether the read value reaches a store.
Hypotheses (item 1): H-load-clean (0 F/Urec) / H-load-uaf (F rows). Discriminator: locator class at load time.
