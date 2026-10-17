# Next: pristine-regen discriminator for the dropped s4296 patch
HYPOTHESIS-ID: m6-mission-stall
Hypotheses for the s5085 drop: H-skip (RS64_SKIP_REPLAY=1), H-noop (apply script exits 0 w/o patching), H-stale (funcs_26.c regenerated, fixup never run).
Discriminator: regen into a SCRATCH dir (never the live RecompiledFuncs): make_elf.py -> N64Recomp -> fixup_game_funcs_vendored.py <scratch>, twice (default and RS64_SKIP_REPLAY=1); count 'PATCH: s4296 A14 spin yield' in funcs_26.c. Absent only in SKIP arm => H-skip; absent in both => H-noop (new post-condition will exit nonzero); present in both => H-stale.
Note: fixup cannot run on a copy of the patched tree (s5090 logs).
