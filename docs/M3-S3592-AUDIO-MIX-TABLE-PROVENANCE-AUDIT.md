# M3 s3592 — audio mix-table provenance audit

## Scope and discriminator

This was a source-only, grep-enumerate/classify audit of the audio voice
mix-table fields at `voice+0x168` and `voice+0x188`. The discriminator was one
complete table of initializers, selector writers, bank layout, bounds, and
indirect consumers. The audit excluded the already-closed CPU MORT body at
`0x8009D7D0..0x8009DD7C`.

Competing hypotheses:

- H-MixTableComplete: the table and selector establish the banks consumed by
  `audioMixStereoBlock8`.
- H-MixTableGap: a concrete initializer, selector writer, consumer base, count,
  or function target is missing or invalid.
- H-MixTableMisread: these offsets are not the active voice mix-table fields.

## Evidence

The complete relevant search covered `../N64Recomp/RecompiledFuncs/funcs_*.c`,
including literal and address-derived uses of `0x168`/`0x188` and the named
audio-family symbols.

1. `initMusyXVoiceSlot` at `0x8009BE70` clears `0x190` bytes, establishing
   zero initialization for both fields. `computeVoicePanCoefficients` at
   `0x8009C2E0..0x8009C438` reads the signed halfword at `+0x188`, computes
   `voice + 0x168 + (selector << 4)`, and writes exactly eight halfwords at
   offsets `0,2,...,0xE`. Its three callers are present in the audio overlay.
2. `updateVoiceChannelParams` at `0x8009C4C8..0x8009C4D0` is the only
   audio-overlay writer found for `+0x188`; it toggles the existing value with
   `xori 1`. With the slot clear, the selector alternates between banks 0 and
   1. No other audio-overlay writer to this field was found.
3. `audioMixStereoBlock8` at `0x8009DC98..0x8009DD2C` reads `+0x188`, selects
   `voice+0x168` or the adjacent 16-byte bank, then consumes eight entries at
   offsets `0..0xE`. Each entry is paired with a same-slot entry from the
   other bank and dispatched through `LOOKUP_FUNC(ctx->r11)`. The caller
   `renderVoiceAudioBlock` supplies the four targets through known
   return-link-derived addresses at `0x8009DBAC`, `0x8009DBD0`,
   `0x8009DBF4`, and `0x8009DC18`.
4. Literal `0x168`/`0x188` matches elsewhere are stack slots, unrelated
   structures, or other overlays. The address-derived matches in `funcs_22.c`
   and `funcs_23.c` are separate sequence-table helpers, not this voice
   object.

## Result

H-MixTableComplete is selected structurally. The requested initializer,
selector writer, two-bank layout, eight-entry bound, and all eight indirect
consumer pairs are accounted for. H-MixTableGap is not supported: no concrete
invalid base, selector, count, or function target was found, so no guard or
runtime change is justified. H-MixTableMisread is not supported by the
coherent producer/consumer layout and caller chain.

This is a source-structure result only. Runtime descriptor contents, allocator
state, and DMA/task timing remain unproven; it does not establish that values
seen during a failing run are legitimate.

## Reproduction queries

```sh
rg -n -i '0x168|0x188|168\(|188\(|audioMixStereoBlock8|jalr|voice.*mix|mix.*table' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n -i '0x8009DC98|0x8009DC9C|0x8009DCAC|0x8009C4C8|0x8009C4D0' ../N64Recomp/RecompiledFuncs/funcs_*.c
rg -n 'computeVoicePanCoefficients|initMusyXVoiceSlot|updateVoiceChannelParams\(' ../N64Recomp/RecompiledFuncs/funcs_*.c
```
