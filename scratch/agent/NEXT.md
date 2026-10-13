# Next work unit

HYPOTHESIS-ID: mission-phase-correctness

s4743 done offline: overlay 0x2C image bounded (externals only L_10D8, L_112C; no jal/jr;
see scratch/agent/s4743_ovl2c_static.txt), fixup draft at scratch/agent/fixup6r_draft.py.

OPEN DEPENDENCY (human): RSPRecomp allowlist (scratch/agent/UNBLOCK.md). Do not work around it.
Try `../N64Recomp/build/RSPRecomp factor5_rsp_ovl2c.toml`; a permission denial = still
blocked: go BLOCKED (do not substitute again). If it runs:
1. Output lands in build/factor5_ucode/factor5_ucode_ovl2c_recompiled.c
2. Wire fixup6r_draft.py into tools/fixup_factor5_ucode.py after the 6k..6q blocks.
3. Regen (make_elf -> N64Recomp -> fixup_game_funcs -> cmake), run scratch/agent/s4737_run.sh.
Discriminator: runaway DL tasks (site-3 restart via L_1DB0, 10-14x) drop to normal 1x if the
splice fixes it; unchanged => 0x153==0x2C is not the restart cause. The ovl-route 0x2C counter
must fire (positive control) with no new Unhandled jump target.
