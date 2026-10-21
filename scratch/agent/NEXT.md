# NEXT: fold the s5768_setterbp soak
Read scratch/agent/m6/s5768_setterbp/summary and grep BPHIT in run_pre.log. Control: bp_mtm>0 and BPHIT a0 values look like 0x80xxxxxx (else the ctx offset/arg register assumption is wrong: fix and requeue).
H1 setter hit with a0==0x80137DBC before lives-- (player craft debris -> fail); H2 only NPC a0 (fail is health-only); H3 bp_scene=bp_npc=0 (fail via bit1 settle path, s5759).
HYPOTHESIS-ID: g1-nonhealth-fail
