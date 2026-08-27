# s2576 generated-symbol census: `0x80109428`

| Field | Evidence | Result |
|---|---|---|
| Generated span | `funcs_49.c` contains `fake_func_80109428` at `0x80109428`; its body is `c.lt.s $f0,$f2` at `0x80109428` plus the `nop` delay slot at `0x8010942C`. | Complete 8-byte ROM entry, but only one meaningful instruction and no callable body. |
| Preceding neighbor | `triggerObjectiveVoiceLineOnce` ends at `0x80109424` with the stack restore. | Target is separated from the prior complete function. |
| Following neighbor | `lvk_checkComplexObjectives` begins at `0x80109430` with its stack prologue. | Target is a boundary fragment immediately before a named function. |
| Companion symbol entry | `fake_func_80109428 = 0x80109428`; the companion comment says `real function is lvk_checkComplexObjectives`. | Companion retains the placeholder and identifies the following real function; it supplies no human name for the fragment. |
| Active generated tables | `funcs.h` and `recomp_overlays.inl` both retain `fake_func_80109428`. | No existing project mapping to reuse. |
| Exact/source/m2c/caller searches | Searches for `80109428` / `fake_func_80109428` / matching source and m2c material found only the generated declaration/body, overlay entry, syms entry, and companion placeholder. | No independent candidate. |
| Semantic candidate | A lone floating-point compare cannot be named as an independent callable function; assigning `lvk_checkComplexObjectives` would absorb an instruction fragment into its neighbor. | No defensible rename. |

## Decision

Selected `H-data-or-boundary`. The placeholder remains unchanged. This is a
static, single-source boundary classification; it does not prove reachability
or explain why the fragment is represented separately. The next unresolved
placeholder in this region is `0x80109618`.
