# NEXT: fold the s5769_setterbp soak (fixed BPHIT printf)
Read scratch/agent/m6/s5769_setterbp/summary and grep BPHIT in run.log/run_pre.log. Control: bp_mtm>0 (s5768 hit 6x) and a0 values look like 0x80xxxxxx; if bp_scene>0 but a0 garbage, the ctx offset (ctx+32 = r4?) is wrong - check recomp_context layout and requeue.
H1 scene setter hit with a0==0x80137DBC (player craft debris -> fail, supported by s5768 hit order scene-setter immediately before each mtm); H2 only NPC a0 (NPC setter hit 0x in s5768); H3 fail via bit1 settle path (s5759).
HYPOTHESIS-ID: g1-nonhealth-fail
