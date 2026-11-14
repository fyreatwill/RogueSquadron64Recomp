# NEXT (s7321): 24-bit truncation class over holder pointers — census, classify every site
HYPOTHESIS-ID: spill-holder-pointer-trunc
Context: s7317-s7320 closed the holder-field edge for order (class B), top byte (A) and difference (C), 0 cross. The remaining idiom
on the same holder set is TRUNCATION: the spill arena starts at 0x81000000, and 0x81000000 & 0x00FFFFFF = 0 (also & 0x007FFFFF,
& 0x003FFFFF alias low RAM). A heap pointer 0x80xxxxxx masked to 24 bits is its physical address and works; a spill pointer masked the
same way points into the bottom of RDRAM. 0x1FFFFFFF (K0_TO_PHYS) is safe up to 512 MB. Shapes: `and/andi d, p, M` with M a 24/23/22-bit
low mask (M built by lui/ori), `sll d, p, 8 ; srl d, d, 8`, and `lui 0x00FF ; ori 0xFFFF ; and` feeding a segment/DMA/RSP address store.
Hypotheses: H-safe (every such site masks with >= 29 bits or the operand is scalar) vs H-scalar (field never a pointer there) vs
H-alias (a holder pointer is truncated to < 25 bits -> a spill pointer would alias physical 0 -> defect candidate, fix or prove the
owner never lands in spill).
Unit:
1. Add class D to tools/s7317_field_compare_census.py: holder-field load -> and/andi with a constant mask < 0x01FFFFFF, or sll k / srl k
   with k >= 7 on the same value; record the mask bits and the consumers. Planted selftest (positive control: field & 0x00FFFFFF listed,
   field & 0x1FFFFFFF NOT listed). Whole-program variant too (any register, not just holder fields) as a second count for context.
2. Classify. If > ~40 sites unclear, hook them into the s7318 classifier (new class idx 512+: count inputs in spill range = "alias"),
   ONE dd8 21:9 L4 flight, control = synthetic spill substitution at a hot heap site (like ROGUESQ_S7318_BCMP_CTL).
3. Any H-alias site with a spill input: name the consumer (DMA/segment/RSP), fix the owner placement or the mask, two-arm qualified.
Outcomes: all safe/scalar -> spill-pointer class fully closed; take CURRENT-TRUTH 17 (next ladder rung / new idiom audit).
