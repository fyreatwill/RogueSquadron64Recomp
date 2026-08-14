# NEXT work unit (s951)

Pre-run decision: source-only; do not build, run the game, or enqueue a soak.
The discriminating measurement is the complete non-sentinel writer/indirect
dispatch set for the `tickAudioChannel` context `+0x64` field. The table
address set is already complete through direct generated forms.

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit the remaining channel-object origin and indirect-dispatch edges for
`+0x64`: enumerate all audio-overlay function-pointer tables/registrations and
all callers that can pass a channel object to the `+0x64` writers/readers;
cross-check whether any non-generated or indirect writer can replace the
observed `-1` sentinel. Source-only; no guard, behavior change, build, or
soak.

Competing hypotheses:

- H-channel-context-field-valid: channel `+0x64` is a legitimate value for
  the per-slot table and every computed consumer uses the same contract.
- H-channel-context-field-mismatch: a channel-field writer or table consumer
  treats `+0x64` as an incompatible field/value.
- H-channel-context-field-unclassified: a writer, computed consumer, or
  object-origin edge remains unresolved.
- H-channel-context-field-sentinel-contract: all reachable channel-field
  writers intentionally maintain `-1`, making the table write a deliberate
  sentinel propagation rather than an invalid voice value.

Discriminating measurement: complete audio-overlay function-pointer
registration/call edges and channel-object origin set for every `+0x64` access.
A reachable non-sentinel writer or incompatible object selects mismatch; only
sentinel writers with closed dispatch/origin edges select the sentinel
contract; any unresolved indirect edge selects unclassified.

Exact commands:

`rg -n -C 10 "0x8008BC10|tickAudioChannel|0X64|0x64|jalr|LOOKUP_FUNC" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`

`rg -n -C 8 -- "-0X276C|-0x276C|-0X271C|-0x271C|0X17C|0x17C|0x8013D894|0x8013D880" ../N64Recomp/RecompiledFuncs/funcs_21.c ../N64Recomp/RecompiledFuncs/funcs_22.c ../N64Recomp/RecompiledFuncs/funcs_23.c ../rogue_squadron64/symbol_files/main_overlay.txt`
