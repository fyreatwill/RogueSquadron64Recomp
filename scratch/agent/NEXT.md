# NEXT work unit (s918)

HYPOTHESIS-ID: m3-voice-stream-dma-inventory

Audit the adjacent generated audio helper `dmaVoiceSampleAndSignal`
(`0x8009BE08`, size `0x38`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate its complete DMA and
queue argument flow, every global/slot load and store, termination and return
behavior, all generated callers, and companion symbol or decomp evidence. Do
not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-voice-stream-dma-unclassified: the helper's DMA arguments, queue signal,
  or slot fields contain an unchecked or incompatible pointer/size contract.
- H-voice-stream-dma-classified: it is a fixed-shape synchronous DMA followed
  by one queue signal, with all callers supplying the same slot/message form.
- H-voice-stream-dma-shape-mismatch: a caller or sibling helper supplies a
  different DMA or queue contract; record the exact split and stop.

Discriminating measurement: a complete site table for
`dmaVoiceSampleAndSignal`, every DMA/queue/global load and store, all generated
callers, and the companion symbol/decomp basis. Any omitted access,
unbounded arithmetic/termination, or incompatible caller shape rejects full
classification.

Exact commands: use `rg` to enumerate `dmaVoiceSampleAndSignal` and its
callsites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game build
or soak is planned.
