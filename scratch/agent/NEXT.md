# NEXT (s5887): class-2 objects take ~all fire; class-1 targets get 12/710 hits
Context (s5886): SEND decode fixed (obj=*(slot+4), desc=obj+0x34). 666/710 hits are class-2 (fail-arm descs 80319cdc/a9c/e5c ~135 each). Destroying all three = lose arm.
Hypotheses: (a) class-2 are friendly/escort objects the autopilot's blind fire hits because they sit on its path; (b) class-2 are ordinary hostiles that the game wants killed and the lose arm is a separate trigger; (c) class-2 desc positions coincide with class-1 groups (aim ambiguity).
Discriminator: dump class-2 descs' positions (+0x78 float xyz words 4-6 like [spawn1]) and class (+0x70/+0x74/+0x80) next to class-1 positions, plus player pos at each class-2 hit; compare with retail lv0 data (docs/M6-LV0-OBJECTIVE-TARGETS.md). Control: class-1 rows already exist. Offline first: tools/dump_lv0_objective_targets.py with class 2.
Run: zsh scratch/agent/s5885_ctx.sh style (g1_fireall.sh, LOG_HITS+LOG_HUDBIT).
HYPOTHESIS-ID: g1-mission-progression
