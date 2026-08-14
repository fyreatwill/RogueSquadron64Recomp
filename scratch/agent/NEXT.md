# NEXT work unit (s950)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is the complete `tickAudioChannel` context
`+0x64` lifecycle and computed-address consumer set for
`0x8013D894 + index*0x17C`.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit the `tickAudioChannel` channel context around `0x8008BC10` and every
generated use of its `+0x64` field; enumerate all computed consumers and
writers of the table at `0x8013D894 + index*0x17C`, then cross-check companion
symbols and the known voice table. No guard, behavior change, build, or soak.

Competing hypotheses:

- H-channel-context-field-valid: channel `+0x64` is a legitimate value for
  the per-slot table and every computed consumer uses the same contract.
- H-channel-context-field-mismatch: a channel-field writer or table consumer
  treats `+0x64` as an incompatible field/value.
- H-channel-context-field-unclassified: a writer, computed consumer, or
  object-origin edge remains unresolved.

Discriminating measurement: complete channel-context `+0x64` reader/writer
set, table address arithmetic, all computed consumers, and companion-symbol
cross-check. Consistent field/value and table contracts select valid; an
incompatible structure or consumer selects mismatch; any unresolved edge
selects unclassified.

Exact commands:

`rg -n -C 10 "0x8008BC10|tickAudioChannel|0X64|0x64" ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`

`rg -n -C 8 -- "-0X276C|-0x276C|-0X271C|-0x271C|0X17C|0x17C|0x8013D894|0x8013D880" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`
