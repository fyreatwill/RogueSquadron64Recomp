# NEXT (s7318): class B field-order compares vs live spill pointers — runtime cross-block check
HYPOTHESIS-ID: spill-holder-field-compare
Context: s7317 named the live spill holders (dd8 21:9 L4: up to 120 live spill blocks, 2747 holder words, 42 owner types) and closed
the top-byte-shift form (32 sites, spill-equal). Open: 182 sites where a word loaded from a holder-field offset (register base) is
ordered (slt/sltu) against a non-constant register (scratch/s7317/field_census.txt "  B" lines; inflate_codes_recomp 17,
loadDatFile 10, inflate_blocks 10, _Genld 8, ...). Static pass cannot tell if the other operand is in the same block.
Hypotheses: H-same (every B compare that sees a spill pointer compares it with a pointer into the SAME block or the same arena
-> order is the retail order) vs H-cross (some B site orders a spill pointer against a heap pointer / pool bound -> its result can
differ from retail's all-heap order) vs H-scalar (the loaded field is never a pointer at these sites at runtime).
Unit:
1. New tools/apply_s7318_bcmp_probe.py (fixup, RS64_REPLAY registration per docs/REGEN-VERIFY.md, env ROGUESQ_S7318_BCMP=1 only):
   before each of the 182 slt/sltu sites (generate the list from tools/s7317_field_compare_census.py), call
   rs64_s7318_bcmp(pc, a, b). C++: classify per pc: both scalar / one spill (is the other in the same live spill block? same arena?
   a heap pointer?) / heap-heap; count per pc, first 4 examples per pc for cross cases. Dump the table at exit / every 1200 swaps.
   Use the s7317 allocation map (ROGUESQ_S7317_ALLOCMAP=1) for the block lookup.
2. Positive control in the same run: ROGUESQ_S7318_BCMP_CTL=<pc> forces operand a to 0x81000040 at one site with a heap other
   operand -> must log a cross case.
3. Run the s7317 run-B recipe (LEVEL=4 dd8 21:9, g1_level_coverage_common, HOLD_S=150). Rebuild needs only RecompiledFuncs+main.
Outcomes: 0 cross cases with the control firing -> H-same/H-scalar, class B closed, the struct-field edge closed. Any cross pc ->
read that function, name the compare's meaning, decide whether retail order is required (fix: allocate that owner type outside
the spill arena, or map the compare).
If the probe can't be built in one iteration, fall back to CURRENT-TRUTH Next steps 16.
