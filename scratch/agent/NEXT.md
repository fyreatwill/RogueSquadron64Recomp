# NEXT (s7419)
HYPOTHESIS-ID: objdump-decode-blindspot

Class CB (CURRENT-TRUTH Next steps item 1). s7418 found mips64-elf-objdump prints `cache` as `.word`, so s7405's cache row was
a structural zero. tools/s7392_mesg_census.parse already re-decodes branch-likely words; nothing else is patched.
1. Per address, compare the objdump mnemonic (/tmp/s7418.dis; regenerate with
   `mips64-elf-objdump -d --no-show-raw-insn ../rogue_squadron64/build/roguesquadron.elf` if missing/older than the ELF)
   against the RecompiledFuncs disasm comment (`// 0xADDR: op`, rabbitizer). Beware overlays: key on (function name, addr).
   Table: op -> objdump-as-.word count, objdump-different-name count (aliases like move/or, li/addiu, b/beq are benign: list them).
2. `grep -l "s7392_mesg_census\|c7392.parse" tools/*.py` -> for each importer, the mnemonic sets it filters on; intersect with
   the blind set from 1.
3. Patch s7392 parse to decode the blind words (as it already does for BL), control = the 32 known live cache words at e.g.
   0x800934AC / 0x80018D88 come back as `cache`; re-run every affected census (s7400-s7405, s7418) and diff its rows/rc.
Hypotheses: H-clean (blind set = cache + branch-likely only, no other census row hidden) / H-blind (another op, or a census
row changes once decoded). Discriminator: the per-tool row diff after the parse patch, with the cache recovery as control.
Rerun tools/s7418_opcode_residue.py (rc 0 expected) after any parse change, since its liveness uses c7392.parse.
