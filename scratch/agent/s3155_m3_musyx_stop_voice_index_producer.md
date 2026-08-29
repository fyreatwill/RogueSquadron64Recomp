# Session 3155 — `musyxStopVoice` index producer edge

## Competing hypotheses and discriminator

- `H-M3-ValidProducer`: every reachable predecessor proves the index passed to
  `musyxStopVoice` is in `0..31`.
- `H-M3-UnclassifiedProducer`: a reachable producer leaves the index
  unbounded.
- `H-M3-DeadSite`: the call is unreachable or only generated lowering.

The discriminator was the complete predecessor and writer table for the call
at `tickAllAudioChannels:0x8008CED0`.

## Predecessor table

| Edge | Guest instruction | Effect on `s6` before the call |
| --- | --- | --- |
| function entry | `0x8008C9BC` | sets `s6 = 0` |
| first-loop back edge | `0x8008D724` / `0x8008D728` | call is reached with the prior value; increment occurs only after the call, then continues while `s6 < MEM_BU[0x80141AD0]` |
| first-loop exit | `0x8008D734` | resets `s6 = 0` for the separate second loop; does not reach the call at `0x8008CED0` |
| second-loop increments | `0x8008D8F4`, `0x8008D91C` | occur after the first-loop call and cannot feed it |

The call is therefore reached only on first-loop iterations with
`s6 = 0..count-1`, where `count` is the byte at `0x80141AD0`.

## Complete writer table for `0x80141AD0`

| Writer | Valid-input path | Invalid-input path |
| --- | --- | --- |
| `setDisplayMode` (`0x8008EA14`) | `0x8008EA20` tests `a1 < 0x21`; `0x8008EA44` stores `a1` | `0x8008EA54` stores `0x20` |
| `reapplyDisplayMode` (`0x8008EB5C`) | `0x8008EB68` tests `a1 < 0x21`; `0x8008EB8C` stores `a1` | `0x8008EB9C` stores `0x20` |

The generated tree contains no other store to this byte. Both independent
companion metadata and the generated bodies identify the byte as the active
channel count and describe the same two setters and validation rule.

## Result

`count <= 0x20`, so the pre-increment call argument is always `s6 < 0x20`.
This selects `H-M3-ValidProducer` and closes the `musyxStopVoice` computed
record `+0x1` producer question at this static scope. The base KSEG0 check in
`musyxStopVoice` remains a separate safety check; no guard, build, run, oracle
watch, or audio behavior was changed.

Evidence sources: generated `RecompiledFuncs/funcs_23.c` at the listed guest
PCs; companion `rogue_squadron64/symbol_files/main_overlay.txt` entries for
`setDisplayMode`, `reapplyDisplayMode`, and `tickAllAudioChannels`.
