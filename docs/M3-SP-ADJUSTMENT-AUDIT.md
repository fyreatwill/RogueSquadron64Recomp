# M3 audit: `$sp` adjustment balance (s5558)

Class: generated MIPS `$sp` frame adjustments represented as
`ctx->r29 = ADD32(ctx->r29, ...)`. Risk: a reachable path applies a frame
adjustment without the matching restore, leaving later stack accesses at the
wrong address.

## Census

The whole generated tree (`../N64Recomp/RecompiledFuncs/funcs_*.c`, 51 files)
contains 2,502 `RECOMP_FUNC` bodies and 1,751 bodies containing at least one
self-adjustment. The two syntactic controls were 4,849 generated comments for
original `addiu $sp, $sp, imm` instructions and 4,854 generated
`ctx->r29 = ADD32(ctx->r29, imm)` assignments.

The five-assignment difference is the existing early-return guard epilogues in
`funcs_3.c:1748,1756`, `funcs_15.c:5710,5736`, and `funcs_25.c:5483`; each is
a hand-added return path and the corresponding original epilogue remains in
the function. This was checked before balance classification.

Raw summation is not valid because N64Recomp emits the delay-slot instruction
both before `return;` and again after it. Collapsing adjacent duplicate numeric
adjustments gives 1,727 balanced functions and 24 nonzero candidates. The
positive control is a normal frame pair such as `initPlayerCraftMovementMode`
(`-0x20`, `+0x20`, with the delay-slot duplicate collapsed).

## Candidate classification

| Candidate group | Count | Result |
|---|---:|---|
| Non-returning service/worker loops | 8 | Intentional: `siServiceThread`, `mainEventQueueWorker`, `piDmaWorker`, `hudDisplayUpdateWorker`, `saveServiceWorker`, `tickFormatMessageWorker`, `tickSongAssetLoadWorker`, `mainGameLoop` loop instead of executing an epilogue. |
| Invalid/data-gap or fragment entries | 12 | Not callable frame bodies: `data_gap_80024A0C`, `data_gap_8004661C`, `data_gap_8006F4AC`, `data_gap_80093E74`, `data_gap_80097D58`, `data_gap_800C64A4`, `data_gap_8010721C`, `static_3_80007064`, `static_3_80029270`, `static_3_80045024`, `static_4_800E9B10`, `static_4_80106C50`. |
| Invalid/trap tail or synthetic gap | 3 | `audioCompandS16`, `lvj_checkComplexObjectives`, and `duplicateSymbolPrefixForApplyCraftAnimAndDetailParams` have the adjustment inside invalid/trap or synthetic placeholder material; no normal prologue-to-return path exists. |
| Positive-only invalid stream | 1 | `__OSGlobalIntMask` is an invalid instruction stream with an embedded adjustment, not a normal callable frame. |

The 24 candidates therefore contain no reachable ordinary function with an
unmatched `$sp` adjustment. No guard or runtime change is authorized.

## Verdict

H3 selected: the raw candidates are generated control-flow/data-fragment
artifacts and intentional non-returning workers, not a live `$sp` imbalance.
This closes this idiom class for the current generated tree. Re-open only if a
new backtrace identifies one of these bodies on a return path, or regeneration
changes the normalized census.
