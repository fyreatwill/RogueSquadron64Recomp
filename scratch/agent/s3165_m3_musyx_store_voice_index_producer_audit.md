# Session 3165 — `musyxStoreVoiceAdsrParams` index producer audit

## Competing hypotheses

- `H-M3-Proven`: every reachable producer of the voice index passed to
  `musyxStoreVoiceAdsrParams` proves the `0..63` mixer-record bound.
- `H-M3-Unclassified`: a reachable producer is unbounded, or the owning
  `+0x67` field is populated through an unrecovered data/indirect path.
- `H-M3-Dead`: the apparent call or access is unreachable/lowering-only.

## Complete static table

| Guest PC | Site / caller | Producer or owner construction | Local proof | Independent metadata |
|---|---|---|---|---|
| `0x8008A9D8` | `musyxSetVoiceAdsrFromTable` → `musyxStoreVoiceAdsrParams` | `$s5` is copied from incoming `$a0`; the byte at `$s5+0x67` is loaded directly as `$a0` | No check on the loaded byte before the call; callee masks to 16 bits, computes `index*0x88`, and checks only `0x801496F8` base | `main_overlay.txt` names `musyxSetVoiceAdsrFromTable @ 0x8008A8C4` and `musyxStoreVoiceAdsrParams @ 0x800922C4`; its comment identifies the destination as an `0x88` voice slot |
| `0x8008A548` | Same sound-macro function, `musyxInitVoiceFromSample` edge | Same `$s5+0x67` field; used as the voice index for the preceding init call | No local range check in this path | Companion names `musyxInitVoiceFromSample @ 0x80092128` |
| `0x8008962C` | `tickAudioChannel` → `isAudioSlotActive` | `$s0+0x67` is read from the active channel/voice record | This is a reader/control use, not a writer of the index field; no proof that it establishes the stored byte's range | Generated symbol/call structure agrees with the named MusyX channel path |
| `0x8008BC50`, `0x8008C464`, `0x8008C940` | Three additional MusyX readers in `funcs_23.c` | Each reads an owning record's `+0x67`; no corresponding store to that field appears in the generated tree | Reader sites do not prove the producer contract | Generated tree contains the sites; companion metadata does not expose a distinct writer body for them |

## Writer inventory

The complete generated-source search for stores at record-relative `+0x67`
finds no `sb`/`MEM_B` writer through a live MusyX record pointer. The only
literal `+0x67` stores are stack temporaries in `0x800873E4` and unrelated
overlay records at `0x800EC944`, `0x800EC9B0`, `0x800ECBAC`, `0x800E7C58`,
`0x800E841C`, `0x800E8434`, and `0x80100010`; none is connected by the
generated call/data-flow graph to the `$s5+0x67` consumer. No direct `jal`,
function-pointer entry, or `get_function` edge supplies a recovered writer.

## Result

`H-M3-Unclassified` is selected. The call is a real reachable generated site,
so `H-M3-Dead` is rejected. The field's complete reachable writer is not
recovered, so `H-M3-Proven` cannot be selected. This is a static contract
classification, not proof of a retail-invalid index. No guard, audio behavior,
generated source, build, or runtime run was authorized.
