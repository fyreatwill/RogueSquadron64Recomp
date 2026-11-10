# NEXT: owner reports first; otherwise RSPRecomp scalar-unit lowering census vs cxd4 su.c
HYPOTHESIS-ID: rsp-su-lowering-census
Context: s7092 closed the RSP vector unit (tools/s7092_vu_mem_test 0/8.59 G; tools/rsp_vu_diff 496/496 live).
The remaining RSP layer is how ../N64Recomp/RSPRecomp/src/rsp_recomp.cpp lowers SCALAR instructions into
build/factor5_ucode/*.c. Mnemonics used (s7092 census over the 3 compiled TUs): ori addiu lhu or jal mtc2 andi sll
bne addu beq lw lbu j sh mtc0 sw jr mfc0 sb mfc2 subu slt addi srl and lh lui sra negu blez bgtz sllv bgez bltz
xori sub srlv nor xor break add sltiu lb cfc2 b.
Hypotheses: H-su-ok (every lowering matches RSP semantics: 32-bit wrap, no overflow traps on add/addi/sub,
sign/zero extension of lh/lb/lhu/lbu incl. UNALIGNED scalar loads/stores (RSP allows them, byte loop), shift
amount masks &31, slt/sltiu signedness, mfc2/mtc2/cfc2 element byte order and e=15 wrap, branch delay slots,
jr/jal target masking to IMEM 0xFFC (and the link value), r0 never written) vs H-su-bad (a named op/operand
shape lowers differently; candidates: sltiu sign-extended immediate compared unsigned, mfc2 at odd e, cfc2 of
VCC/VCE packing, srlv/sllv mask, jal link = pc+8 & 0xFFF).
Unit (offline, one tool tools/s7093_su_census.py + a host test like tools/s7085_int_test):
1. Parse every RSPRecomp record ("// mnem ops" + C lines) in the 3 TUs; per mnemonic, classify the emitted C
   shape(s) and count sites (expect one shape per mnemonic per operand class; print any outlier).
2. For each shape, a host C test: the emitted expression vs a cxd4 su.c / vu MFC2/MTC2/CFC2 reference over
   exhaustive 16-bit immediates x random registers (and every DMEM address for the loads/stores, using the live
   RSP_MEM_* block like s7092 run.sh does).
3. Control flow: every jr/jal/j/b* target resolves to an existing label or the dispatch switch; delay-slot
   instruction emitted before the branch is taken (check order in each record).
Controls: positive = mutate one emitted shape in a copy (e.g. sltiu compare signed) and show the test flags it;
count control = per-mnemonic site totals equal the RSPRecomp instruction count of the fresh pass
(tools/ucode_regen.sh verify regenerates it).
Expected outcomes: 0 outliers / 0 diffs (closes the RSP scalar layer), or a named (op, operand shape) -> fix in
RSPRecomp or tools/fixup_factor5_ucode.py, `zsh tools/ucode_regen.sh snapshot`, L6 boot (`zsh scratch/s7089/run.zsh`).
