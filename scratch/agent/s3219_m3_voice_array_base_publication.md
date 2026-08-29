# Session 3219 — M3 voice-array base publication census (A9)

## Discriminator

The joined static table was every generated store and load of the voice-array
base at `D_801496F8` (`lui 0x8015` / `-0x6908`), the address-of encodings
`lui 0x8014` / `0x96F8` and a literal `0x801496F8`, caller fan-in, and the
companion symbol metadata. Competing outcomes:

- `H-NamedProducersOnly`: every store is in the named allocate/reset family
  and loads are range-checked or null-safe.
- `H-InvalidPublisher`: at least one generated store writes a non-KSEG0 or
  overlapping distinct base that the existing A9 guard is papering over.
- `H-NoLiveBase`: no remaining generated publication beyond already-named
  sites.

No port run. No new guard without a named illegitimate writer.

Positive control for this static census: the companion independently names
`allocateSongChannelArray` at `0x8008F0A0`, `initN64RspMixer` at
`0x8009189C`, and the RSP-mixer voice-slot array as base `0x801496F8` with
stride `0x88`; those addresses and the `count * 136` size in the generated
allocator match.

## Publication table

| Guest PC | Generated function | Operation | Contract evidence | Classification |
|---|---|---|---|---|
| `0x8008F0CC` | `allocateSongChannelArray` | `sh $s0, D_80149700` (count) | `$s0` is the voice-count argument; `initN64RspMixer` clamps it to `0x20` before the call | Legitimate count publish |
| `0x8008F0E4` | `allocateSongChannelArray` | `sw $v0, D_801496FC` | Same first `rs_malloc` result as the base; used by the init-zero loop and by `shutdownAudioEngine`'s free | Same-malloc alias, not a second base |
| `0x8008F0EC` | `allocateSongChannelArray` | `sw $v0, D_801496F8` | First `rs_malloc` (`jal 0x80001ACC`) of `count * 0x88` bytes. Later mallocs in the same function store to `D_80149758`/`D_8014975C`/`D_80149708`/`D_8014970C`/`D_80149764`, not this slot. No success check; a failed malloc would publish `0` | Sole live base publisher |

The exact generated search found no additional store:

- one `sw …, -0x6908` and one `MEM_W(-0x6908, …) =` in the whole
  `RecompiledFuncs/funcs_*.c` tree, both at `0x8008F0EC`
- zero `sw …, 0x96F8` and zero literal `0x801496F8` stores
- two `addiu …, -0x6908` hits in `funcs_45.c` are `lui $a0, 0x800B` dat-item
  addresses (`0x800A96F8`), not this global

There is no generated reset/zero store to `D_801496F8`.
`shutdownAudioEngine` at `0x80091E48` frees the `D_801496FC` alias and does
not republish or clear the base.

## Caller fan-in

| Guest PC | Function | Edge |
|---|---|---|
| `0x80091934` | `initN64RspMixer` | sole caller of `allocateSongChannelArray`; clamps count `< 0x21` else `0x20` |
| `0x80091C58` | `initAudioSubsystem` | calls `initN64RspMixer` |
| `0x80091D14` | `reapplyAudioConfig` | calls `initN64RspMixer` |
| `0x8008EA78` | `setDisplayMode` | calls `initAudioSubsystem` |
| `0x8008EBC0` | `reapplyDisplayMode` | calls `reapplyAudioConfig` |

Companion `main_overlay.txt` independently describes this same install path
(`initN64RspMixer` clamps voiceCount to `0x20` and installs the mixer;
`reapplyAudioConfig` is the runtime counterpart with one caller in
`reapplyDisplayMode`).

## Load table (A9 consumers)

| Guest PC | Generated function | Guard | Notes |
|---|---|---|---|
| `0x80090E78` | `musyxMixActiveVoices` | `AUDIO_VOICE_BASEPTR_LOOP_GUARD` | loop-head skip |
| `0x80090EA0`, `0x80090EBC` | `musyxMixActiveVoices` | transitive on the loop-head guard | same iteration |
| `0x800913BC` | `musyxSynthFrame` | `AUDIO_VOICE_BASEPTR_LOOP_GUARD` | loop-head skip |
| `0x80092100` | `isAudioSlotActive` | `AUDIO_SLOT_ACTIVE_GUARD` (s166) | KSEG0 early return, not the A9 named pair |
| `0x80092138` | `musyxInitVoiceFromSample` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | first reload |
| `0x8009219C`, `0x800921D0`, `0x80092258` | `musyxInitVoiceFromSample` | transitive | no rewrite of the global |
| `0x80092278` | `musyxStartVoiceRelease` | none | indexed `base + idx*0x88` then field stores |
| `0x800922C8` | `musyxStoreVoiceAdsrParams` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |
| `0x80092328` | `musyxTriggerVoiceAttack` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |
| `0x8009236C` | `musyxStopVoice` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |
| `0x800923A4`, `0x800923C0` | `musyxSetVoicePitchBend` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` (both branches) | |
| `0x800923FC` | `setVoiceModulationParams` | none | indexed `base + idx*0x88` then field addresses |
| `0x80092450` | `stopVoiceMarkRetrigger` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |
| `0x80092478` | `stopVoiceMarkRetrigger` | transitive | |
| `0x80092494` | `beginVoiceFadeRelease` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |
| `0x800924F4` | `deactivateVoice` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |
| `0x80092568` | `getVoiceUserField` | `AUDIO_VOICE_BASEPTR_ENTRY_GUARD` | |

Host-only `MEM_W(-0x6908, …)` reads inside diagnostic patches
(`musyxRenderVoiceSamples`, drain-path probes, `funcs_23.c`/`funcs_26.c`/
`funcs_30.c`) are not game loads or stores.

The two unguarded consumers are reachable readers of the named base, not
publishers. They do not authorize a new guard: no illegitimate writer was
identified.

## Decision

`H-NoLiveBase` is refuted: `allocateSongChannelArray` at `0x8008F0EC`
publishes the malloc result into `D_801496F8`. `H-InvalidPublisher` is not
selected at generated-source scope: the only store is that malloc result, the
`D_801496FC` word is a same-value alias, and later allocator mallocs target
other globals. `H-NamedProducersOnly` is selected for publication.

Load-side range checks are incomplete (`musyxStartVoiceRelease`,
`setVoiceModulationParams` have no KSEG0 skip). That is consumer coverage,
not a second publisher, so the existing A9 guards stay safety machinery
rather than an explanation of a wild published value.

This is static evidence only. A9's remaining retail/port in-range and
downstream voice/slot-effect requirement is still blocked on a
target-phase M5 route; this census does not relax or add a guard.

ORIGIN: generated guest-PC store/load census plus independent companion
symbol metadata; no mitigation or runtime behavior change was made.
