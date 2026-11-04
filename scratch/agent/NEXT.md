# NEXT: why generated function bodies run past the toml size
HYPOTHESIS-ID: generated-size-mismatch

Why: s6869 cut 18 decoded tails after the fact. audioCompandS16 has size 0x54 in syms/rogue_squadron.syms.toml, yet N64Recomp emitted 7384 more words, so the size never reached the generator. Fixing that at the source would remove the junk branch labels behind the s5668 lagging-label bug as well.
Hypotheses: H-elf (make_elf.py writes a symbol size that differs from the toml, or extends to the next symbol) / H-recomp (N64Recomp ignores the ELF size for these and runs to the next symbol) / H-toml (the recompiler reads a different symbol list from the one edited).
Discriminator: offline only. For audioCompandS16, lvj_checkComplexObjectives and __OSGlobalIntMask, print the size in the toml, in the make_elf ELF (readelf or nm -S) and in the N64Recomp output range. The stage where 0x54 stops being 0x54 selects the hypothesis. Same-run control: a function whose body matches its size must agree at all three stages.
If it is a one-line source fix: regen into a scratch dir, tools/regen_replay.sh, tools/regen_verify.sh. Expect 2708/75 or better, and the fixup_label_realign and cut steps to find less work. Do not change the live tree unless the compare holds.
Bounded: one session. If the fix touches N64Recomp itself and the compare moves, record it and take the next ladder rung (G3 in-flight frame diffs).
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_replay.sh + regen_verify.sh to the CLAUDE.md regen order (owner file, not edited).
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
