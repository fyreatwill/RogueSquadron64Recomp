# M3 s3606 — remaining speech/cache rs_free class

## Work unit

Static census of every generated original `jal rs_free` in
`waitForAnyAudioSlot`, `freeAudioCacheEntry`, and
`finalizeCurrentSpeechBuffer`. Remaining audio frees after the
closed destructor skipped-NULL and unchecked classes: unchecked
`-0x64AC`, `-0x64B0`, `-0x64B4` in `waitForAnyAudioSlot`, the two
`freeAudioCacheEntry` frees of cache `+0x4`, and skipped `-0x648C`
in `finalizeCurrentSpeechBuffer`. Classified every original `sw` of
each pointer and whether a free can run on a non-allocator or
already-freed value. No build or runtime run was performed.

The discriminator was the single complete original census of those
`jal rs_free` sites plus every original `sw` of each pointer:

- H-NextClassGap: a remaining free can pass a pointer that is not
  the matching allocator store, or can free it after a sibling
  already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of a
  matching init store, and only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object identities or unshared writers
  prevent a complete classification of a pointer source.

Closed classes were not repeated: destructor skipped-NULL, destructor
unchecked-free, `-0x6904` alias, remaining-indexer, `-0x6908`
non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `lui 0x8014` `lw`/`sw` of `-0x64AC`/`-0x64B0`/`-0x64B4`/
`-0x648C` and original `lui 0x8014; addiu -0x6600` cache-table
accesses across all `RecompiledFuncs/funcs_*.c`. Hits in `funcs_25.c`
use `lui 0x8015` and are different objects. Generated `MEM_W` stores
of the four BSS words match the original `sw` list exactly.

| Pointer | BSS | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| `-0x64AC` | `0x80139B54` | `loadSndFiles` delay-slot `sw $v0` `0x8006640C` | `load_asset_with_malloc_flags` `rs_malloc` of name `0x8003C72C` | `waitForAnyAudioSlot` `0x800668E4` — `lw $a0; jal rs_free` (no skip, no post-free NULL) |
| `-0x64B0` | `0x80139B50` | `loadSndFiles` delay-slot `sw $v0` `0x80066424` | same loader of name `0x8003C73C` | wait `0x800668F4` |
| `-0x64B4` | `0x80139B4C` | `loadSndFiles` `sw $v0` `0x80066448` | same loader of name `0x8003C74C` | wait `0x80066904` |
| cache `+0x4` | `0x80139A00` + `i*8+4`, 16 entries | `loadSongAssetByName` `sw $v0, 0x4($s2)` `0x80066654`; keys inited to `-1` by `loadSndFiles` | `rs_malloc` after `get_asset_size_extra` | `freeAudioCacheEntry` `0x800669A4` (a0==-1 walk) and `0x800669E4` (matching-key walk); both `sw -1` at the key, not the pointer |
| `-0x648C` | `0x80139B74` | `initSpeechSubsystem` `sw $zero` `0x80066B60` (a0==0 DMA path); `sw $a0` `0x80066B8C` (`$a0` = `load_asset` `$v0`, a0!=0 path) | `load_asset` `rs_malloc` on the a0!=0 path only | `finalizeCurrentSpeechBuffer` `0x80067904` — `lw $a0; beq $a0, $zero; jal rs_free` (no post-free NULL) |

No other original `0x8014` store of any of the four BSS words exists.
No other original `0x8014 -0x6600` store of cache `+0x4` exists.
`parseLoadedSndSection` and `initLevelMusicBank` load the three SND
words as parse arguments; they do not store a replacement.
`findAudioChannelById` loads cache `+0x4` as a lookup return.

`rs_free` itself `beq $s0, $zero` and returns, so an unchecked
`lw; jal` of never-written BSS zero is a skip, not a Gap.

## Remaining functions

### `load_asset_with_malloc_flags` (`0x800647E0`) / `load_asset` (`0x8006488C`)

Both call `get_asset_size_extra`, `rs_malloc` that size, DMA into
the buffer, `teardownAssetDma`, and return the malloc pointer in
`$v0` (`$s2`). There is no malloc-failure check before the return;
that is the same unproven allocator-legitimacy edge s3602–s3605 left
open, not a second pointer source.

### `loadSndFiles` (`0x800663B0`) — three SND words and cache keys

Walks the 16 cache keys at `0x80139A00` down from entry 15 and stores
`-1`. Then three `load_asset_with_malloc_flags` calls; delay-slot /
fall-through stores put those `$v0` results at `-0x64AC`, `-0x64B0`,
and `-0x64B4`. `parseSndFiles` consumes the three pointers. Generated
callers are `initSceneForMission`, `menuOverlayInit`, and
`initMission`.

### `waitForAnyAudioSlot` (`0x800668B0`) — unchecked triple free

`tickMusyXIfActive`, then spin on `anyAudioSlotActive` until
nonzero. If `lbu 0x80130B39` is nonzero, skip the three frees;
else `lw $a0; jal rs_free` of `-0x64AC`/`-0x64B0`/`-0x64B4` with
nop delay slots (the loaded word is passed) and no post-free NULL.

`cinematicLoopBody` is the looping caller, but the wait is on the
exit path (`0x800A64D4`), not inside `j L_800A6024`. Setup stores
`1` at `0x80130B39` (`0x800A5EA0`) and the exit path stores `0`
(`0x800A6568`) *after* the wait, so the cinematic wait always sees
the skip flag and does not free. The other generated wait sites
pair a matching `loadSndFiles` in the same caller:
`menuOverlayInit` loads then waits; `mainGameLoop` calls
`initMission` (which loads) then `endMissionCleanup` (which waits).
A cinematic-to-menu `loadSndFiles` overwrite without a preceding
free leaks the cinematic buffers; that is original, not a Gap.

