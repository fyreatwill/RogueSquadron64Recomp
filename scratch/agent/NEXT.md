# NEXT: fold s5739_hpwatch_a — which PC writes hp 0x137E7C to 0 (and lives 0x130B10)?
Read scratch/agent/m6/s5739_hpwatch_a/{summary,keys.log,lldb_att*.log}. Controls: run.log has trap-at-swap; lldb log shows 0x3470 watch hit before deletion. If no mission reached / trap fired early, retune TRAPSWAP (mission origin 0x690400 at update_screen ~#11727) and requeue.
Hypotheses: (H1) hp zeroed by a collision/damage routine with huge damage (bt names a damage fn; check damage arg source); (H2) hp zeroed by a mission-state/respawn routine (flag/timer kill) -> bt names state fn; (H3) port defect: host memcpy/memset clears the record (bt in host code, not recomp fn).
Discriminator: top frame of the bt at the hp-to-0 write.
HYPOTHESIS-ID: g1-gameover-cause
