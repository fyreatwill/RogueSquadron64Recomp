# Session 3249 — MusyX status-03 idiom audit

Source audited: `/Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs.s2471-gate3-before/funcs_26.c`, plus generated callers in `funcs_15.c`, `funcs_12.c`, and `funcs_16.c`. This is a static snapshot, not runtime evidence.

## Census

The status byte is the first byte of each voice slot (`0x80154620 + slot_stride`, stride `0x1228`). The complete generated-source search for that base/offset found these reads and stores:

| PC | function | operation / state use | edge or transition |
|---|---|---|---|
| `0x8009AF80` | `findVoiceSlotByAge` | read nonzero | free-slot/age scan; no status-03-specific transition |
| `0x8009B298` | `stopVoiceSlotSynced` | read `01` / `02` | `01` clears status at `0x8009B2C4`; `02` performs stop/message work, then publishes `03` at `0x8009B30C` |
| `0x8009B36C` | `stopVoiceByHandle` | read nonzero | handle lookup; calls `stopVoiceSlotSynced` on match |
| `0x8009B3EC`, `0x8009B44C` | `isVoiceHandleActive` | read nonzero | active-handle query; no mutation |
| `0x8009B62C`, `0x8009B654` | `serviceVoicePoolFrame` | read nonzero, then dispatches `00/01/02/03` | `02` enters stop/reap path; `03` enters streaming/status-3 path |
| `0x8009B8E8`, `0x8009B95C` | `getVoicePlaybackProgressByKey` | read nonzero | keyed progress query; no mutation |
| `0x8009BC9C` | `findFreeSpeechVoiceSlot` | read zero/nonzero | free-slot scan; no mutation |
| `0x8009BCF8` | `shutdownMusyXVoices` | read nonzero | waits for a nonzero slot while repeatedly invoking `stopVoiceSlotSynced` |

Direct status stores found:

| PC | function | value | meaning / downstream edge |
|---|---|---:|---|
| `0x8009B2C4` | `stopVoiceSlotSynced` | `00` | terminal clear for a slot already in state `01` |
| `0x8009B30C` | `stopVoiceSlotSynced` | `03` | publishes status-03 after the state-02 stop/message path |
| `0x8009B6F8` | `serviceVoicePoolFrame` | `02` | service promotes a qualifying live voice to state 02 |
| `0x8009B7A8` | `serviceVoicePoolFrame` | `00` | clears a non-streaming voice after `stopVoice` |
| `0x8009B7CC` | `serviceVoicePoolFrame` | `03` | service republishes status-03 for a streaming voice |
| `0x8009B7EC` | `serviceVoicePoolFrame` | `00` | clears status-03 after the stream field reaches zero |
| `0x8009BBF0` | `initMusyXVoiceTable` | `00` | initialization clear |

## Contract result

`H-Status03NamedContract` selected for the audited snapshot. The status-03 publisher is named and legitimate: `stopVoiceSlotSynced` publishes `03` at `0x8009B30C` after the status-02 stop path. `serviceVoicePoolFrame` is the named consumer/reaper: it recognizes `03` at `0x8009B680`, checks the stream field, calls `stopStreamedVoice` when required, and clears the status at `0x8009B7EC` once the stream field is zero. The service also has a second legitimate `03` publication at `0x8009B7CC` for the streaming branch.

`shutdownMusyXVoices` is a waiter over the same slot status table, not a publisher. Its status-03 wait is therefore safety/control flow around the named worker contract; the static result does not authorize removing the wait hatch or force-clearing the byte.

This is two-source static evidence: generated instruction sites establish the writer/consumer transitions, and the companion named-symbol table identifies the functions and caller addresses (`shutdownMusyXVoices` is called from `funcs_15.c`; the query helpers are called from `funcs_12.c`, `funcs_15.c`, and `funcs_16.c`). No runtime causation is claimed.
