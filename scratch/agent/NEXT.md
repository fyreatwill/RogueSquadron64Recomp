# NEXT: root-cause the dd4 POOLX=4 crash in renderFlatMeshFaceGroup (s6549)
HYPOTHESIS-ID: g1c-dd-phase2
Hypotheses: H-heap (cap*0x18 pool at 2400 overlaps/exhausts neighbouring heap block, s6062), H-ptr (larger window feeds stale/garbage mesh node pointer), H-flaky (crash unrelated to cap; px1 repeat also crashes sometimes).
Work unit: run scratch/agent/s6549_run.sh 4 1 and 4 4 and 4 2 twice each (separately, one at a time); for crashes get the faulting guest address (x1=0x80011524 in the crash regs) and the pool base/end from the [poolx] log + allocator; discriminator = crash only when px>=2 and guest fault addr near pool end -> H-heap.
