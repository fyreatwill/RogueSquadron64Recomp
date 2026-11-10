# NEXT: owner reports first; otherwise check allocTextRenderTarget and the other menu_overlay names in 0x800B2630-0x800B4400
HYPOTHESIS-ID: generated-symbol-misnomer-fixes
Context (s7073): 0x800B2630..0x800B3F24 is the async backdrop JPEG loader (enqueueBackdropLoad, tickBackdropLoaderWorker,
openBackdropJpegAssets, decodeBackdropTilesToTextures, freeBackdropLoadRequest; strings "backdrop/%s", "%03ld", "alpha" at
0x800A5C20..0x800A5C50 in ../rogue_squadron64/build/roguesquadron.elf .ovl.menu, file off 0x10b410 = va 0x800A5130).
Unit: list every menu_overlay.txt symbol with address in 0x800B2630..0x800B4400 (allocTextRenderTarget 0x800B32F4,
buildPrefixedAssetName 0x800B43F4, ...), read each body in ../N64Recomp/RecompiledFuncs (bound by next RECOMP_FUNC line, NOT
awk '/^}/' - bodies bleed), list its callees and the string constants it loads (0x800A5Cxx).
Hypotheses: H-backdrop (allocTextRenderTarget is the backdrop tile texture target; callers are the loader) vs H-text (a real
text render target with text callers). Discriminator: its callers and the w/h it is passed.
If misnomer: rename as in s7073 (scratch/s7073/renames.tsv recipe: perl word-boundary over live funcs_*.c, funcs.h,
recomp_overlays.inl, symbol_files, syms toml, every tools/ fixup needle+replacement), control = per-file counts + fixup_preempt
6/9, rebuild, scratch/s7031/arm.zsh L6 dd1 4:3 NOCAP with 1 s samples (positive control = renamed fn in samples).
If all names in the range hold: close the misnomer thread for the menu block and take the next G rung.
