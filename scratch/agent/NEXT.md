# NEXT (s7323): address-derived table index, class F
HYPOTHESIS-ID: spill-addr-index
Context: s7322 closed class E (KSEG re-tags: 404 sites, 0 H-alias). Classes A-E cover the spill pointer as a value: top byte, order,
difference, truncation and re-tag. One shape is still open: the pointer used as an INDEX. Code like `(p & 0x1FFFFFFF) >> k`,
`(p - 0x80000000) >> k`, `(p << 3) >> (3+k)` or `p >> k` with 8 <= k < 23, then scaled and added to a table base, indexes a page table,
bitmap or bucket array sized for 4/8 MB of RDRAM. A spill pointer 0x81xxxxxx gives an index past the end of an 8 MB table, so the
write lands in whatever follows the table. With an `andi`/`and` bound before the add (a hash), it is safe.
Hypotheses: H-none (no such index), H-bounded (every one is masked or range-checked, or its source is never a heap pointer) vs
H-overflow (an unbounded address-derived index whose source can be spill: name the table and its size, fix it with the PTRMASK pattern).
Unit:
1. Class F in tools/s7317_field_compare_census.py: srl/sra by 8..22 (or a phys-mask/subtract of 0x80000000 then shift) of a non-constant;
   follow d through sll/addu up to a memory BASE use or `addu` with a constant base (G list). Record bounded (andi/and/sltiu/bound
   compare on the path) or unbounded, the source provenance (holder field / word / arg) and the table base. Planted selftest: positive
   `lw a0,0x10($s1); srl v0,a0,12; sll v0,v0,2; lui at,0x8013; addu at,at,v0; lw t0,0x40($at)` listed unbounded; negative with
   `andi v0,v0,0x3FF` before the sll listed bounded.
2. Classify. Unbounded sites with pointer-shaped sources: hook them into the s7318 classifier (idx 768+, table 768 -> 1024 in
   src/main/upstream_compat.cpp) as (source, 0x80000000) and run ONE dd8 21:9 L4 flight with ctl ROGUESQ_S7318_BCMP_CTL=800173C0
   (per frame in flight, s7321).
3. Any H-overflow: name the table, its size and what follows it; fix; two-arm qualify.
Outcomes: 0 unbounded spill sources -> the spill-pointer audit family closes (A-F); then CURRENT-TRUTH 18.
