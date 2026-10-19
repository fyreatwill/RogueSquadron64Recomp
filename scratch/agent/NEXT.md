# Next work unit: read s5480_objc_end (scratch/agent/m6/s5480_objc_end, SOAK-RESULTS.md)
Question: once counter word 0x138064 reaches 3 (wp hit, TS timestamps in lldb_att1.log), do breakpoints setHudEnableBit4 / requestMissionTransitionMode fire?
Hypotheses: (A) bp fires within seconds -> mission ends legitimately at ~450 s hold; read which phase follows. (B) counter hits 3 but bp never fires -> lv0_checkComplexObjectives not called or early-out upstream: find its caller. (C) counter never reaches 3 this run (autopilot variance) -> repeat; s5479 got 3 only at the end.
Control: wp on 0x138064 must show stores (it did in s5479).
HYPOTHESIS-ID: m6-mission-end-trigger