### `loadSongAssetByName` (`0x8006657C`) — cache constructor

First walk returns success if the key is already present. Else it
finds a `-1` slot, `rs_malloc`s, `sw $v0, 0x4($s2)`, DMA-fills, then
`sw $s4, 0x0($s2)` of the key. Generated callers are the menu/level
song preload family (`cueMenuScreenAudioA/B/C`,
`preloadMenuMusicSetA`, `initLevelMusicBank`,
`preloadSceneReferencedSongs`, `tickSongAssetLoadWorker`,
`mallocCraftSelectionData`, `initCutsceneAudioChannels`,
`initCraftSelectScreen`, `runModelViewerSoundDemo`).

### `freeAudioCacheEntry` (`0x80066960`) — keyed table free

16 entries of `{key, ptr}`. `a0 == -1` walks every occupied key
(`key != -1`), frees `+0x4`, and stores `-1` at the key. `a0 != -1`
frees matching keys the same way. Both generated callers
(`menuSubtype02Handler`, `stopMusicAndResetAudio`) pass `a0 = -1`.
The pointer word is not NULLed, but a later free-all sees `key == -1`
and skips, so sequential double-free of the same occupancy is
blocked.

### `initSpeechSubsystem` (`0x80066A90`) / `finalizeCurrentSpeechBuffer` (`0x800678E4`)

Incoming `a0` byte 0 takes `findAssetAcrossSegments` of
`0x800A05C8`, stores the DMA handle at `-0x6490`, and stores zero at
`-0x648C`. Nonzero `a0` indexes that name table and `load_asset`s,
then stores the malloc pointer at `-0x648C`. Every generated
`initSpeechSubsystem` site passes `a0 = 0` (`setupCutsceneLevel`,
`mallocCraftSelectionData`, `initCraftSelectScreen` after
`addu $a0, $zero, $zero` at `0x800AECE4`, `initVwingHudAndSlotState`,
`initInteractiveSceneContext`, `initMission`). The malloc store is
therefore unreferenced in the generated tree.

`finalizeCurrentSpeechBuffer` calls `shutdownMusyXVoices`, then
`lw $a0, -0x648C; beq $a0, $zero` to `teardownAssetDma` of
`-0x6490`, else `jal rs_free` with no post-free NULL. On the
generated a0==0 path the skipped free is of BSS/init zero. Generated
finalize callers (`gracefulMenuShutdown`,
`cinematicShutdownAudioAndAssets`, `drainAudioAndFinalizeSpeechBuffer`
from the craft-select exit in `drawRadarIcon`,
`runMenuRandomBackdropScreen`, `menuSubtype02Handler`,
`shutdownMenuMessagingAndSpeech`, `endMissionCleanup`) therefore
cannot `rs_free` a live malloc of `-0x648C`.

## Sibling-free edge

The three SND words are not NULLed after `waitForAnyAudioSlot`.
Sequential double-free on the generated call graph is blocked: the
cinematic wait is skipped by `0x80130B39`, and the two B39-clear
waits each follow a `loadSndFiles` in the same init/cleanup pair.
A later destructor would free the latest stored malloc, not a
non-allocator value. The cinematic-to-menu overwrite is a leak, not
a Gap, matching s3605's `reapplyAudioConfig` overwrite.

Cache `+0x4` is not NULLed, but the key is set to `-1` before any
sibling can see the occupancy. That is not a concrete stale-free of
a non-allocator pointer.

`-0x648C` is NULLed only by the a0==0 init store. The skipped
finalize free on the generated path is of that zero. The unreferenced
a0!=0 malloc path would lack a post-free NULL; no generated caller
takes it.

Live consumers (`parseLoadedSndSection`, `initLevelMusicBank`,
`findAudioChannelById`) continue to load those words; their lifetime
versus either free remains the unproven allocator/lifetime boundary
s3602 already parked. The `anyAudioSlotActive` spin in
`waitForAnyAudioSlot` is outside this free class.

## Result

`H-NextClassComplete` is selected. `-0x64AC`/`-0x64B0`/`-0x64B4`
are the matching `load_asset_with_malloc_flags` stores;
`waitForAnyAudioSlot` frees those same words after a B39 skip or a
paired `loadSndFiles`. Cache `+0x4` is the matching
`loadSongAssetByName` malloc store; `freeAudioCacheEntry` frees it
and marks the key `-1`. `-0x648C` is init-zero on every generated
caller, so the skipped finalize free is of BSS/init zero.
`H-NextClassGap` is not selected: no untrusted load and no concrete
sibling-free of a non-allocator pointer. `H-NextClassUnevaluable` is
not selected: the four BSS words and the 16-entry cache are plain
pointer slots with a single nonzero malloc writer each.

This is static evidence. Runtime allocator state, B39 on the
validated route, cinematic-to-menu overwrite, and live contents
after either free remain unproven, matching s3586–s3605. No guard or
runtime change is authorized.

ORIGIN: writers are `loadSndFiles` (`-0x64AC`/`-0x64B0`/`-0x64B4`
from `load_asset_with_malloc_flags` `rs_malloc`),
`loadSongAssetByName` (cache `+0x4` `rs_malloc`), and
`initSpeechSubsystem` (zero of `-0x648C` on the generated a0==0
path; unreferenced `load_asset` store on a0!=0). No mitigation was
added.
