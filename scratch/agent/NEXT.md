# NEXT (s7523)
HYPOTHESIS-ID: rsp-dpc-register-model

First: fold s7522_fs_levels from SOAK-RESULTS if it ran. It scores max(FS, FR): 0 -> FS CLOSED 6 levels in CURRENT-TRUTH item 20.
1 -> read scratch/s7522_fs_levels/out.txt LIVE rows (`t= b153= src= route=`: the port runs other code than the resident image there).
Name the 0x153 writer and fix the route in tools/fixup_factor5_ucode.py. 3 -> a ctl did not fire ([s7522-ctl] / [s7521-ctl] lines).
4 -> no sum.

Class FT = the gap FR exposed: the RSP-side DPC/SP status register model. FR found our DPC model zeroes DPC_CURRENT per task
(rs64_dpc_current_read in src/rsp/dpc_bridge.cpp returns g_rsp_dpc_end), so L_1DB0 always takes b3 where hardware could take
path A when the RDP is still busy. Audit every mfc0 the gfx ucode issues (grep RSP C0 reads in build/factor5_ucode/factor5_ucode_recompiled.c:
SP_STATUS, DMA_FULL/BUSY, SEMAPHORE, DPC_START/END/CURRENT/STATUS/CLOCK). Per read site, log the value the port returns and the
branch it drives. Compare with a hardware model: RDP consumes [CURRENT,END) at a finite rate, so a task that starts while the
previous task's list is still draining sees CURRENT != END.
Hypotheses: H-canon (every read site's branch is the same under both models), H-dead (they differ only on paths whose effect is
nil, as FR's path A submits an empty range), H-live (a read site changes control flow, e.g. a wait loop skipped or a list re-submit).
Ctl: env forces one DPC_STATUS busy bit / CURRENT != END read per site class and it must row.
Runs: L4 dd1 + L15 dd8 21:9 via tools/g1e_owner_quiet_arms.zsh (+ROGUESQ_G1E_PROBES=1). Run `mkdir -p $R` first. Then a levels soak.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
