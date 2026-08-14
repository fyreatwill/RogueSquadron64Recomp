# NEXT work unit (s949)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is the complete `soundMacroOpKeyOnNote` object
and field lifecycle: callers establish whether `a0` is a voice record or a
different context, writers establish the meaning of `+0x64`, and consumers of
the table at `0x8014 - 0x276C` establish whether the value is a slot handle.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit `soundMacroOpKeyOnNote` at `0x80089C44`: enumerate every generated
caller, trace its `a0` source, enumerate all writes to the caller object's
`+0x64`, and enumerate reads/consumers of the slot-indexed table populated at
`0x8014 - 0x276C`. Cross-check companion symbols and the known voice table.
No guard, behavior change, build, or soak.

Competing hypotheses:

- H-sound-macro-voice-context-valid: callers pass the same voice-record or
  composite-handle-bearing object, and `+0x64` is a valid slot/handle field.
- H-sound-macro-context-mismatch: at least one caller or consumer uses a
  different structure, making the `+0x64` read incompatible with the voice
  handle contract.
- H-sound-macro-context-unclassified: callers, writers, or table consumers
  remain unresolved after the exhaustive source/symbol search.

Discriminating measurement: complete caller `a0` provenance, `+0x64` writer
set, and table-consumer inventory. Consistent voice-object provenance and
compatible slot use select valid; an incompatible structure or field use
select mismatch; any unresolved edge selects unclassified.

Exact commands:

`rg -n -C 12 "soundMacroOpKeyOnNote|jal +0x80089C44|0x80089C44" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/*.txt`

`rg -n -C 8 "0X64|0x64|-0X276C|-0x276C|801427" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`
