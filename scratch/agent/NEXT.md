# NEXT work unit (s917)

HYPOTHESIS-ID: m3-voice-pool-reset-inventory

Audit the adjacent generated audio helper `accumulateVoiceSampleOffset`
(`0x8009BD7C`, size `0x8C`) in
`../N64Recomp/RecompiledFuncs/funcs_26.c`. Enumerate its complete cursor and
offset arithmetic, every speech-buffer/global load and store, termination
conditions, return behavior, all generated callers, and companion symbol or
decomp evidence. Do not add a guard, change game behavior, build, or run a
soak.

Competing hypotheses:

- H-speech-offset-unclassified: the helper's cursor/offset arithmetic mixes
  incompatible speech-buffer shapes or has an unproven bound.
- H-speech-offset-classified: its input/output fields, arithmetic, and callers
  form one explicit bounded contract.
- H-speech-offset-shape-mismatch: a caller or sibling helper supplies a
  different buffer/offset contract; record the exact split and stop.

Discriminating measurement: a complete site table for
`accumulateVoiceSampleOffset`, every buffer/global load and store, all
generated callers, and the companion symbol/decomp basis. Any omitted access,
unbounded arithmetic/termination, or incompatible caller shape rejects full
classification.

Exact commands: use `rg` to enumerate `accumulateVoiceSampleOffset` and its
callsites in `../N64Recomp/RecompiledFuncs/funcs_26.c`, then bounded `sed`
windows and the companion `rogue_squadron64` symbol/decomp files. No game
build or soak is planned.
