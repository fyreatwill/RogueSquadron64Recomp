# Exercise the full regen chain on a pristine tree

HYPOTHESIS-ID: m5-audio-destub-mission-route

s4810: A9 in RS64_REPLAY; ovl2c_mode is regen-safe via fixup_factor5_ucode. Remaining: the replay has never run end to end with A9/A10.
Work unit: in a scratch dir, run make_elf.py -> N64Recomp into a fresh output dir (NOT the live RecompiledFuncs), then tools/fixup_game_funcs_vendored.py <dir>; check "[s4648-replay] failures=0" and that funcs_23/24/25/26 cmp identical to live.
Discriminator: failures=0 + cmp identical => chain preserves A9/A10; any FAIL names the script to repair. If regen into a scratch dir is not possible, say so and move to M5 plan next step.
