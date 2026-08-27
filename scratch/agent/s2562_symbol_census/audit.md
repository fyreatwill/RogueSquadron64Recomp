# s2562 generated-symbol census: `0x80101CCC`

## Discriminator table

| Evidence | Result |
|---|---|
| Project symbol span | `fake_func_80101CCC`, VRAM `0x80101CCC`, size `0x4`; next entry `lv2_initializeObjectTracking` starts at `0x80101CD0`, so the span is complete. |
| Generated implementation | `RecompiledFuncs/funcs_43.c` contains one instruction: `lw $a0, 0x3C($v0)` at `0x80101CCC`; there is no prologue, return, or complete callable body. |
| Immediate previous entry | `lv1_checkComplexObjectives` at `0x80101C48`, size `0x84`, ends at `0x80101CCC`; its generated body has a normal `jr $ra` / delay-slot epilogue at `0x80101CC4` / `0x80101CC8`. |
| Immediate next entry | `lv2_initializeObjectTracking` at `0x80101CD0`, size `0x224`; its generated body starts with a normal stack prologue. |
| Companion symbol input | `mission_overlay.txt` retains `fake_func_80101CCC = 0x80101CCC` and states `// real function is lv2_initializeObjectTracking` for the following entry. It supplies no human name for the four-byte span. |
| Exact repository search | No `func_80101CCC`, human symbol, m2c definition, or source definition was found outside the active generated/project symbol entries. |
| Caller search | No generated or repository `jal`/symbol call site targets `0x80101CCC`; the span has no evidence of an independently callable function. |
| Local semantics | The lone load reads an object field into `$a0`; without a return or entry sequence it is an orphan instruction fragment, not enough to name a function. |

## Result

`H-data-or-boundary` / `H-no-match` selected. The placeholder remains unchanged.
This is a static, single-source boundary classification, not a reachability or
dead-code proof. The next unresolved generated placeholder in project-symbol
order is `0x80102A98`.
