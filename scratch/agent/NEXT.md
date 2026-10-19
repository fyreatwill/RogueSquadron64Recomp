Work unit: fold the s5514_wp_flag soak (scratch/agent/SOAK-RESULTS.md tail; log scratch/agent/m6/s5514_wp_flag/lldb_att*.log). Check first that the 0x3470 control watch hit (a 'Watchpoint N hit' before the delete). Then list the bt/ctx->r31 of every 0x130B58 hit and the value transitions; find the one that sets bit 0x02000000 (value & 0x02000000 going 0->1) and name its PC and caller. If the soak failed (nohangar etc.), re-queue once; hangar route is flaky ~3/5.
Hypotheses: H1 menu-overlay writer via passed pointer with register mask; H2 cutscene dispatch (cutsceneDispatchSlotsByFlag) sets it; H3 never set on this route.
Discriminator: writer PC list with bit-25 transitions; H3 = zero transitions with control firing.
HYPOTHESIS-ID: second-distinct-mission-coverage
