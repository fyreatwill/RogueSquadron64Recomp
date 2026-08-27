# s2549 generated-symbol census: `0x800C6968`

## Region table

| Region | Generated body | Companion evidence | Candidate | Result |
|---|---|---|---|---|
| `0x800C6968–0x800C696F` (8 bytes) | `addu sp,fp,zero`; `lw ra,0x24(sp)`; no `jr`, `jal`, branch, or complete callable body | `RecompiledFuncs/funcs_35.c`, `funcs.h`, and `recomp_overlays.inl` retain `fake_func_800C6968`; `rogue_squadron64/symbol_files/menu_overlay.txt` retains the same placeholder; exact-address, source, and caller searches found no human mapping | None defensible | `H-data-boundary` / `H-no-match`; unchanged |

## Evidence

The active overlay table gives the placeholder an 8-byte span at ROM offset
`0x21838`. The preceding named region ends at `0x800C6967`, while the next
named function, `loadJfifAsset`, begins at `0x800C6970` with a normal stack
prologue. The two instructions in the placeholder restore stack/return state
but do not return or transfer control, so treating them as an independent
game function or borrowing either neighboring name would be speculative.

No regeneration-safe rename was applied.

## Discriminator result

`H-named-match`: not selected; no exact companion name exists.

`H-no-match`: selected at static evidence scope.

`H-data-boundary`: selected as the best structural classification because the
span is an incomplete epilogue/setup fragment rather than a callable body.

`H-regeneration-risk`: not reached; there was no candidate to validate.

This is a static, single-source result. It does not prove the fragment is
dead or that the original binary never entered it.
