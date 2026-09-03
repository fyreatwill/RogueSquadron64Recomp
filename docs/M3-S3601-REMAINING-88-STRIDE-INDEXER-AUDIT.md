# M3 s3601 — remaining 0x88-stride voice-table indexers

## Work unit

Static census of every generated function that forms
`D_801496F8 + idx*0x88` (`lui 0x8015; lw -0x6908` then
`(idx<<4)+idx<<3`) other than the two consumers closed in session 3600
(`musyxStartVoiceRelease`, `beginVoiceFadeRelease`). Direct callers of
`isAudioSlotActive`, `stopVoiceMarkRetrigger`, `musyxInitVoiceFromSample`,
`musyxStoreVoiceAdsrParams`, `musyxStopVoice`, `musyxSetVoicePitchBend`,
`deactivateVoice`, `getVoiceUserField`, `musyxTriggerVoiceAttack`, and the
remaining same-formula indexer `setVoiceModulationParams` were classified.
No build or runtime run was performed.

The discriminator was the complete remaining-indexer / caller / `a0`
construction census across `funcs_21.c` through `funcs_26.c`:

- H-NextClassGap: a live remaining indexer can pass `0xFF` from the `-1`
  packed-handle low byte, or another out-of-range index, into the `0x88`
  voice table.
- H-NextClassComplete: every remaining caller argument is a slot below
  the live count or is structurally gated before the JAL, and only
  runtime allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification of the index source.

Closed classes were not repeated: release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Twelve `0x88`-formula consumers exist under `-0x6908`. Two were closed in
s3600. The remaining ten:

| Consumer | PC | Local `a0` mask | Local count check |
|---|---|---|---|
| `isAudioSlotActive` | `0x800920FC` | none | none (s166 KSEG0 **base** guard) |
| `musyxInitVoiceFromSample` | `0x80092128` | `andi 0xFFFF` | none (s484 base guard) |
| `musyxStoreVoiceAdsrParams` | `0x800922C4` | none | none (s484 base guard) |
| `musyxTriggerVoiceAttack` | `0x8009231C` | `andi 0xFFFF` | none (s484 base guard) |
| `musyxStopVoice` | `0x80092368` | none | none (s484 base guard) |
| `musyxSetVoicePitchBend` | `0x80092390` | none on `a0` (`a1` range-checked) | none (s484 base guard) |
| `setVoiceModulationParams` | `0x800923E4` | none | none |
| `stopVoiceMarkRetrigger` | `0x8009244C` | none | none (s484 base guard; inactive `+0x0==0` returns) |
| `deactivateVoice` | `0x800924F0` | none | none (s484 base guard) |
| `getVoiceUserField` | `0x80092564` | none | none (s484 base guard) |

`allocateSongChannelArray` uses the same `<<4 / + / <<3` formula as a
**byte size** for `rs_malloc` of the table and then stores the pointer at
`-0x6908`. It is not an indexer. `musyxMixActiveVoices` walks the table
from the live-count halfword at `-0x6900`; that mix-table family was
closed in s3592.

No generated `jal 0x800924F0` and no data-word reference to
`deactivateVoice` exist in `RecompiledFuncs/`. It is an unreferenced
consumer.

## Direct callers

### Packed-handle `+0x67` (inherits s3600 `+0x0` skip)

Every `-1` packed-handle writer also zeros `record+0x0` (s3600).
`tickAllAudioChannels` skips `+0x0==0` before `tickAudioChannel`.

| Site | Function | Callee | Gate |
|---|---|---|---|
| `0x8008C940` | `tickAudioChannel` | `isAudioSlotActive` | Parent skip `+0x0==0`. |
| `0x8008962C` | `computeChannelWaitDuration` | `isAudioSlotActive` | `s0 = a0` is the `0x17C` record. Callers are `tickAudioChannel` and seven `soundMacroOp*` handlers, each reached only from `tickAudioChannel`. |
| `0x8008BC50` | `tickAudioChannel` (`flags & 1`) | `stopVoiceMarkRetrigger` | Parent skip `+0x0==0`. Callee also returns on `slot+0x0==0`. |
| `0x8008A548` | `soundMacroOpPlaySampleKeymap` | `musyxInitVoiceFromSample` | `s5 = a0` is the record. Only caller is `tickAudioChannel` `0x8008C454`. |
| `0x8008A9D8` | `musyxSetVoiceAdsrFromTable` | `musyxStoreVoiceAdsrParams` | `s5 = a0` is the record. Only caller is `tickAudioChannel` `0x8008C3A0`. |

A live `+0x67 == 0xFF` still requires the allocator to return slot 255.
`allocateSynthVoice` returns `-1` or an index below the slot-count byte
at `0x80141AD0` (s3587).

### Allocator return, `-1` gated

| Site | Function | Callee | `a0` |
|---|---|---|---|
| `0x80086988`, `0x8008699C` | `stopVoiceByKey` | `isAudioSlotActive`, `stopVoiceMarkRetrigger` | `s0` = `allocateSynthVoice` after `s0 == -1` skip. |
| `0x800870BC` | `startNoteOnVoice` | `isAudioSlotActive` | `s1` = `allocateSynthVoice` after `-1` skip. |
| `0x800980EC`, `0x8009816C`, `0x8009818C`, `0x80098194` | `startStreamedSampleVoice` | `musyxInitVoiceFromSample`, `musyxSetVoicePitchBend`, `setVoiceModulationParams`, `musyxTriggerVoiceAttack` | `s0` replaced by `stopVoiceByKey` return (itself the allocator slot) after `-1` skip. Return value is that same slot, or `-1` on the early-out. |

