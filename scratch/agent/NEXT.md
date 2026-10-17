# Next: resume the s5041 poison-on-free read-after-free probe on the mission route
HYPOTHESIS-ID: poison-on-free-raf-probe
s5059: census-on hangar recipe passed 3/3 (7/7 on current binary), so the route is usable again; the earlier nohangar stalls are unattributed/transient.
Run: re-queue the s5042 poison_off / poison_on arms (tools/apply_s5042_free_poison.py hook, ROGUESQ_FREE_POISON) with the s5037 default recipe incl. GUARD2, one at a time, phase-gated on VI transitions. Include a positive control (poison-everything fires). Discriminator: on-arm crash/divergence at a freed-block read with a writer PC means read-after-free exists; identical off/on means none on this route.
