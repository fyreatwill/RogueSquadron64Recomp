# M3 s3600 — unmasked release/fade voice-table index

## Work unit

Static census of every generated caller of `musyxStartVoiceRelease` and
`beginVoiceFadeRelease`, and of every `MEM_BU(..., 0x67)` load in
`funcs_22.c` through `funcs_24.c` that can become their voice-table index.
No build or runtime run was performed.

The discriminator was the complete caller / `+0x67` / packed-handle writer
/ `-1` ordering / `0x88`-table bound chain:

- H-NextClassGap: a live release/fade call can pass `0xFF` from the `-1`
  packed-handle low byte, or another out-of-range index, into the `0x88`
  voice table.
- H-NextClassComplete: every caller argument is a slot below the live
  count or is structurally gated before the JAL, and only runtime
  allocator legitimacy remains.
- H-NextClassUnevaluable: aliases or mixed layouts prevent a complete
  object-level classification of the index source.

## Census size

Four generated call sites plus the two consumer definitions. Seven
`MEM_BU(..., 0x67)` loads in `funcs_22.c`/`funcs_23.c`. No `MEM_B` store
to `+0x67` exists anywhere in the generated tree; the byte is only written
as the low byte of the packed-handle word at record `+0x64`.

`soundMacroOpKeyOff` has no generated JAL. Opcode 17 of `tickAudioChannel`
inlines the same `lbu 0x67 / a1=1` body.

## Consumers

Both functions form `slot = D_801496F8 + a0 * 0x88` from
`lui 0x8015; lw -0x6908` and `(a0 << 4) + a0 << 3`. Neither masks `a0`
and neither compares it to the mix live-count halfword at `0x8015:-0x6900`
or the slot-count byte at `0x80141AD0`.

`musyxStartVoiceRelease` (`0x80092274`) has no KSEG0 guard. It always
stores `0x14` at `+0x30`. When `a1 != 0` it also copies float `+0x5C` to
`+0x68`, zeros `+0x64`/`+0x60`, sets phase `+0x6C` to `3`, and copies
`+0x30` into `+0x58`.

`beginVoiceFadeRelease` (`0x80092490`) has the existing s484 KSEG0 guard
on the table **base**, not on the index. Inactive slots (`+0x0 == 0`)
return without writing. If `+0x1 != 0` it stores `0x14` at `+0x30`,
clears `+0x1`, and skips the envelope block; otherwise it performs the
same envelope stores as release.

Attack (`musyxTriggerVoiceAttack`) still masks `a0` to 16 bits. The
callers below pass an 8-bit `lbu` or a count-bounded loop counter, so
that 16-bit difference is not a caller-side overflow on these edges.

## Direct callers

| Site | Function | `a0` construction | Gate |
|---|---|---|---|
| `0x8008C464` | `tickAudioChannel` opcode 17 | `lbu a0, 0x67(s0)`; `a1=1` | Parent `tickAllAudioChannels` skips `record+0x0==0`. Opcode is `andi 0x7F` then `sltiu 0x51` before the jump table; case 17 is in range. |
| `0x8008A6CC` | `soundMacroOpKeyOff` | `lbu a0, 0x67(a0)`; `a1=1` | Same load. No generated caller. |
| `0x8008DB98` | `stopVoicesByHandle` | `s1 = handle & 0xFF` after rejecting full-word `-1` | Fade runs after the `0x17C` record is cleared to `-1`, but `a0` is the pre-clear slot, not the sentinel word. Callee `+0x0==0` still applies. No local count check. |
| `0x8008DCC4` | `stopAllSynthVoices` | loop `s4 = 0 .. count-1` from `0x80141AD0` | Count-bounded. Inactive records still JAL; callee `+0x0==0` returns. |

`tickAudioChannel` is reached only from `tickAllAudioChannels`
(`0x8008CA14`), which walks `D_8013D880` with stride `0x17C`, bounded by
the same slot-count byte, and skips a record whose word at `+0x0`
(`-0x2780`) is zero.

The interpreter done-gate at `L_8008C8E8` treats `a0 & 0xFF == 0` as
"fetch next opcode" and nonzero as "return". Opcode 0 (stop) writes `-1`
to `+0x64` and sets `a0=1`, so it cannot fall through to opcode 17 in the
same tick. Opcode 17 sets `a0=0` after release, so it continues, but it
does not itself publish `-1`.

