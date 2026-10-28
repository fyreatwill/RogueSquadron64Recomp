# NEXT: does enlarging the flight-scene DL-chunk pool (scale by px) remove the dd4 px2 collapse?
HYPOTHESIS-ID: g1c-dd-phase2
Facts (s6563): px2 head pops/begin ~100 vs px1 ~50; splice rates equal; reinit at 0x80018094 builds a fixed 2909-chunk pool (relink loop 0x80018044 stride 0x108 inside buildAndRegisterDefaultMaterial 0x80017B88).
Hypotheses:
- H-D1: px2 demand genuinely exceeds a pool of any size reachable here (then bigger pool only delays collapse).
- H-D2: pool is retail-sized (2909) and px2's 2x demand outruns it; scaling count by px fixes it.
- H-D3: refuted-ish (equal splice rate).
Discriminator: in fixup (tools/apply_s6*.py, not generated C) multiply the 2909 count in buildAndRegisterDefaultMaterial by ROGUESQ_DD_POOLX (check the arena has room, carve from 0x80800000+ if needed). Run s6553_run.sh 4 2 "ROGUESQ_DLPOOLLOG=1" x5 and px1 x1 as control. H-D2: no empty_b=1, no 0x80000000 NULL-node SIGBUS in 5/5. H-D1: still empties, just later (record begin delta). Positive control: DLPOOLLOG len after reinit must show ~2909*px.
