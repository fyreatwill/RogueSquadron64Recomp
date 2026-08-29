# Session 3162 — `stopVoiceByKey` producer audit

## Discriminator

The competing outcomes were `H-M3-Proven`, `H-M3-Unclassified`, and
`H-M3-Dead`. The complete producer table is:

| guest PC | caller / edge | return source | range proof | independent metadata |
|---|---|---|---|---|
| `0x80098054` | `startStreamedSampleVoice` → `stopVoiceByKey` | `stopVoiceByKey` calls `allocateSynthVoice` at `0x80086934`, copies `v0` to `s0`, and returns `s0` unless it is `-1` | `allocateSynthVoice` scans from index 0 while `t0 < MEM_BU(0x80141AD0)`. The complete generated writer inventory for that byte is `setDisplayMode` (`0x8008EA44`/`0x8008EA54`) and `reapplyDisplayMode` (`0x8008EB8C`/`0x8008EB9C`); each accepts `a1 < 0x21` and otherwise stores `0x20`. A successful result is therefore `0..31`; `-1` is rejected at `0x80098064`. | Companion `main_overlay.txt` identifies all three functions at the same addresses and describes `allocateSynthVoice` as scanning the voice pool. The companion ELF independently contains `allocateSynthVoice @ 0x80086594` and `stopVoiceByKey @ 0x80086914`. |

## Result

Selected: `H-M3-Proven`. The generated call graph has one direct
`stopVoiceByKey` caller, and no indirect registration or `get_function` edge
was found by the complete symbol/function search. The result is proven below
the 64-slot bound before `startStreamedSampleVoice` passes it to
`musyxTriggerVoiceAttack`.

This is static evidence only. No guard, audio behavior, generated source,
build, or runtime route was changed. The prior `H-M3-Unclassified` label is
superseded because the complete `D_80141AD0` writer set was included; it was
believable when only the caller's local `!= -1` check had been considered.
