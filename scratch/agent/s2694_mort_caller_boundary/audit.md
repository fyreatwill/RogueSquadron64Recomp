# s2694 M5 caller/publication boundary audit

Source snapshot: `../N64Recomp/RecompiledFuncs/funcs_24.c`, with the
companion map at `../rogue_squadron64/symbol_files/main_overlay.txt`.
No build or runtime probe was run.

## Direct-call census

| Caller site | Caller | Relevant arguments | Immediate result/field use |
|---|---|---|---|
| `0x80090F00` | `musyxMixActiveVoices` | `a0=voice`, `a1=frame offset`, `a2=voice-block stride`, `a3=output block + voice offset` | Returns to the voice loop; caller advances stream cursor and clears/sets voice status. |

`musyxMixActiveVoices` is called by `musyxSynthFrame` at `0x800914C8`,
`0x80091588`, and `0x8009163C`. These are scheduling loop sites, not
additional direct callers of `musyxRenderVoiceSamples`.

## Render output and post-call consumers

Inside `musyxRenderVoiceSamples` (`0x8008FFAC`), `$a3` is copied to `$s0` at
`0x8008FFF4`. The kernel writes generated samples through `$s0` and updates
voice-local state through `$s1`, including fields `+0x3C`, `+0x40`, `+0x44`,
`+0x48`, `+0x4A`, `+0x58`, `+0x60`, `+0x62`, `+0x64`, `+0x78`, and `+0x84`.
It calls only the internal numeric helper `truncDouble`; it has no AI, queue,
DMA, or publication call.

After the call at `0x80090F00`, `musyxMixActiveVoices` rereads and increments
the voice cursor at `0x80090F24`, clears the per-voice state byte at
`voice+0x22` at `0x80090F3C`, and later marks voice state and writes loop
bookkeeping at `+0x7C`, `+0x80`, and `+0x84` (`0x80090F8C` through
`0x80091000`).

There is no named payload copy or transform from the render output block into
the AI worker allocation (`0x801496B0` / sixteen `0x300` buffers), no queue or
service signal, and no ordering edge to `osAiSetNextBuffer` in this caller
chain. The `0x800902DC` site previously associated with this boundary is
instead `acquireSampleStreamBlock` inside `musyxRenderVoiceSamples`; it stores
the descriptor result at voice `+0x40` and is not an AI publication site.

## Decision

The complete named caller/consumer table selects `H-unresolved-address`. It
rules out `H-caller-publishes` and `H-service-boundary` for the audited caller
chain on static evidence only. No runtime watch, writeback, remap, or
mitigation is authorized. The missing edge remains either an unnamed or
indirect consumer outside this call chain or an unmapped service boundary.
