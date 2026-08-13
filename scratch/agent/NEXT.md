# NEXT work unit (s920)

HYPOTHESIS-ID: m3-streaming-voice-inventory

Audit the next adjacent generated audio helper `serviceStreamingVoice`
(`0x8009BF14`, size `0x13C`) in the generated recompiled files. Enumerate its
complete control and voice-record/queue/buffer field flow, every indirect call
and pointer/size argument, loop or termination behavior, all generated callers,
and companion symbol or decomp evidence. Do not add a guard, change game
behavior, build, or run a soak.

Competing hypotheses:

- H-streaming-voice-unclassified: the helper's queue/state/buffer fields or
  callback path contains an unchecked or incompatible contract.
- H-streaming-voice-classified: it has one coherent bounded voice-record
  service shape and all generated callers supply the same record form.
- H-streaming-voice-shape-mismatch: a caller or sibling path supplies a
  different queue/buffer/callback contract; record the exact split and stop.

Discriminating measurement: a complete site table for
`serviceStreamingVoice`, every slot/global/queue/buffer load and store,
indirect call and argument, loop/termination behavior, all generated callers,
and the companion symbol/decomp basis. Any omitted access, unbounded
termination, or incompatible caller shape rejects full classification.

Exact commands: use `rg` to enumerate `serviceStreamingVoice` and
`0x8009BF14` in `../N64Recomp/RecompiledFuncs`, then bounded `sed` windows
and the companion `rogue_squadron64` symbol/decomp files. No game build or
soak is planned.
