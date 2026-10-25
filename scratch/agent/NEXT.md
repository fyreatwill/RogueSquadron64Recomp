# Does extending the s6207 image drop by 0x25000 (pure translation with the pool) fix wide HUD/texture corruption?
HYPOTHESIS-ID: g1d-widescreen
s6216 measured: ctl image ends 0xB00000, pool 0xB25000, HUD TLUT lives in the 0x25000 gap; wide drop ends image AT pool, covering the gap (memset+RT64 wb clobber TLUT). 
Change: tools/apply_s6031_far.py rs64_g1d_image_drop: drop = ov + env ROGUESQ_G1D_DROP_EXTRA (default 0 for the control arm, 0x25000 test arm). Regen order make_elf -> N64Recomp -> fixup_game_funcs -> cmake (DEVELOPER_DIR for Metal).
Arms (one build, sequential, 12 MB, 16:9): extra=0 (control: must reproduce [g1d-wb] end=0xAE6E00 and TLUT clobber) vs extra=0x25000. H-short: wb/memset end becomes 0xAC1E00, TI max unchanged in 0xAE5xxx, HUD ammo readout renders correctly in framebuffer capture. H-other: still wrong -> something else lives in the gap or image moved into heap data. Check heap NULL / crash markers.
