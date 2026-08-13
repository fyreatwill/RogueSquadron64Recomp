# NEXT work unit (s919)

HYPOTHESIS-ID: m3-voice-slot-helper-inventory

Audit the adjacent generated audio helper `func_8009BE40`
(`0x8009BE40`, size `0xD4`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate its complete control and
voice-slot field flow, every indirect call and pointer/size argument, loop or
termination behavior, all generated callers, and companion symbol or decomp
evidence. Do not add a guard, change game behavior, build, or run a soak.

Competing hypotheses:

- H-voice-slot-helper-unclassified: the helper's slot fields, indirect calls,
  or pointer/size arguments contain an unchecked or incompatible contract.
- H-voice-slot-helper-classified: it has one coherent bounded slot-operation
  shape and all callers supply the same argument form.
- H-voice-slot-helper-shape-mismatch: a caller or sibling path supplies a
  different slot/callback contract; record the exact split and stop.

Discriminating measurement: a complete site table for `func_8009BE40`, every
slot/global load and store, indirect call and argument, all generated callers,
and the companion symbol/decomp basis. Any omitted access, unbounded
arithmetic/termination, or incompatible caller shape rejects full
classification.

Exact commands: use `rg` to enumerate `func_8009BE40` and its callsites in
`../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed` windows and the
companion `rogue_squadron64` symbol/decomp files. No game build or soak is
planned.
