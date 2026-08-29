# Session 3158 — `musyxStoreVoiceAdsrParams` voice-index audit

## Scope and discriminator

This is a source-only audit of the complete `0x88`-stride voice-record class
for `musyxStoreVoiceAdsrParams` (`0x800922C4`). The competing outcomes were:

- `H-M3-Proven`: every reachable indexed access has a dominating base and
  `0..63` index proof.
- `H-M3-Unclassified`: a reachable access lacks a complete base/index proof.
- `H-M3-LoweringOnly`: apparent sites are only duplicated lowering.
- `H-M3-Dead`: no reachable caller/site remains in the dispatch graph.

The discriminating measurement was the complete current generated
caller/site/producer table, checked against the companion symbol metadata.

## Site and caller table

| guest PC | operation | derived address | proof status |
|---|---|---|---|
| `0x800922E0` | store halfword `+0x28` | `base + (a0 * 136) + 0x28` | reachable; `a0` unproved |
| `0x800922E8` | store halfword `+0x2A` | same record | reachable; `a0` unproved |
| `0x8009230C` | store word `+0x2C` | same record | reachable; `a0` unproved |
| `0x80092318` | store halfword `+0x30` | same record | reachable; `a0` unproved |

The generated body computes the stride as `sll a0,4`, `addu`, `sll,3`,
which is `a0 * 17 * 8 = a0 * 0x88`. It loads the array base from global
`0x801496F8` at `0x800922C8`; the existing entry guard proves only that this
pointer is in KSEG0, not that the masked/indexed value is within 64 records.
There is no index mask, compare, or branch in the body.

The current generated tree has exactly one direct caller:
`musyxSetVoiceAdsrFromTable` at `0x8008A9DC`. Immediately before the call,
`0x8008A9D8` loads `a0` with `lbu 0x67(s5)`. The caller performs no `<64`
check before the call. The companion symbol file independently identifies
the caller as the SoundMacro ADSR path and the callee as writing the four
fields in a `0x88` voice slot. The current overlay registration contains one
entry for the callee; no alternate generated direct or function-table caller
was found.

The identified base writer is `allocateSongChannelArray`:
`0x8008F0EC` stores the `rs_malloc` result into `0x801496F8`. Its allocation
size is derived from its incoming low 16-bit count and the same `0x88`
stride, which supports the base/stride interpretation but does not establish
that the later SoundMacro byte at `s5+0x67` is bounded to the allocated
record count. No other writer of the global was found in the current
generated tree.

## Result

This selects **`H-M3-Unclassified`**. The caller is reachable and the four
stores are real independent guest sites, not lowering duplicates; the
callee’s base guard does not prove the index. This is two-source static
evidence (generated control flow plus companion symbol metadata), not proof
that retail supplies an invalid value. No guard, audio behavior, or runtime
behavior is authorized by this result.