## `+0x67` loads that do not feed release/fade

These share the packed-handle low byte and the same `0x88` index formula
in their callees, but they are not this class's JALs:

| PC | Function | Callee |
|---|---|---|
| `0x8008BC50` | `tickAudioChannel` (`flags & 1`) | `stopVoiceMarkRetrigger` |
| `0x8008C940` | `tickAudioChannel` | `isAudioSlotActive` |
| `0x8008962C` | `computeChannelWaitDuration` | `isAudioSlotActive` |
| `0x8008A548` | `soundMacroOpPlaySampleKeymap` | `musyxInitVoiceFromSample` |
| `0x8008A9D8` | `musyxSetVoiceAdsrFromTable` | `musyxStoreVoiceAdsrParams` |

`funcs_21.c` `r29+0x67` loads are stack spills. `funcs_39.c` is outside
the requested window.

## Packed-handle writers versus the `-1` sentinel

On a `0x17C` record, `+0x64` is the packed handle whose big-endian low
byte is `+0x67` (s3586). The complete generated writer set for that word:

| Writer | Value | `+0x0` pairing |
|---|---|---|
| `startNoteOnVoice` `0x80087294` | `((hi16) << 16) \| ((a2 & 0xFF) << 8) \| slot` | Publishes only after `allocateSynthVoice` returns a non-`-1` slot. Failure jumps to `L_8008739C` before any handle store. |
| `stopVoiceByKey` | `-1` | cleanup |
| `soundMacroOpStopVoice` | `-1` | zeros `+0x0` first |
| `soundMacroOpReturnFromGosub` cleanup | `-1` | zeros `+0x0` first |
| `soundMacroOpGosub` lookup-fail | `-1` | zeros `+0x0` first |
| `tickAudioChannel` opcode 0 | `s1`, which is `-1` from `0x8008BF1C` | zeros `+0x0` first, then exits the interpreter |
| `releaseSynthVoice` | `-1` | zeros `+0x0` in the same function |
| `stopVoicesByHandle` | `-1` | zeros `+0x0` before the fade JAL |
| `stopAllSynthVoices` | `-1` | zeros `+0x0` before the fade JAL |
| `resetMusyXEngineState` | `-1` | also stores `0` at `-0x2780` (`+0x0`) |

Every sentinel writer therefore leaves `record+0x0 == 0`, which is the
exact skip used by `tickAllAudioChannels` before the key-off JAL. Fade
from `stopVoicesByHandle` uses the matched live slot, not the sentinel
just stored. Fade from `stopAllSynthVoices` uses the count-bounded
counter.

A live packed handle with low byte `0xFF` would require the allocator to
return slot 255. `allocateSynthVoice` returns `-1` or an index below the
slot-count byte (s3587); that byte is the same bound as the two fade
loops.

## Result

`H-NextClassComplete` is selected for this idiom. Every generated
release/fade edge is either count-bounded or structurally gated so that
the `-1` sentinel cannot be the index of a live JAL. Layout identity of
`+0x67` as the packed-handle low byte is already closed by s3586.

`H-NextClassGap` is not selected: no concrete out-of-range or
sentinel-as-index writer/call pair was found. `H-NextClassUnevaluable` is
not selected: the four call sites, the `+0x67` loads, and the handle
writers are one object (the `0x17C` record's packed handle feeding the
`0x88` table).

This is static evidence. Runtime allocator state, record lifetime, and
the live slot-count byte remain unproven, matching s3586–s3588. No guard
or runtime change is authorized. The consumers' missing local count check
is a missing bound, not a demonstrated invalid value.

The sibling unmasked `0x88`-stride indexers (`isAudioSlotActive`,
`stopVoiceMarkRetrigger`, `musyxInitVoiceFromSample`,
`musyxStoreVoiceAdsrParams`, `musyxStopVoice`, `musyxSetVoicePitchBend`,
`deactivateVoice`, `getVoiceUserField`) are outside this class.

ORIGIN: the only non-sentinel writer of the index byte is
`startNoteOnVoice` at `0x80087294`; the value is legitimate by
construction if the allocator contract holds. Cleanup writers
deliberately publish `-1` together with `+0x0 = 0`. No mitigation was
added.
