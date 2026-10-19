# M3 `$at` branch-join audit

Session 5560 (2026-10-19) audited the generated MIPS `$at` register (`ctx->r1`)
at every generated label with at least two incoming branch/jump edges.

## Measurement

Command:

```text
python3 tools/audit_at_branch_join.py /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs
```

The current tree contains 51 generated files, 2,502 functions, 9,966 generated
`ctx->r1` writes, and 23,641 generated `ctx->r1` references. The comment-level
positive control also sees 19,259 `$at` uses and 9,999 `$at` destination writes.
There are 2,681 multi-predecessor joins, 413 of which touch `$at`. The audit
therefore did not silently miss the register or all join sites.

The two explicit controls behaved as expected: `loadOverlay` has an ordinary
multi-predecessor join (one join, no `$at` dependency), while the known
`fake_func_800B75C4` data-gap fragment has no join. `audioMixStereoBlock8`
remains an ordinary no-join return control with two `ctx->r1` writes.

## Candidates and classification

The 25 candidates below are the complete output. A candidate means the first
`$at` use in the 12-comment post-join window precedes a local `$at` destination
write; it is not by itself a reachable value-loss proof.

| generated record | join | first use | classification |
|---|---|---|---|
| `data_gap_80099FDC` | `L_8009A008` | `0x8009A00C lw $a0, 0x30($at)` | invalid/data gap |
| `audioCompandS16` | `L_800A2DF0`, `L_800A2DF4`, `L_800A2E08` | `0x800A2E18 .word` | invalid/data gap |
| `audioCompandS16` | `L_8009EDE0`, `L_8009F4D0`, `L_8009FB0C`, `L_800A09E4`, `L_800A323C`, `L_8008BFE4` | `$at` in decoded fragment | malformed fragment |
| `audioCompandS16` | `L_800A2C68`, `L_800A2A04`, `L_800A2148`, `L_800A3354`, `L_800A2BE0` | `.word`/special decode | invalid/data gap |
| `data_gap_800CC3D4` | `L_800CD328` | `0x800CD354 addi` | invalid/data gap |
| `lvj_checkComplexObjectives` | `L_80109900` | `0x80109914 lwc1` | malformed fragment |
| `static_3_800A2FE4` | `L_80089EDC`, `L_800A2BE0`, `L_8008BFE4`, `L_80083868`, `L_8008ADEC` | `.word`/invalid decode | invalid/data gap |
| `data_gap_80024A0C` | `L_80025734`, `L_800257D8` | `lw ...($at)` | invalid/data gap |
| `__OSGlobalIntMask` | `L_8003B398` | `.word INVALID` | invalid/data gap |

The independent fixup evidence agrees with this classification: the current
N64Recomp fixup log records 214 trapped cross-function gotos for
`audioCompandS16`, 36 for `lvj_checkComplexObjectives`, and a neutered
`fake_func_800CC3D4`; the companion symbol source explicitly labels the data
gap records. The generated source itself contains the `.word`, `INVALID`, and
`InstrIdType` markers at the remaining candidates. No ordinary reachable
function has a `$at` join value-loss candidate.

## Verdict

H3 wins: the apparent hazards are invalid/data-gap or cross-function fragment
material. H1/H2 remain unevidenced for reachable code; no patch, guard, or
runtime build is authorized. This closes the `$at`/`r1` branch-join class under
the current generated tree. Reopen only with a new recompiler/provenance
source or a candidate in an ordinary complete function.