`stopVoiceByKey` is the only generated caller of `allocateSynthVoice`
that then indexes the `0x88` table with the returned slot besides
`startNoteOnVoice`. Incoming `a0` is `andi 0xFF` (a key, not a slot).

### Count-bounded loop vs `0x80141AD0`

| Site | Function | Callee | Bound |
|---|---|---|---|
| `0x80086C48` | `findActiveVoiceByKeyPair` | `isAudioSlotActive` | `s3` starts at 0, `addiu 1`, `sltu` against the slot-count byte. |
| `0x8008E5CC` | `anyAudioSlotActive` | `isAudioSlotActive` | `s0` starts at 0, `addiu 1`, `slt` against the same byte; `blez` skips the walk. |
| `0x8008CE7C`, `0x8008CED0`, `0x8008D424`, `0x8008D710` | `tickAllAudioChannels` | `musyxTriggerVoiceAttack`, `musyxStopVoice`, `musyxSetVoicePitchBend`, `setVoiceModulationParams` | `s6` starts at 0 and increments once per `0x17C` record; continue while `s6 <` slot-count byte. Inactive records still JAL; callees that test `+0x0` return. |
| `0x80097DF4` | `serviceStreamedVoices` | `getVoiceUserField` | `s3` starts at 0, `addiu 1`, `lbu 0x1AD0` bound. |

The second `tickAllAudioChannels` walk after `L_8008D738` reuses `s6` as
a `0x20`-bounded `0x28`-stride counter and does not call these indexers.

### Speech-slot word at `0x8015462C` (`+0xC` / `+0x120C`)

| Site | Function | Callee | `a0` |
|---|---|---|---|
| `0x800869F4`, `0x80086A08` | `silenceVoiceSlot` | `isAudioSlotActive`, `stopVoiceMarkRetrigger` | Incoming `a0` after full-word `-1` skip. Only caller is `stopStreamedVoice`. |
| `0x800982EC` | `stopStreamedVoice` | `silenceVoiceSlot` | Incoming `a0` used as `0x18`-stride stream-table index, then passed through. Only caller is `serviceVoicePoolFrame` `lw 0x0($s5)`. |
| `0x80098264` | `setVoiceVolumePanLocked` | `setVoiceModulationParams` | Incoming `a0`. Only caller is `setVoiceMixByKey`. |
| `0x8009B534` | `setVoiceMixByKey` | `setVoiceVolumePanLocked` | `lw 0x462C($at)` after rejecting full-word `-1`. |

`s5` in `serviceVoicePoolFrame` is initialized to `0x80154638 - 0xC` =
`0x8015462C`. The `0x1228`-stride speech object at `0x80153420` stores
the streamed-voice slot at `+0x120C`, which aliases `lui 0x8015; lw
0x462C`. Generated writers of that word:

| Writer | Value |
|---|---|
| `serviceVoicePoolFrame` `0x8009B794` | return of `startStreamedSampleVoice` (allocator slot or `-1`) |
| init path `0x8009B20C` | explicit `-1` |

Consumers reject full-word `-1` before the JAL. The stored non-sentinel
value is the same allocator slot already classified above.

## Result

`H-NextClassComplete` is selected for this idiom. Every generated
remaining `0x88`-stride edge is count-bounded against `0x80141AD0`,
gated by `record+0x0==0` before a `+0x67` load, or taken from
`allocateSynthVoice` / `startStreamedSampleVoice` after a `-1` skip.
`deactivateVoice` has no generated caller. Layout identity of `+0x67`
as the packed-handle low byte is already closed by s3586/s3600. The
`0x462C` speech-slot word is the streamed-voice allocator return, not
a packed handle.

`H-NextClassGap` is not selected: no concrete out-of-range or
sentinel-as-index writer/call pair was found. `H-NextClassUnevaluable`
is not selected: every remaining JAL's `a0` resolved to one of the
three constructions above.

This is static evidence. Runtime allocator state, record lifetime, and
the live slot-count byte remain unproven, matching s3586–s3588. No
guard or runtime change is authorized. The consumers' missing local
count check is a missing bound, not a demonstrated invalid value.

The remaining `-0x6908` users that do **not** take `a0` as a slot index
(`musyxMixActiveVoices`, `musyxRenderVoiceSamples`, `musyxKeyOnVoice`,
`musyxSynthFrame`, `shutdownAudioEngine`, `allocateSongChannelArray`)
are outside this class.

ORIGIN: non-sentinel index sources are `allocateSynthVoice` (legitimate
by construction if the s3587 contract holds), the packed-handle low
byte whose `-1` writers also zero `+0x0` (s3600), count-bounded loop
counters versus `0x80141AD0`, and the `0x462C` speech-slot word written
from `startStreamedSampleVoice`'s allocator return. No mitigation was
added.
