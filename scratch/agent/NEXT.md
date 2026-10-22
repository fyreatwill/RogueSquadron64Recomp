# NEXT (s5925): which findSegmentObjectSphereHit caller is BOLT DAMAGE?

HYPOTHESIS-ID: g1-mission-progression

s5924: hret=6 was lock-on-site only; per-caller hits (s5921 run.log [s5908]): 800ff288 75/3.37M, 800f141c 2246, 800f14dc 1867 (funcs_41 viewpoint/LOS probe), 8005cf5c/d0d8/d24c ~850 each (lock-on loops), 8005eb5c 0, 8004dd84 0.
Hypotheses: (A) damage = 800ff288 (75 hits, overlay; rare hits because bolts are few/short-lived); (B) damage does not use this function (separate bolt-vs-object path); (C) 800ff288 hits happen but consumer discards.
Discriminator: extend rs5908_call (tools/apply_s5908_callers.py) with per-(caller, shape w0) hit table AND a log line for each 800ff288 hit (obj, t, ship bolt active flag); disasm 800ff288's enclosing function in RecompiledFuncs to name the consumer. Positive control: 800f141c hits must appear per shape.
Outcomes: A -> trace its consumer for the damage/msg5 post; B -> grep writers of NPC hp/msg5 senders instead; C -> read consumer after return.
Run: scratch/agent/s5921_poke.sh variant after rebuild.
