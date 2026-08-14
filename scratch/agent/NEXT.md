# NEXT work unit (s940)

HYPOTHESIS-ID: m3-audio-stop-voices-by-handle-contract

Audit the voice-record base/count lifecycle consumed by `stopVoicesByHandle`
at `0x8008DA98`: enumerate every generated writer/initializer of the record
base at `0x8013D880`, the voice count at `0x80141AD0`, record handle fields at
`base + index*0x17C + 0x64`, and the `-1` sentinel used by the scan. Include
all callers/helpers that establish or invalidate those values and the
companion symbol/decomp evidence. Source-only; do not add a guard, change
game behavior, build, or run a soak.

Competing hypotheses:

- H-stop-voices-by-handle-lifecycle-valid: initialization and all writers prove
  a bounded count, valid base, in-range node index, and a reachable `-1`
  sentinel for every scan.
- H-stop-voices-by-handle-lifecycle-unclassified: the local arithmetic is
  coherent, but base/count/index or sentinel legitimacy is not proven.
- H-stop-voices-by-handle-lifecycle-mismatch: different writers or helpers use
  incompatible bases, strides, counts, handle offsets, or sentinel meanings.

Discriminating measurement: an exhaustive generated-source reference inventory
for the four lifecycle addresses/fields, with each writer's phase and range,
plus decomp-symbol cross-check. Any writer that can produce an out-of-range
index/base, any incompatible field contract, or any unproven sentinel path
selects unclassified/mismatch; otherwise the lifecycle is classified.

Exact command: `rg -n -C 8 "8013D880|80141AD0|0x64|0x17C|0x2780|0x271C|0x2770|0x276C|0x2768|0x2758" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64/symbol_files/main_overlay.txt`, then classify each writer and lifecycle edge. No game build or soak is planned.
