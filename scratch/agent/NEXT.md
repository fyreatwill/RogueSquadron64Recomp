# NEXT (s7320): spill-pointer DIFFERENCE class — census subu over holder-offset fields, classify every site
HYPOTHESIS-ID: spill-holder-pointer-diff
Context: s7317-s7319 closed the ordering edge (class A top-byte shifts, class B 182 slt/sltu: 0 cross). The sibling idiom is a
difference: `subu d, p, q` (or addu with a negated value) where p is a load from a holder offset (scratch/s7317/d8_holders_all.txt.gz,
offsets of words that held live spill pointers in dd8 21:9 L4 flight) and q is a pointer from another allocation or a heap bound.
Spill (0x81000000+) minus heap (0x80xxxxxx) is >= 8 MB: any size/limit check on d (sltiu/slt vs a constant, used as a length) would
then fail where retail passes.
Hypotheses: H-same (p and q in the same object: d is an in-object length, base-invariant) vs H-scalar (p is never a pointer at that
site) vs H-cross (q from another allocation: d is wrong under spill -> defect candidate).
Unit:
1. Extend tools/s7317_field_compare_census.py with a class C detector (subu of a holder-offset load against a non-constant register,
   record what consumes d: compare-with-constant / length arg / store) + a planted selftest snippet (positive control). One run over
   d8_holders_all.txt.gz; write tools/s7320_bdiff_sites.txt.
2. Classify every site statically with the s7319 signature approach (tools/s7319_bcmp_static_class.py as the model). If more than ~40
   sites stay unclear, add them to the s7318 runtime hook (apply_s7318_bcmp_probe.py: hook subu sites, class cross = one operand spill
   and the other 0x80xxxxxx) and run ONE dd8 21:9 L4 flight with the control at a known hh site.
3. Any H-cross site: read the function, name what d means, fix (allocate that owner outside the spill arena or correct the length),
   two-arm qualified.
Outcomes: all scalar/same -> class C closed, spill-pointer edge fully closed; take CURRENT-TRUTH 17 (next ladder rung).
