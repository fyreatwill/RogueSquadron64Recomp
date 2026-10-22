# NEXT (s5906): per-shape-class r2 and fine-test outcome

HYPOTHESIS-ID: g1-mission-progression

s5905: no caller-side predicate; all shape classes take collideSegmentAgainstObjectNodes (0x80069AF0). RET rate 80330c5c 20%, 80323f58 1%, 80330b74 0%.

Hypotheses:
- H-size: 80323f58 etc. are large-scale shapes (big r2), thin bolts pass through hollow meshes; 80330c5c are NPC-scale.
- H-filter: fine test rejects by node/material flag per class (shape-specific), independent of size.
- H-objective: the 21 objective NPCs use shape records other than 80330c5c, which is why RETs do not progress c1.

Discriminator (one build, one run of scratch/agent/s5902_life.sh): in rs5904 tally add per-class (a) r2 = cc[3] min/max at sin_, (b) count of calls into 0x80069AF0 and its returns (wrap in funcs_16.c at the jal 0x8006AB40 site), (c) at objective-NPC teardown/spawn log [desc obj]+0 shape. Positive control: classes with RET>0 must show fine-test ret>0. Fold into tools/apply_s5835_sphere_probe.py incremental (see apply_s5905_shape58.py pattern).
