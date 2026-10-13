# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

(s4739 was a maintenance iteration: CURRENT-TRUTH compacted 60013 -> 37683 bytes, no experiments. The unit below is carried over unchanged from s4738.)

s4738 finding: runaway mission tasks restart because DMEM[0x153]==0x2C (selected by DL op 0xBD while 0x28 resident) reaches the window entry 0x1DB0, whose switch (factor5_ucode_recompiled.c ~5486, built by the fixup-6 splices in tools/fixup_factor5_ucode.py) has no 0x2C case -> `goto L_1DB0` task-entry restart.

Work unit: identify overlay 0x2C.
1. Read generated L_1298 / L_15A4 to find the overlay-table index/DMA descriptor used for id 0x2C (DMEM table, ROM/RDRAM source, size).
2. Compare with how 0x28 was handled (`r17 += 0x20; goto L_10D8`, fixup ~line 1027) and the spliced ids (10/C/14/18/1C/24).
3. Decide: real image to splice (new factor5_rsp_ovl*.toml) vs no-op-like route.

Hypotheses:
- H-2C-noop: image trivial like 0x28 -> route to L_10D8 with the same r17 advance.
- H-2C-real: image has code -> needs a splice.
- H-2C-misselect: 0xBD at d153 0x28 should not select 0x2C; our 0x15A4/0x1298 translation mis-computes the id.

Discriminator: dump the DMEM overlay-table entry for id 0x2C and the first 32 words at its RDRAM source at the first site-3 hit with d153==0x2C (reuse the kind-6 hook; one build, one run via `scratch/agent/s4737_run.sh`).
- All-zero / ret-only => H-2C-noop.
- Real code => H-2C-real.
- Nonsense entry or id absent from the table => H-2C-misselect.
Positive control: the same dump for id 0x28 must show known content.

Regen order if the fixup scripts change: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake. Put any generated-code edits in tools/fixup_factor5_ucode.py. Kill the game with SIGKILL; run from build/ with the ROM present.
