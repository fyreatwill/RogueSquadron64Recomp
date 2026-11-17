# NEXT (s7508)
HYPOTHESIS-ID: fe-rsprecomp-scalar

Context: s7507 closed FD (RSPRecomp control flow, H-equal, tools/s7507_rsp_ctrl_flow.py rc 0). The RSP scalar unit lowering was never
audited against a model: rsp_recomp.cpp process_instruction cases add addi addiu addu and andi lb lbu lh lhu lui lw negu nop nor or ori
sll sllv slt slti sltiu sltu sra srav srl srlv sub subu xor xori sb sh sw (+ mfc0/mtc0 actions), and the librecomp/include/librecomp/rsp.hpp
macros they expand to (RSP_ADD32/RSP_SUB32/RSP_SIGNED, RSP_MEM_{W,H,HU}_LOAD/STORE, RSP_MEM_B/BU, and the fast paths rs64_dmem_w/h with the
`(a ^ 2) & 0xFFE` halfword swizzle, alignment-gated by rs64_g1e_dmem).

Work unit: class FE = the s7412/s7413 shape for the RSP side. One offline tool tools/s7508_rsp_scalar.py:
 E1 census: every scalar op in the 3 COMPILED images (main gfx incl. the 9 spliced overlay streams, ucode B, boot) - decode from ROM
    (reuse s7507 load_instrs/tomls), map to the emitted C line (reuse s7507 segments/walk alignment), and check each line == the expected
    template for op/regs/imm (sign- vs zero-extended imm: andi/ori/xori zero, addiu/slti/sltiu sign; sltiu compares UNSIGNED against the
    sign-extended imm incl. rs=$zero - the s7093 fix; shifts by sa vs rs&31; lui << 16; r0 writes discarded).
 E2 semantics: compile every distinct emitted template with rsp.hpp (cc, the real header, rs64_g1e_dmem both 0 and 1) and drive it over
    32-bit edge values vs a Python MIPS32/RSP model; DMEM ops over addresses 0xFF8..0x1007 wrap (12-bit), unaligned w/h (the RSP allows
    them), sign/zero extension, and the fast-path vs slow-path result equality.
 E3 controls: mutants (zero-ext addiu, signed sltiu, sra->srl, missing &31 on srav, halfword swizzle ^0, no 0xFFF wrap) must each flag.
Hypotheses: H-equal (0 defects) / H-dead (defect only in a template no compiled image uses) / H-live (a compiled site lowers wrongly ->
fix in rsp_recomp.cpp or rsp.hpp (lib/: export.sh + commit), regen via tools/ucode_regen.sh, rerun s7507 + s7508 + s7091 census, build,
one L4 300 s hold, RDP stream vs angrylion on one frame).
Discriminating outcome: E1/E2 defect list split by compiled-site use count. No game run unless H-live.
