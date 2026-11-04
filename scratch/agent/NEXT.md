# NEXT: the other ELF sizes that disagree with the toml
HYPOTHESIS-ID: elf-size-valid-tails

Why: s6870 fixed 6 functions. 111 functions disagree with the toml (scratch/s6870/census.py). Most are 4-12 byte nop padding, but osYieldThread (ELF 0x1C00, toml 0x4C), tickCraftSelectScreen (0xD88 / 0x2EC), __osException (0x61C / 0x238), getTextureAttrBySlot (0x1B0 / 0x4C) and fake_func_800AF6A8 are not. Those tails hold no do_break-stopping .word, so the cut tool reports them and leaves them.
Hypotheses: H-real (the toml is short: the tail is real code reached by a path the walk misses) / H-unnamed (the tail is one or more real functions with no symbol, so an entry is missing from the lookup table) / H-data (dead decoded data, safe to size).
Discriminator: offline only. For each function with a delta over 0x20, run the walk for real_end, then look for jal, data-word and lui+addiu references to addresses in the tail (tools/audit_ptr_reach.py, controls as in s6870). Reference from real code = H-unnamed; walk reaches it = H-real; neither = H-data.
Only H-data rows go into tools/func_sizes.txt. Then tools/regen_front.sh, tools/regen_replay.sh, tools/regen_verify.sh; baseline is 2688 / 78 / 17 (scratch/s6870/compare.json).
Also fix: regen_obj_compare.py should report objects present on one side only. Check 801096D8's two read sites at 0x800AE428 and 0x800AE4EC directly.
Bounded: one session. Then take the next ladder rung (G3 in-flight frame diffs at the opt-in settings).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_front.sh, regen_replay.sh and regen_verify.sh to the CLAUDE.md regen order (owner file, not edited). Decide whether to regenerate the live tree.
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
