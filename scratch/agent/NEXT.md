# NEXT: locate the REAL slot-state halfword (two wrong addresses so far: 0x137F24, 0x137F3C are craft float data)
Work unit (offline, no game run): find the generated-code reader that tests the slot state bits 0x8/0x10 (the non-health fail check, s5733) - grep build/ generated funcs for `& 0X8`/`0X10` after an LHU near the slotDispatcherIter / requestMissionTransitionMode path; read the exact base register + offset chain, compute the RDRAM address with a worked example from a live register dump if needed.
Discriminator: address whose writers are NOT computeCraftSelectTurnFromInput / playerXwingInit float stores. Then queue a slotwatch soak with that address AND lives control (wp4 0x130B10); a run is void if lives never decrements.
HYPOTHESIS-ID: g1-nonhealth-fail
