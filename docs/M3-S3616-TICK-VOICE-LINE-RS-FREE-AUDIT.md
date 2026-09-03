# M3 s3616 — remaining tickMultiPartVoiceLine rs_free of $s0

## Work unit

Static census of every generated original `jal rs_free` in
`tickMultiPartVoiceLine`. Remaining funcs_37 voice-line free
after the closed model-viewer mesh-chain class: `0x800CBF04` of
`$s0` (`$a0` of the tick). Classified the pointer's writer and
whether a free can run on a non-allocator or already-freed
value, including `mallocVoiceLineStruct`'s `rs_malloc(0x24)` at
`0x800CBF88` and every original store of that return. No build
or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `sw` of the pointer:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table, loadCharTextureSet
DMA-array, load_asset-then-free, texture-scratch `rs_free`,
text-texture `rs_free`, format-message `rs_free`, speech-file
`rs_free`, speech/cache `rs_free`, destructor skipped-NULL,
destructor unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `tickMultiPartVoiceLine`: one site,
this class. `funcs_37.c` still has later `rs_free` in
`npcAtAtUpdate`, `npcAtStUpdate`, and `playerAtStUpdate`.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| hangar/craft voice line | `0x800CDA18` (`0x800D-0x25E8`) | `craftSelectionVoiceLineHelper` `sw $v0, -0x25E8($s3)` `0x800AE3B4` (`$s3=0x800D`); `mallocCraftSelectionData` `sw $zero` `0x800A941C`; hangar tick `sw $zero` `0x800AAF18` | `mallocVoiceLineStruct` `rs_malloc(0x24)` `0x800CBF88` | tick `0x800CBF04` of `$s0`; callers NULL on return 1 |
| craft-select voice line | `0x800CDFB0` (`0x800D-0x2050`) | `startSlotLoopAnimWithVoiceSync` `sw $v0, -0x2050($s1)` `0x800B1C10` and `0x800B1D28` (`$s1=0x800D`); `initCraftSelectScreen` `sw $zero` `0x800AED5C`; timed-fade tick `sw $zero` `0x800B2550` | same `rs_malloc(0x24)` | same `0x800CBF04`; callers NULL on return 1 |
| menu voice line | `0x800CF154` (`0x800D-0xEAC`) | `menuControllerInput` `sw $v0, -0xEAC` `0x800B5F9C` and `0x800B78C8`; `initVwingHudAndSlotState` `sw $zero` `0x800B95B4`; menu tick `sw $zero` `0x800B7C8C`; backdrop tick `sw $zero` `0x800BFDFC` | same `rs_malloc(0x24)` | same `0x800CBF04`; callers NULL on return 1 |

Those three words are the only original stores of the malloc
return as a heap pointer. `rs_free` itself `beq $s0, $zero`
at `0x80001CA4` and returns, so a NULL `$a0` is a skip, not a
Gap. Tick also `beq $s0, $zero` at entry and returns 1 without
calling `rs_free`.

## Remaining function

### `tickMultiPartVoiceLine` (`0x800CBE00`) — one free

Frame is `-0x28`. `$a0` is the 0x24-byte line; `$a1` is dt
(`mtc1` into `$f2`). `$s0 = $a0`.

1. If `$s0` is NULL, return 1 (`L_800CBF48`).
2. If `+0x1E == 1` (loop/fade, set by `setVoiceLineLoopFlag`):
   - If `+0x1C == 0`, fall through to `L_800CBF04` and
     `jal rs_free` of `$s0`, then return 1.
   - Else add dt into `+0x20`, clamp to `0x800A7BD0`, call
     `applySpeechVolumeScalar`. If fade has not reached the
     clamp, return 0. If it has, `stopSpeechSlotIfActive(+0x1C)`
     and return 1 **without** freeing.
3. Else if `+0x1D != 0` (clip playing):
   - If `+0x1C != 0`, `isSpeechSlotActive(+0x1C)`; inactive
     zeros `+0x1C`. Return 0 either way.
   - If `+0x1C == 0`, add dt into `+0x4`; when `+0x4` exceeds
     duration `+0x0`, zero `+0x4` and `+0x1D`. Return 0.
4. Else (`+0x1D == 0`):
   - If `+0x1A == +0x18` (index == count), `L_800CBF04` frees
     `$s0` and returns 1.
   - Else `enqueueSpeechClip` of `+0x8[index]` with bank
     `+0x1B`, store the slot at `+0x1C`, set `+0x1D = 1`,
     increment `+0x1A`, return 0.

