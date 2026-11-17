# NEXT (s7509)
HYPOTHESIS-ID: ff-rsprecomp-vector-operands

Context: FD (s7507, control flow) and FE (s7508, scalar unit; s7093 + tools/s7508_rsp_scalar_gaps.py) are CLOSED H-equal. Already
covered for the vector side: s7092 (vector DMEM fast paths vs ares byte loops, VRCP/VRSQ vs cxd4; rsp_vu_diff SIMD==SISD) and s7091
(live text == pristine generator text). NOT covered: whether RSPRecomp's OPERAND EXTRACTION for vector ops matches the ROM bits. It
uses rabbitizer accessors (GetRsp_vd/vs/vt, GetRsp_elementhigh vs elementlow chosen by hasOperand, GetRsp_de()&7, the Imm7 sign
extension `((int8_t)(imm << 1)) >> 1`, VtIndex/VsIndex for ltv/stv/vrndn/vrndp, rt/rs for mfc2/mtc2/cfc2/ctc2), and then
rsp_vu*.hpp scales the offset by access size inside RSP::LQV/LDV/... . A rabbitizer field slip would be invisible to s7091 (same
generator both sides) and to s7092 (implementations only).

Work unit: class FF, one offline tool tools/s7509_rsp_vec_operands.py (reuse s7508's live walk: import tools/s7508_rsp_scalar_gaps.py
audit()/words_for() and cf.segments, so splices + slot copies are covered).
 V1 per live record of main/B/boot whose ROM word is cop2 vector (op 18, rs&16), lwc2 (op 50) or swc2 (op 58): independent decode
    (computational: e=bits 21-24, vt=16-20, vs=11-15, vd=6-10, funct=0-5; lwc2/swc2: base=21-25, vt=16-20, opcode=11-15
    (lbv0 lsv1 llv2 ldv3 lqv4 lrv5 lpv6 luv7 lhv8 lfv9 lwv10 ltv11), element=7-10, offset=sign-ext bits 0-6; vrcp/vrsq/vmov family:
    de=vs field) -> the exact expected `rsp.NAME<e>(args);` line from the vector_operands table order in rsp_recomp.cpp; compare.
 V2 offset scaling: grep rsp_vu*.hpp for each LxV/SxV and check offset is multiplied by the right size (lbv 1, lsv 2, llv 4, ldv 8,
    lqv/lrv/lpv/luv/lhv/lfv/ltv/stv/swv 16) — compile one call each with a probe base and read back the DMEM address touched.
 V3 controls: flip the e bits of one spliced vector word; swap vs/vt in one live line; drop the Imm7 sign (use 0x7F mask) on one
    negative-offset lqv; each must flag.
Hypotheses: H-equal (0 defects) / H-dead (defect only in records no compiled path executes, e.g. after a never-taken overlay route) /
H-live (a compiled vector site has a wrong operand -> fix in rsp_recomp.cpp (../N64Recomp, commit there) or rsp_vu*.hpp (lib/:
export.sh + commit), regen via tools/ucode_regen.sh, rerun s7507/s7508/s7509 + s7091 census, build, one L4 300 s hold, one frame vs
angrylion).
Discriminating outcome: V1/V2 defect list split by compiled-site use. No game run unless H-live.
After FF: RSP generator classes are exhausted; take CURRENT-TRUTH item 21 (next ITERATION.md 3c rung or a new guest idiom-class audit).
