# NEXT (s7317): spill-pointer holders — the struct-field edge of the s7316 bound class
HYPOTHESIS-ID: spill-holder-field-compare
Context: s7315 (lui constants) and s7316 (global data words) closed H-clean. Remaining edge: a bound or pointer compare made on
an object FIELD (register base), which neither tool follows. Start from runtime fact, not a grep: s7316 dumps showed 80-87 heap
words holding 0x81xxxxxx spill pointers (scratch/s7316/spill_words.txt, addr=value per dump; heap at OSMEM 12, L1 dd2 16:9).
1. Name the owners: re-run the s7316 recipe (PORTING-STATE s7316 "Run" line) with ROGUESQ_RDRAM_DUMP_DIR plus the spill
   event ring/malloc ra (s6893 ring in src/main/upstream_compat.cpp; [spill] req lines carry no ra -> add ra to the log line
   if needed, one build). Map each holder word to its enclosing heap block (walk the rs_malloc chain from 0x8010FF18 in the
   dump: 0x10-byte headers, size at +4) and the allocating caller's ra for both the holder block and the spill block.
2. For each owner type (distinct allocator ra), read the retail functions that load that field (lw at the same offset from the
   owner pointer) and classify any slt/sltu/mask on it. H-reject (a field compare rejects/misorders a 0x81 pointer) vs H-clean.
3. Discriminator for any H-reject site: same binary, dd2 vs dd1 log of that branch outcome (dd1 has no spill).
If no owner is nameable in one iteration, fall back to CURRENT-TRUTH Next steps 16.
