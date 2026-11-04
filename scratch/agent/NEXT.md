# NEXT: data-decoded function tails: prove them dead, then stop compiling them
HYPOTHESIS-ID: data-decoded-tail-audit

Why: s6868 closed G5 function names (docs/GENERATED-NAME-CENSUS.md). audioCompandS16 has a 0x54-byte real body but 103780 generated lines (9% of the tree, 3172 .word lines); __OSGlobalIntMask has 11376 lines; 24 functions hold .word lines. s5668's audio fault came from this tail, and any stray goto into it runs data. This is an idiom-class audit (ITERATION item 3 model): enumerate all 24, classify, close the class.
Hypotheses: H-dead (no label in a tail is reached from the real body, so every tail can be cut after the real end) / H-reached (a real branch or fall-through enters a tail: name it, it may be a real defect or a mis-sized symbol) / H-size (the toml size is wrong and part of the "tail" is real code; the .word position, not the size, marks the end).
Discriminator: one offline tool over the generated tree: per function, real end (toml size and first .word), then every goto or label crossing that end from below. Same-run control: an injected branch across the end in a scratch copy must be flagged. Then one runtime arm: trap at each tail entry (opt-in env in a scratch build), lvl1 and lvl5 flight and an audio-heavy cinematic, with a control trap on a live function firing.
If H-dead holds: add the cut to the fixup chain (tools/fixup_*.py plus tools/regen_replay.sh), regen_verify, report compile time and binary size before and after. Expect exactly the cut functions to differ.
Keep static_* callees of cut tails in mind: the data_gap_ bodies lose their only site and can go in the same step.
If an owner report arrives, it outranks this.
Ask owner when a human is next on: add tools/regen_replay.sh + regen_verify.sh to the CLAUDE.md regen order (owner file, not edited).
Owner judges: docs/owner_sheet_s6860_lvl10_hud_ab.png, docs/owner_sheet_s6861_pause_hud_ab.png.
Open, not queued (G4): FPS60+dd3 at 300 s, FPS60+dd2 on lvl10, wide bundles at 300 s continuous. Owner can lift the park for these.