Tick never writes the caller's slot. Return 1 is the "done"
signal; every generated caller NULLs its slot on that value.

## Matching init

### `mallocVoiceLineStruct` (`0x800CBF60`) — only allocator

`$a0` is a `u16` clip-id list terminated by `0xFFFF`, `$a1` is
the duration float in a GPR, `$a2` is the bank/voice id.
`rs_malloc(0x24)` at `0x800CBF88` (`$a1` flags 0) is captured
in `$s1`. The function does not NULL-check `$v0` before the
init stores. It writes:

- `+0x1B = $a2`, `+0x1A/+0x1C/+0x1D/+0x1E = 0`
- `+0x4 = 0`, `+0x20 = 0`, `+0x0 = duration`
- copies clip ids into `+0x8` until `0xFFFF`, `+0x18 = count`

Returns `$s1`. No generated path stores that return except the
three slot words above.

Generated `jal 0x800CBF60` (five sites):

| Site | Function | Live-slot skip | Store |
|---|---|---|---|
| `0x800AE3AC` | `craftSelectionVoiceLineHelper` | `bne -0x25E8, L_800AE3CC` | `-0x25E8` |
| `0x800B1C00` | `startSlotLoopAnimWithVoiceSync` | `bne -0x2050, L_800B1C28` | `-0x2050` |
| `0x800B1D18` | `startSlotLoopAnimWithVoiceSync` | `bne -0x2050, L_800B1D38` | `-0x2050` |
| `0x800B5F80` | `menuControllerInput` | none | `-0xEAC` |
| `0x800B78BC` | `menuControllerInput` | `bne -0xEAC, L_800B78D0` | `-0xEAC` |

The `0x800B5F80` store can overwrite a live menu slot. That
leaks the previous `rs_malloc(0x24)`; the new return is the
value later ticked and freed. It is not a second pointer
source for the free.

## Tick callers — NULL on return 1

Generated `jal 0x800CBE00` (four sites). Each loads one of
the three slots, skips NULL, and `sw $zero` on return 1:

| Site | Function | Slot load | NULL store |
|---|---|---|---|
| `0x800AAEF0` | `runHangarSelectionFrame` | `-0x25E8` | `0x800AAF18` |
| `0x800B253C` | `tickTimedScreenFadeFloat` | `-0x2050` | `0x800B2550` |
| `0x800B7C5C` | `menuControllerInput` | `-0xEAC` | `0x800B7C8C` |
| `0x800BFDD0` | `runMenuRandomBackdropScreen` | `-0xEAC` | `0x800BFDFC` |

No generated `jal 0x800CBE00` passes a non-slot pointer.
`setVoiceLineLoopFlag` (`0x800CC02C`) only `sb 1, +0x1E($a0)`
and every generated caller loads the same slot with a NULL
skip first. Overlay clone `funcs_49.c` `static_5_800AF6AC`
repeats `tickCraftSelectScreen`'s loop-flag load of `-0x2050`;
it does not tick or malloc.

## Pairing / double-free

Sequential double-free of a live line is blocked by return-1
plus the caller's NULL. The next tick loads NULL and returns
without `jal rs_free`. Hangar and craft-select mallocs refuse
to store over a live slot. Menu malloc2 does the same. Menu
malloc1 and the three screen-init `sw $zero` stores
(`mallocCraftSelectionData` `-0x25E8`, `initCraftSelectScreen`
`-0x2050`, `initVwingHudAndSlotState` `-0xEAC`) can leak a
still-live line; they do not hand a non-allocator pointer to
the free.

The `+0x1E == 1 && +0x1C != 0` completion path returns 1
without freeing, and the caller still NULLs. That leaks the
0x24 object. The free that does run (no slot, or index ==
count) still receives the matching `rs_malloc(0x24)`.

`attachedAudioVisualEmitterNpcHandler`'s `lwc1 -0x25E8($at)`
uses `$at = 0x8004`, not `0x800D`.

Re-init without a done-tick, a first-malloc failure, and the
fade-complete leak are the same unproven re-init / allocator
edges s3604–s3615 left open, not a second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: no non-allocator last writer of the
three slots, and sequential double-free is blocked by the
return-1 NULL. `H-NextClassUnevaluable` is not selected: `$s0`
is the 0x24 voice-line object from `mallocVoiceLineStruct`.
