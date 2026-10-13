# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4740 result: overlay 0x2C is a REAL image: ROM 0x27368, 0x240 bytes (DMA len field 0x23F), dest = window 0x1DB0 (idx 0), ends `j 0x112C; ori ra,0x10d8`. Overlay 0x28 is the 0x1C-byte stub at ROM 0x27348. ROM base for the 0x7A table = 0x25610.

Work unit: splice overlay 0x2C.
1. Model on factor5_rsp_ovl1c.toml / ovl24.toml (check how the scratch composite .z64 is built; it overwrites only the window range at the hardware dest). Create factor5_rsp_ovl2c.toml (text_address 0x04001DB0, ROM 0x27368, size 0x240).
2. Add a case 0x2C at the 0x1DB0 window switch in tools/fixup_factor5_ucode.py (~line 1020, next to the 0x28 route), routed like 0xC/0x14/0x18/0x1C.
3. Regen: make_elf.py -> N64Recomp -> fixup_game_funcs.py -> cmake. Re-run scratch/agent/s4737_run.sh; expect runaway tasks (site-3 hits 10-14) to drop to ~1 per task.

Hypotheses: H-splice-fixes (runaway disappears); H-other-edge (persists via another unrouted id; read d153 in the dlw ring); H-image-needs-more (2C jumps outside its image, stray/crash).
Positive control: tasks with d153==0x28 behave as before.
