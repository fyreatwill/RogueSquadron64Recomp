# NEXT work unit (s921)

HYPOTHESIS-ID: m3-streaming-voice-inventory

Audit the next adjacent generated audio helper `consumeVoiceSamples`
(`0x8009C240`, size `0x60`) in the generated recompiled files. Enumerate its
complete control and voice-record/cursor field flow, every indirect call and
pointer/size argument, loop or termination behavior, all generated callers,
and companion symbol or decomp evidence. Do not add a guard, change game
behavior, build, or run a soak.

Competing hypotheses:

- H-consume-voice-unclassified: the helper's state/cursor contract contains
  an unchecked or incompatible field/value path.
- H-consume-voice-classified: it has one coherent bounded voice-record state
  transition and all generated callers supply the same record form.
- H-consume-voice-shape-mismatch: a caller or sibling path supplies a
  different state/cursor contract; record the exact split and stop.

Discriminating measurement: a complete site table for
`consumeVoiceSamples`, every slot/global/queue/buffer load and store,
indirect call and argument, loop/termination behavior, all generated callers,
and the companion symbol/decomp basis. Any omitted access, unbounded
termination, or incompatible caller shape rejects full classification.

Exact commands: use `rg` to enumerate `consumeVoiceSamples` and
`0x8009C240` in `../N64Recomp/RecompiledFuncs`, then bounded `sed` windows
and the companion `rogue_squadron64` symbol/decomp files. No game build or
soak is planned.
