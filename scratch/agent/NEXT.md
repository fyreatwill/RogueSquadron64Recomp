# NEXT (s7322): KSEG re-tag class E — pointers rebuilt from a narrowed value
HYPOTHESIS-ID: spill-pointer-retag
Context: s7321 closed class D (24-bit masks, 0 H-alias). Its one real alias shape (commitMeshDrawBatchRefs `(ref & 0xFFFFFF) | 0x80000000`)
showed the general idiom: a pointer narrowed somewhere (packed into 24 bits, stored as a 16-bit half or index, kept as an offset from a
base) and later RE-TAGGED into a KSEG0 pointer. Any re-tag that does not restore bit 24 maps a spill pointer 0x81xxxxxx onto heap.
Shapes: `or/addu d, x, R` with R = constant 0x80000000 (lui 0x8000), `lui d, 0x80xx ; or/addu d, d, x` where x has <= 24 significant
bits (andi/lhu/srl source), `addu d, x, 0x80000000`, and PHYS_TO_K0 helpers (osPhysicalToVirtual).
Hypotheses: H-safe (every re-tag source was never a spill pointer: physical addresses from hardware/DMA, ROM offsets) vs H-paired
(re-tag consumes a class-D packed value; already covered by the D producers) vs H-alias (a re-tag rebuilds a pointer whose original was
spill -> silent heap alias; fix the packing or keep the owner out of spill).
Unit:
1. Class E in tools/s7317_field_compare_census.py: a register holding constant 0x80000000 (or any 0x80xx0000 lui) combined by or/addu
   with a non-constant; record the other operand's provenance (andi/lhu/srl/and-mask/field load) and first 4 consumers. Planted selftest
   (positive: `lui 0x8000; or a0, v0, t4` after `and v0, v1, 0xFFFFFF` listed with provenance class-D; negative: `lui 0x8000; addu`
   with a full-width pointer source NOT counted as narrowed).
2. Classify. Pair each narrowed re-tag with its producer. Hook the unpaired producers into the s7318 classifier (idx 640+) and run ONE dd8
   21:9 L4 flight, ctl ROGUESQ_S7318_BCMP_CTL=800173C0 (proven per-frame in flight, s7321).
3. Any H-alias: name the owner and placement, fix, two-arm qualify.
Fold first: SOAK-RESULTS line for s7321_trunc_levels (L1/L12 class-D coverage; exit 1 = a class-D cross, reopen item 16).
Outcomes: all safe/paired -> spill-pointer audit family closed; take CURRENT-TRUTH 18.
