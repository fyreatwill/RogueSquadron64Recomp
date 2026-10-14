# M3 s4821 — indirect jump (jr non-ra / jalr) census

Tool: `tools/census_indirect_jump.py` (static, over `../N64Recomp/RecompiledFuncs/funcs_*.c`).

| Class | Count | Lowering | Verdict |
|---|---|---|---|
| `jr` jump-table (`switch (jr_addend_X >> 2)`) | 177 | every switch has `default: switch_error(...)` (177/177) | loud-fail, exact |
| `jr/jalr <reg>` non-zero, `LOOKUP_FUNC(ctx->rN)` | 113 call sites | `get_function(addr)`; unknown addr logs `Failed to find function` and exits (or stubs under `ROGUESQ_STUB_MISSING_FUNCS`) | loud-fail, never silent |
| `jr/jalr $zero` → `LOOKUP_FUNC(0)` | 114 sites | `get_function(0)` would abort | all inside data-decoded-as-code: audioCompandS16 82, data_gap_800CC3D4 15, static_3_800A2B50 10, static_3_800A29BC 3, static_3_800A2924 1, __OSGlobalIntMask 2, lvj_checkComplexObjectives 1 (proven dead s4819) |

Conclusion: an indirect jump can only fail by aborting with a printed address; no silent
mis-dispatch lowering exists. The `$zero` sites sit in the same data-as-code regions
as the s4820 ldl/ll-sc sites. Class closed. Evidence: census counts + `get_function`
source review (`overlays.cpp:644`). Reachability of the static_3_* symbols is
single-source (adjacency to audioCompandS16 data), not execution-checked.
