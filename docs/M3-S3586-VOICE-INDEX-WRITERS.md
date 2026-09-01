# M3 s3586 — `voice_record+0x64` writer/lifecycle audit

## Question and discriminator

This bounded static audit enumerates every generated write to the MusyX
voice-table field at `D_8013D880 + slot*0x17C + 0x64`, plus the call edges that
publish records into the handle list.

- H-VoiceIndexBounded: the low byte of every live field value is a valid
  voice-table slot, and invalidation uses `-1`.
- H-VoiceIndexUnsafe: a writer can publish an out-of-range low byte while its
  handle node remains reachable.
- H-VoiceRecordMisread: the field is being treated as a slot index when it is
  actually a packed handle, or the table/layout identification is wrong.

The discriminator is the complete writer list and value construction, checked
against the consumer's exact compare and indexing operations.

## Writer enumeration

The field's absolute offset is represented by generated code as `-0x271C($at)`
when `$at = 0x80140000 + slot*0x17C`.

| PC | Function | Value | Lifecycle classification |
|---|---|---|---|
| `0x80087294` | `startNoteOnVoice` | `((a0 >> 16) << 16) | ((a2 & 0xFF) << 8) | slot` | Publishes a packed handle. `slot` is the return of `allocateSynthVoice`, whose scan returns `-1` or a table index below the active count. |
| `0x80086984` | `stopVoiceByKey` | `-1` | Clears the selected record after unlinking it. |
| `0x800897B8` | `soundMacroOpStopVoice` | `-1` | Clears the record after unlinking it. |
| `0x80089814` | `soundMacroOpReturnFromGosub` | `-1` | Clears the record on macro cleanup. |
| `0x8008DA68` | `releaseSynthVoice` | `-1` | Clears the record after unlinking it. |
| `0x8008DB80` | `stopVoicesByHandle` | `-1` | Clears the matching record after unlinking it. |
| `0x8008E660` | `resetMusyXEngineState` | `-1` | Initializes all 32 records in a `0x17C`-stride loop. |

No other generated store to the field's `-0x271C` representation was found.
The direct `startNoteOnVoice` callers are at `0x800876E0`, `0x80087828`,
`0x80087CBC`, and `0x80089CF0`; reset has three direct callers in `funcs_23.c`.

## Consumer reconciliation

`stopVoicesByHandle` loads node `+0xC`, compares the complete value against the
record field, then masks that handle to eight bits before indexing the
`0x17C`-stride table. Thus node `+0xC` is a packed handle, not a standalone
slot index. The table, stride, active-count byte, node links, and four direct
consumer edges remain structurally consistent.

## Result

`H-VoiceRecordMisread` is selected for the semantic correction: the prior
description called `voice_record+0x64` a standalone slot index, but the live
value written by `startNoteOnVoice` is a packed handle whose low byte is the
slot. The table and layout identification are not overturned.

`H-VoiceIndexUnsafe` is not selected. Every enumerated non-sentinel writer uses
the allocator's returned slot, and all cleanup/reset writers use `-1`. This is
static evidence only; allocator state and record lifetime remain unproven at
runtime. No guard or runtime instrument is authorized.

ORIGIN: the only non-sentinel writer is `startNoteOnVoice` at `0x80087294`;
its packed value is legitimate by construction if the allocator contract
holds, with the slot index in the low byte. Cleanup writers deliberately
publish the `-1` sentinel.
