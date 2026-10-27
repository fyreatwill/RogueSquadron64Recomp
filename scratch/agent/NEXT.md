# NEXT: why is the span grid saturated at -128 at dd4? log pre-clamp operands in streamTerrainGridCellsByDistance
HYPOTHESIS-ID: g1c-span-reject-predicate

s6526: rejected dd4 cells have populated recs (rec[3]~-38); span operand is -128 (clamp floor). Recs are file data, not the problem.
Hypotheses: H-overshoot (pre-clamp value legitimately huge-negative because the dd4 distance term is unscaled -> scale the formula input), H-wrong-operand (f12/f10 clamp bounds or f0 derive from a stale/uninitialised float at x>=32), H-by-design (retail clamps far cells to -128 = deliberately empty).
Discriminator (one build, one run, dd1 vs dd4 pinned lvl1, tools/apply_s6522_clampprobe.py is the base): log pre-clamp f0, f12, f10, row/layer/x at 0x80042820 and 0x800426D8 for the first N saturating stores keys>=745, plus 6 non-saturating stores as positive control. If f0 is hugely negative and tracks distance*dd -> H-overshoot (scale input in fixup). If bounds f12/f10 are garbage -> H-wrong-operand.
