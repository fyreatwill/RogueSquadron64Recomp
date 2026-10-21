# NEXT: fold s5741_hpwatch_{a,b} (480 s hold) — which PC writes hp 0x137E7C to 0 (and lives 0x130B10)?
Read scratch/agent/m6/s5741_hpwatch_*/{summary,lldb_att*.log}. Control: lldb log shows the 0x3470 watch hit (rand_recomp) and run.log has 'trap-at-swap'.
s5740 finding: 0x137E7C is a float (150.0 -> 130.0 -> 130.03) written by updatePlayerCraftPhysics (swc1 $f2,0xC0($s3), PCs 0x800B29F8/0x800B1FA0) via playerXwingUpdate; 150 s hold ended before any death.
Hypotheses: (H1) hp zeroed by collision/damage routine; (H2) mission-state/respawn routine; (H3) port defect (host memcpy/memset clears record).
Discriminator: top frame of the bt at the hp-to-0 write (value 0 after >=1 normal write).
HYPOTHESIS-ID: g1-gameover-cause
