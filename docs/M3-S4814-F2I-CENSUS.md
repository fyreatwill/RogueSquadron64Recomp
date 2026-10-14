# M3 s4814 — float-to-int conversion idiom census

Tool: `tools/census_f2i.py` over RecompiledFuncs (1212 sites in `funcs_*.c`).

| macro | sites | feeds ADD32/MEM within 6+6 lines (heuristic) | direct store | other |
|---|---|---|---|---|
| TRUNC_W_S | 1171 | 519 | 21 | 631 |
| TRUNC_W_D | 28 | 4 | 0 | 24 |
| CVT_W_S | 13 | 3 | 0 | 8 |
| CVT_W_D | 2 | 0 | 0 | 2 |

TRUNC_L_*/CVT_L_* : 0 sites. The "addr" column is a loose upper bound (any ADD32/MEM_ use of the moved GPR).

## Semantics
`TRUNC_W_*` = C cast `(int32_t)(float|double)`; `CVT_W_*` = `lrintf/lrint` cast to int32 (recomp.h:350-392).
For out-of-range or NaN input C says UB. On arm64 the cast lowers to `fcvtzs` (saturating, NaN->0, no trap);
`lrintf` on macOS arm64 does not trap either. Real R4300i raises Unimplemented-Operation for these inputs, so
retail never reaches them: any NaN/overflow input here is already a corrupted-state symptom, not a legitimate path.

## Verdict
Class closed on arm64: the conversion cannot fault; it only yields a deterministic saturated value. No guard added —
a guard would mask the upstream writer of the NaN/huge float, not fix it. Caveat: x86 hosts get INT_MIN
(cvttss2si) instead of saturate/0, so an x86 build could diverge; single-source (instruction-set reasoning, no
hit counter, no compile-time-constant scan).
