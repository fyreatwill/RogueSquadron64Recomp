# NEXT work unit (s922)

HYPOTHESIS-ID: m3-streaming-voice-inventory

Audit the next adjacent generated audio helper `advanceVoiceStateToPlaying`
(`0x8009C2A0`, size `0x1C`) in the generated recompiled files. Enumerate its
complete control and voice-record/state field flow, every indirect call and
pointer/size argument, loop or termination behavior, all generated callers,
and companion symbol or decomp evidence. Do not add a guard, change game
behavior, build, or run a soak.

Competing hypotheses:

- H-advance-voice-unclassified: the helper's state transition has an unchecked
  or incompatible field/value path.
- H-advance-voice-classified: it is a fixed-shape state transition with all
  transition and all generated callers supply the same record form.
- H-advance-voice-shape-mismatch: a caller or sibling path supplies a
  different state contract; record the exact split and stop.

Discriminating measurement: a complete site table for
`advanceVoiceStateToPlaying`, every slot/global/queue/buffer load and store,
indirect call and argument, loop/termination behavior, all generated callers,
and the companion symbol/decomp basis. Any omitted access, unbounded
termination, or incompatible caller shape rejects full classification.

Exact commands: use `rg` to enumerate `advanceVoiceStateToPlaying` and
`0x8009C2A0` in `../N64Recomp/RecompiledFuncs`, then bounded `sed` windows
and the companion `rogue_squadron64` symbol/decomp files. No game build or
soak is planned.
