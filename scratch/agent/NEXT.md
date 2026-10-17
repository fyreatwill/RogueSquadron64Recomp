# Next: name the object at 0x80138458 and the writers of its +0x50 float (phys 0x1384A8)
HYPOTHESIS-ID: m6-mission-input
Result s5080: computeGridLayerScrollOffset lerps on x=*(*0x80138D1C+0x50); mission obj=0x80138458, thresholds 2.0/-8.0, outputs 16.0/24.0; x tracks stick (W hold 250 distinct values), static otherwise. 0x130C40 not involved.
Hypotheses: Hship (obj is the player ship, +0x50 a world coordinate/altitude), Hcam (camera object), Hother (scroll/terrain object driven by ship).
Unit: widen the s5078 per-(pc,addr) census hook (tools/apply_s5078_flight_writer_census.py) to phys 0x138458..0x1384C0 and also log which pc writes 0x138D1C-pointer retargets (phys 0x138D1C); reuse scratch/agent/s5080_watch.sh. Discriminator: writer pc names (a ship-integration function = Hship; camera update = Hcam); positive control = any store to the range during W hold.
Note: after touching RecompiledFuncs, `touch src/main/register_overlays.cpp` before cmake.
