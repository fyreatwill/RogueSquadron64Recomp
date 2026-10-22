# NEXT (s5905): what separates RET-producing obj class 0x80330c5c from non-RET 0x80323f58

HYPOTHESIS-ID: g1-mission-progression

s5904: 172/176 RETs come from in-sphere objs with vtable w0 in {80330c5c, 80331158, 803311cc}; 80323f58 has 654 in-sphere events and ~0 RETs. RET is class-gated (H-nested).

Hypotheses:
- H-flag: a per-obj flag/team word (offset in the 0x100 dump of [own40]) differs between the classes and is tested after the sphere hit.
- H-vtbl: the post-sphere code calls a virtual method (vtable 80330c5c+off) that returns hit only for target classes.
- H-target: 80330c5c objs ARE enemies/targets and 80323f58 are scenery/own-team; RET then works and the mission goal gate lies later (check whether RET leads to damage/kill counter).

Discriminator (static first): disassemble the caller of intersectSegmentWithObjectSphere in the bolt loop (RecompiledFuncs, around rs5834_post/`hit` computation) and the funcs at vtable 0x80330c5c entries; list the predicate. Then one run dumping w0..0x40 of one 80330c5c vs one 80323f58 obj for diff (positive control: the two dumps differ in w0).
