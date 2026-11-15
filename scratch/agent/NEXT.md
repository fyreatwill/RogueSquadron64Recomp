# NEXT (s7408)
HYPOTHESIS-ID: fp-int-conversion-contract

s7407 closed class BQ (H-equal: no libm replaced; 4 live IDO 64-bit helpers bit-identical, tools/s7407_libm_census.py).
Class BR: recompiler FP->int conversion macros, lib/N64ModernRuntime/N64Recomp/include/recomp.h:395-450.
TRUNC_W_S/D, TRUNC_L_S/D are plain C casts (UB out of range; arm64 fcvtzs saturates, NaN -> 0); CVT_W_S/D = (int32_t)lrintf /
lrint (64-bit long truncated -> WRAPS out of int32 range); CVT_L_S has a stray ';' in its macro. VR4300: out-of-range/NaN/inf
conversion raises an unimplemented-operation exception (retail fault), in-range follows FCSR RM (nearest; s7405 RM rows H-none).
1. Offline (one script tools/s7408_cvt_contract.py + generated C harness, like s7407): every 2^32 float through each .s macro
   (and a dense double sweep for .d) vs a VR4300 model {in-range: RM-nearest / trunc result; else UNIMPL}. Rows: equal, UNIMPL
   (retail faults, record host value: saturate vs wrap), mismatch in range (must be 0). Control: perturbed macro (+1) mismatches.
2. Census: grep RecompiledFuncs for every TRUNC_*/CVT_W_*/CVT_L_* site (count, function); join with BP's build_fpat IOC=0
   (route stmts) - any site outside the BP route that can see |x|>=2^31 (e.g. float from a guest-derived distance) is a row.
3. Hypotheses: H-equal (in-range identical, out-of-range unreachable live), H-wrap-live (a live CVT_W site receives |x|>=2^31
   and the host wraps where arm64 cast would saturate -> pick saturation behind default-on flag, =0 old), H-macro-bug (the CVT_L_S
   stray ';' changes an expression at some emit site -> fix in fixup or recomp.h with export.sh).
