# Session 3084 generated-symbol audit — `0x800555E8`

## Discriminator

The bounded six-surface table distinguishes an exact callable identity from
an inline fragment/data gap, an address conflict, or insufficient evidence.

## Evidence table

| Surface | Observation | Consequence |
|---|---|---|
| Companion map | `initPlayerStructsPreamble = 0x800555E8`, size implied by the next symbol at `0x800555F0`; described as a two-instruction tail-call entry | Exact adjacent callable identity is supplied independently |
| Generated body | `0x800555E8: j L_800555F0`; `0x800555EC: nop`; then `initPlayerStructs(rdram, ctx)` and return | This is a callable two-instruction preamble, not an isolated data fragment |
| Callers | Generated `initMission` calls `initPlayerStructs` at `0x800555F0`; no semantic conflict with the preamble entry | Adjacent target and role are consistent |
| Header | Declares `initPlayerStructsPreamble` and `initPlayerStructs` as separate generated functions | Generated naming is synchronized |
| Overlay registration | Registers `initPlayerStructsPreamble` at ROM `0x551A8`, size `0x8`, followed by `initPlayerStructs` at `0x551B0`, size `0xA8` | Exact extent and placement agree |
| Project TOML / rename tooling | TOML maps `0x800555E8`, size `0x8` to `initPlayerStructsPreamble`; rename map maps the former placeholder to the same name | Regeneration-safe project mapping agrees |

## Decision

Selected **H-ExactIdentity**. The project TOML and generated tree are already
synchronized to `initPlayerStructsPreamble`; no generated or runtime edit was
needed. Verification found no stale placeholder in the active generated tree.

ORIGIN: naming-only classification. No runtime, audio route, mitigation, or
generated instruction behavior changed.

Next ranked unresolved project-TOML placeholder after this address:
`fake_func_8006ACA4`.
