# M3 s3592 — CPU MORT decode/output publication idiom audit

## Scope and discriminator

The bounded source census covered generated `funcs_27.c` addresses
`0x8009D7D0..0x8009DD7C`, its direct callers at `0x8009C540` and
`0x8009C88C`, and the output publication caller at `0x8009C4C0`. The competing
models were: a complete decode/output contract (H-MortComplete), a missing or
invalid decoded-sample edge (H-MortGap), or a mistaken address-range label
(H-MortMisread). The discriminator was one entry/descriptor/writer/consumer/
base/stride table, not a runtime counter.

## Classified table

| Edge | Generated site | Contract |
|---|---|---|
| Entry | `filterVoiceSampleBlock` `0x8009D7D0` | Takes sample count/phase in `a0`, source samples in `a2`, destination/control span in `a3`; selects either the short-count or packed coefficient path. |
| Filter writer | `0x8009D864` | Rewrites 13 signed 16-bit source samples at `a2`, stride `+2`; loop bound is literal 13. |
| Zero/descriptor writer | `0x8009D87C` | Clears 40 signed 16-bit entries at `a3`, stride `+2`; loop bound is literal 40. |
| Copy writer | `0x8009D8A4` | Copies 13 signed 16-bit samples from `a2` into `a3 + 2*a1`, advancing destination by `+6`; source stride `+2`. |
| Delay entry | `applyVoiceDelayFilter` `0x8009D8C4` | Reads voice state `+0x166`, clamps the delay index to `0..0x50`, then processes the voice delay span. |
| Delay input/output | `0x8009D910..0x8009D960` | Copies 0x77 halfwords from voice `+0x50` to voice base, then updates 0x28 halfwords at `voice+0xF0` from the filtered input plus the caller span. Both loops have explicit bounds. |
| Lattice entry | `runVoiceLatticeFilter` `0x8009D980` | Reads one signed 16-bit sample from `t1`, advances `+2`, computes the fixed-point lattice result, and emits to `t0`. Caller supplies 0xC, 0xD, 0xC, and 0x77 iterations for the four stages. |
| Lattice writer | `0x8009DB2C` | Writes one signed 16-bit result to `t0`, advances destination `+2`, and repeats while the caller-provided count remains positive. Saturation is explicit to signed 16-bit range and aligned by `& 0xFFF8`. |
| Render entry/descriptor read | `renderVoiceAudioBlock` `0x8009DB44..0x8009DBA0` | Reads eight 32-bit stage pointers from `voice+0x140..0x15C` and the output selector/count at `voice+0x164`. |
| Four decode/mix stages | `0x8009DBA4..0x8009DC30` | Each stage calls one mixer, `audioMixStereoBlock8`, then `runVoiceLatticeFilter`; source/output offsets are paired as `0/0x1A`, `0x1A/0x36`, `0x36/0x50`, and `0x50/0x50`. The final stage calls `audioCompandS16`. |
| Publication | `0x8009DC38..0x8009DC58` | Stores the eight processed pointers back to `voice+0x140..0x15C` and publishes the updated selector/count at `voice+0x164`. |
| PCM consumer | `audioMixStereoBlock8` `0x8009DC98..0x8009DD38` | Selects one of two 8-byte function-table banks at `voice+0x168` based on `voice+0x188`; reads eight signed 16-bit input pairs at offsets `0..0xE`, invokes the selected function eight times, and returns packed intermediate values in registers. |
| PCM reducers | `0x8009DD3C`, `0x8009DD54`, `0x8009DD64` | Apply the three fixed-point `1:3`, `1:1`, and `3:1` reductions, then call `audioCompandS16`. |
| PCM output | `audioCompandS16` `0x8009DD7C` | Sign-normalizes, clamps to `[-0x7FFF, 0x7FFF]`, and returns the 16-bit companded result; no memory write or unbounded pointer arithmetic occurs in this range. |

The two caller loops are structurally complete: `updateVoiceChannelParams`
reads paired signed-halfword descriptor streams, calls the filter and delay
functions four times, advances each source by `+2`, and advances the 13-sample
filter descriptor by `+0x1A`. The same pattern is repeated by the second
caller with its alternate stack descriptor at `sp+0xA8`. The render caller
then consumes the four 0x1A-byte channel groups and republishes all eight
stage pointers.

## Result

H-MortComplete is selected structurally. Every entry in the requested range
has a classified caller, bounded source/destination loop, consumer, or
publication edge; there is no missing decoded-sample writer, alternate base,
unchecked count, or concrete invalid value in the generated code. H-MortGap
is not selected, and H-MortMisread is not supported: the range is a coherent
CPU voice-filter/mix/compand path. This is static evidence only; it does not
prove that runtime allocator state, descriptor contents, or MORT DMA timing
are legitimate. No guard or runtime change was made.

Evidence is single-source (the generated recompilation and its direct call
edges); this audit needs an independent runtime/retail line before it can
close the broader M5 audio boundary.
