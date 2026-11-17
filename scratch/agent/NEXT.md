# NEXT (s7520)
HYPOTHESIS-ID: executed-code-bytes-census

First: fold s7519_fp_levels from SOAK-RESULTS if it ran (score 0 -> FP CLOSED 6 levels in CURRENT-TRUTH item 20; 1 -> read
scratch/s7519_fp_levels/out.txt OUTSIDE rows (kind, line, st_pc); 3 -> no arm's planted wb hit a DMA slot with dirty lines: try another
ROGUESQ_CACHE_SHAPE_CTL_WB k (s7519 L4/L15 landed at k=783/773 on slot 0x801B4ED0); 4 -> no [s7519-sum]).

FO+FP closed the libultra replaced-function surface. New idiom class (CURRENT-TRUTH item 21) FQ = executed code bytes vs the
recompiled image. A static recompiler runs the code the ROM held at regen time; hardware runs whatever bytes sit in RAM when the
I-cache fetches them. osInvalICache has 2 sites (s7518 census) = code-overlay loads. Hypotheses: H-canon (every overlay's RAM text at
each osInvalICache / first execution equals the ROM bytes N64Recomp compiled for that overlay slot, relocations applied), H-dead (some
text bytes differ - e.g. runtime-relocated jal targets or data in a text section - but the recompiled code reaches the same targets),
H-live (the game writes code at run time - patching, self-modifying, a decompressed overlay that differs from the ROM image - so the
port runs different instructions than hardware).
Instrument: at each [cache] op=iinv (ROGUESQ_LOG_CACHE_SHAPE=1, ultra_translation.cpp) and at each loadOverlay completion, hash the
RAM range and compare it with the ROM bytes of the overlay section mapped there (overlay table from the regen ELF / N64Recomp section
list; tools/ already has make_elf.py section data). Also a store watch over the loaded text (mark the range in the s7475 bitmap; any
guest store or DMA into executing text after load = row). Ctl: plant one byte flip in a loaded overlay's RAM text (env) and require a
DIFF row. Runs: L4 dd1 + L15 dd8 21:9 via tools/g1e_owner_quiet_arms.zsh, then a levels soak.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
