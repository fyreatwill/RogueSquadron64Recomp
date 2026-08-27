# Session 2542 symbol census — `0x800AAADC`

## Region table

| Placeholder | Complete span | Generated body | Evidence | Result |
|---|---|---|---|---|
| `fake_func_800AAADC` | `0x800AAADC–0x800AAADF` (4 bytes) | `sh $a0, 0x1A($v1)` | Companion `mission_overlay.txt` retains the fake name; next named symbol is `playerSnowSpeederInit = 0x800AAAE0`. Active TOML, generated declaration, implementation, and overlay table agree on the 4-byte span. Exact-address/source/m2c/caller searches found no human candidate. | `H-data-boundary` / `H-no-match`; unchanged |

## Decision

The fragment has no prologue, return, jump, or complete callable body.
Renaming it to `playerSnowSpeederInit` would absorb the next function, while
inventing a semantic name for one store is unsupported. This is a static,
single-source result; no generated code or symbol input changed. The next
sweep region is `0x800AD378`.
