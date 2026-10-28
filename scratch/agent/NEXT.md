# NEXT: lift the cell cap safely (why does POOLX fault on a NULL list node?)
HYPOTHESIS-ID: g1c-dd-phase2
Fact (s6577): at dd6 the cap (2048 on 64x64, 400 on 32x32) trims the ddclamp window below the level extent in ~55% of samples (lvl1/5/10). So the cap is a real lever; extent is not the only limit.
Hypotheses: H-uninit (extra pool entries never linked) vs H-fixedarr (retail-sized parallel array read past end) vs H-clamp.
Work unit: with the s6549 recipe (dd4 lvl1 POOLX=2), find the allocation/array sized by cap at 0x80130C4C and check whether sibling arrays keep retail size (grep the allocator for the cap constant); if so, scale them with the cap. Positive control: px1 clean, px2 faults at 0x80011524.
