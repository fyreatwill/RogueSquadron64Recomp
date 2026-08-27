# s2565 generated-symbol census: `0x80103D08`

## Discriminator table

| Field | Result |
|---|---|
| Project/generated span | `0x80103D08–0x80103D0F`, 8 bytes; `fake_func_80103D08` in the project symbol input and generated declaration, implementation, and overlay table |
| Instructions | `lui a1, 0x8010`; `addiu a1, a1, -0x6C50`, yielding `a1 = 0x800F93B0` |
| Preceding symbol | `lv4_calculateFriendliesSaved`, `0x80103CC4–0x80103D07` |
| Following symbol | `lv5_initializeObjectTracking`, `0x80103D10–0x80103E5B` |
| Companion symbol result | `fake_func_80103D08 = 0x80103D08`; the companion comment identifies the following real function as `lv5_initializeObjectTracking` |
| Exact-address/source/m2c/caller search | No named symbol, source definition, m2c definition, or independent caller at `0x80103D08`; repository hits are the placeholder/table entries and this audit |
| Local semantics | A two-instruction constant-load fragment with no callable prologue, return, call, or visible consumer within the span. It is not sufficient to name as a function or assert a `lv5` preamble |
| Selection | `H-data-or-boundary` / `H-no-match`; leave placeholder unchanged |

## Evidence boundary

This is a static, single-source classification. It does not prove whether the
fragment is reachable or whether the loaded constant participates in the
following function through a representation artifact. No generated code,
runtime behavior, or mitigation changed.

ORIGIN: diagnostic-only. No writer or legitimacy claim applies.
