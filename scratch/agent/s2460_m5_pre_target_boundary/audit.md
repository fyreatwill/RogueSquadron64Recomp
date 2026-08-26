# s2460 M5 pre-target dispatch boundary audit

Date: 2026-08-26

Scope: generated call/return idioms leading to the two qualified-run failure
breadcrumbs. Static evidence only; no behavior or dispatch code was changed.

| Site | Path and continuation | Resolver/termination edge | Result |
|---|---|---|---|
| `0x800AF2C8` `matchKeywordWithPriority` | Sole generated caller is `spawnCutsceneEffectsAndCues` at `0x800A9248`; named call returns through `after_22`, then caller masks `v0` at `0x800A9250` | None. Body loads `v0=*(a0)`, reads `*(v0+0x30)`, compares bytes, and returns at `0x800AF330` or `0x800AF358`; no `LOOKUP_FUNC`/`jalr` | No explicit termination edge. A bad input can fault at the dereference, but this audit does not prove its producer |
| `0x8003E8DC` `slotDispatcherIter` | Loads `slot=*(table + (selector&0xffff)*8)` at `0x8003E938`; indirect call returns through `after_0` | `LOOKUP_FUNC(slot->update_func)` at `0x8003E974`; `update_func==0` reaches `get_function(0)`, whose missing-function path asserts/exits unless stubbed | Selects `H-PreTargetBoundary` for the `0x80007904` family; does not identify the field writer |
| `0x800078E0` `rs_memset` | Direct callers, including `allocateSongChannelArray` at `0x8008F2CC`, return through generated `after_N` labels; body returns at `0x80007900` | No resolver edge | `0x80007904` is only its return delay-slot stamp, not a caller PC |
| `get_function` | `LOOKUP_FUNC` expands to `get_function((int32_t)(val))` | Missing address reaches assert/exit; present address returns a host pointer | Terminal boundary for zero update pointer, not evidence that the pointer is legitimate |

## Result

The explicit `slot->update_func -> LOOKUP_FUNC -> get_function(0)` edge selects
`H-PreTargetBoundary` for the slot-dispatch family. The named
`matchKeywordWithPriority` call has a valid generated continuation and no
resolver, so `H-GeneratedContinuationMismatch` is not supported. The two
failures remain separate at source scope: the slot path has a proven terminal
edge, while the match path has only a potentially bad dereference.

The `0x8000834C` and `0x80007904` values are return delay-slot stamps from
unrelated functions, not the native caller of the resolver. This is a static
breadcrumb limitation, not a mitigation or a legitimacy judgment.

## Next measurement

Run one qualified port capture with the existing resolver first-hit and slot
pre-call diagnostics plus the indirect positive control. The discriminator is
whether the same run records `slotDispatcherIter` pre-call `update=0`
immediately before `get_function(0)`, versus a nonzero update pointer followed
by a failure in `matchKeywordWithPriority`.
