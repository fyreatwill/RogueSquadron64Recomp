# NEXT: fold s5740_hpwatch_{a,b} — which PC writes hp 0x137E7C to 0 (and lives 0x130B10)?
Read scratch/agent/m6/s5740_hpwatch_*/{summary,keys.log,lldb_att*.log}. Control: lldb log must show the 0x3470 watch hit before deletion; run.log must contain 'trap-at-swap' (TRAPSWAP=5200; mission onset is swap #4864, update_screen #11691 -- the two counters differ, s5739 used 12300 on the wrong one and never trapped).
Hypotheses: (H1) hp zeroed by collision/damage routine with huge damage; (H2) mission-state/respawn routine; (H3) port defect: host memcpy/memset clears the record.
Discriminator: top frame of the bt at the hp-to-0 write.
HYPOTHESIS-ID: g1-gameover-cause
