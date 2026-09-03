# M3 s3607 — remaining speech-file rs_free class

## Work unit

Static census of every generated original `jal rs_free` in
`loadSpeechFile` and `shutdownMusyXVoices`. Remaining audio frees
after the closed speech/cache class: skipped `0x8015467C`
(`lui 0x8015; lw 0x467C`) in both functions, unchecked
`0x80154674` (`lw 0x4674`) in `shutdownMusyXVoices`, and the
`loadSpeechFile` free of the 4-byte header scratch after storing
`0x0($s0)` at `0x80154670`. Classified every original `sw` of each
pointer and whether a free can run on a non-allocator or
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

Closed classes were not repeated: speech/cache `rs_free`, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`,
`+0x60`, MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `lui 0x8015` `lw`/`sw` of `0x467C`/`0x4674`/`0x4670`/
`0x4684` across all `RecompiledFuncs/funcs_*.c`. Hits in
`funcs_15.c` are `lui 0x8004; addiu -0x467C/-0x4670`. Hits in
`funcs_8.c` are `lb -0x4684($zero)`. The `funcs_39.c` hit is
`lui 0x800E; addiu 0x4674`. Those are different objects. Generated
`MEM_W` stores of the four BSS words match the original `sw` list
exactly.

| Pointer | BSS | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| header scratch `$s0` | (stack) | `loadSpeechFile` `rs_malloc(4, 8)` `0x8009BAB0` | that 4-byte DMA header | `loadSpeechFile` `0x8009BAEC` — `addu $a0, $s0; jal rs_free` after `sw 0x0($s0)` to `0x4670` |
| `0x467C` | `0x8015467C` | `initMusyXVoiceTable` `sw $zero` `0x8009BBC8`; DMA `sw $v1` `0x8009BB10` (`$v1` = `rs_malloc(count<<2)`); KSEG0 `sw $v0` `0x8009BB60` (`$v0` = `$s1+4`) | DMA path only | skipped `lw; beq zero` plus `lbu 0x800A5120; beq zero` in `loadSpeechFile` `0x8009BA80` and `shutdownMusyXVoices` `0x8009BD50`; no post-free NULL |
| `0x4674` | `0x80154674` | `initMusyXVoiceTable` `sw $v0` `0x8009BC4C` | `rs_malloc(streamSampleCountToByteSize(0x10E0))` | `shutdownMusyXVoices` `0x8009BD60` — `lw $a0; jal rs_free` (no skip, no post-free NULL) |
| `0x4670` | `0x80154670` | DMA `sw $v0` `0x8009BAE8` (`0x0($s0)`); KSEG0 `sw $v0` `0x8009BB74` (`0x0($s1)`) | not a pointer — count used as `sltu` bound and `sll 2` malloc size | never `rs_free`'d |
| `0x4684` | `0x80154684` | DMA `sw $v0` `0x8009BAA8` (`getAssetRamAddress`); KSEG0 `sw $s1` `0x8009BB58` | not a heap object | never `rs_free`'d |

No other original `0x8015` store of any of the four BSS words exists.
`rs_free` itself `beq $s0, $zero` and returns, so an unchecked
`lw; jal` of never-written BSS zero is a skip, not a Gap.

## Remaining functions

### `loadSpeechFile` (`0x8009BA38`) — header scratch, `0x467C`, flags

Early-out when `lbu 0x800A5121` is zero. Otherwise, if `0x467C` is
nonzero and `lbu 0x800A5120` is nonzero, `jal rs_free` of `0x467C`
with no post-free NULL. Then `(a0 & 0xF0000000) == 0x80000000`
selects the in-RAM path: store `a0` at `0x4684`, `a0+4` at
`0x467C`, `0x0(a0)` at `0x4670`, and `sb $zero` at `0x5120`. The
DMA path `rs_malloc`s 4 bytes into `$s0`, DMAs the header, stores
`0x0($s0)` at `0x4670`, frees `$s0`, `rs_malloc`s `count<<2` into
`0x467C`, DMAs the body, and `sb 1` at `0x5120`.

`$s0` is a matching 4-byte malloc/free. `0x4670` is the copied
count, not a pointer.

The only generated JAL is `initSpeechSubsystem` (`0x80066B90`),
which always calls `initMusyXVoiceTable` first. That init
`sw $zero` of `0x467C`, so the start-of-function `0x467C` free is
skipped on the generated tree. Every generated `initSpeechSubsystem`
passes `a0 = 0` (`addu $a0, $zero, $zero` in the delay slot, or
`0x800AECE4` then no later `a0` clobber in `initCraftSelectScreen`),
so `loadSpeechFile` receives the `findAssetAcrossSegments` result of
name `0x800A05C8`.

### `initMusyXVoiceTable` (`0x8009BBA0`) — zero of `0x467C`, malloc of `0x4674`

The only generated JAL is `initSpeechSubsystem` (`0x80066AA4`).
Stores zero at `0x467C`, `rs_malloc`s `streamSampleCountToByteSize(0x10E0)`
into `0x4674` with no malloc-failure check (the same unproven
allocator-legitimacy edge s3602–s3606 left open, not a second
pointer source), and `sb 1` at `0x5121`. Re-init without a
preceding shutdown overwrites `0x4674` and zeros `0x467C`; that is
a leak, not a Gap.

### `0x800A5120` / `0x800A5121`

`0x5120` is written only by `loadSpeechFile`: `sb 1` after the DMA
malloc store, `sb 0` on the KSEG0 path. The `funcs_13.c` hit is
`lwc1 -0x5120`. `0x5121` is written only by `initMusyXVoiceTable`
(`sb 1`) and `shutdownMusyXVoices` (`sb 0`). All other `0x5121`
sites are `lbu`. The KSEG0 store of `a0+4` at `0x467C` therefore
cannot reach either `0x467C` free: both require `0x5120 != 0`, and
the only writer that sets that flag has already stored the DMA
malloc at `0x467C`.

### `shutdownMusyXVoices` (`0x8009BCC4`) — live destructor

The only generated JAL is `finalizeCurrentSpeechBuffer`
(`0x800678EC`). After stopping slots it `sb $zero` at `0x5121`,
then the same skipped `0x467C` free as `loadSpeechFile`, then
unchecked `lw; jal rs_free` of `0x4674`. Neither word is NULLed
and `0x5120` is not cleared. `rs_free` of BSS zero is a skip.

Generated finalize wrappers and their matching inits, each
init-then-exit-finalize with no nested finalize JAL:

| Wrapper | Init in the same function | Caller |
|---|---|---|
| `cinematicShutdownAudioAndAssets` | `setupCutsceneLevel` on the entry path of `cinematicLoopBody` | `cinematicLoopBody` exit path (`0x800A64EC`), not inside `j L_800A6024` |
| `runMenuRandomBackdropScreen` | `initVwingHudAndSlotState` at entry | `menuOverlayInit` case `L_800C5C44` |
| `menuSubtype02Handler` | `initInteractiveSceneContext` at entry | `menuOverlayInit` case `L_800C5CC0` |
| `menuControllerInput` via `shutdownMenuMessagingAndSpeech` (`a0=1`) | `initVwingHudAndSlotState` at entry; only `jr` is after the `0x8F($sp)==1` exit | `menuOverlayInit` |
| `runHangarMenuFromOverlay` via `gracefulMenuShutdown` | `mallocCraftSelectionData` then the hangar loop | `menuOverlayInit` |
| `drawRadarIcon` via `drainAudioAndFinalizeSpeechBuffer` | `initCraftSelectScreen` then the craft-select loop | `menuOverlayInit` |
| `endMissionCleanup` | `initMission` immediately before in the same block | `mainGameLoop` (two sequential init/cleanup pairs) |

`menuOverlayInit` (`0x800C58A0`) dispatches those screens as
mutually exclusive cases; each jumps to `L_800C5CEC` and does not
call another finalize wrapper. `shutdownMenuMessagingAndSpeech`
skips the speech free when `a0 == 0`; the live site passes `a0 = 1`.

## Sibling-free edge

`0x467C` and `0x4674` are not NULLed after shutdown. Sequential
double-free on the generated call graph is blocked: every live
finalize is the exit of a function that inited in the same
activation, overlay cases do not nest, and a later screen's init
stores a new malloc before its own finalize. A later destructor
would free the latest stored malloc, not a non-allocator value.
Re-init without shutdown leaks the previous `0x4674` and zeros
`0x467C` without freeing a DMA buffer; that is original, not a Gap,
matching s3604's `reapplyAudioConfig` overwrite and s3606's
cinematic-to-menu SND leak.

The KSEG0 store of `a0+4` is a non-allocator writer of `0x467C`,
but both frees skip when `0x5120 == 0`. That is not a concrete
stale-free of a non-allocator pointer.

Live consumers (`allocAndConfigureNewVoice` of `0x4670` as a count
bound, `0x467C` as a table base, and `0x4674` copied to slot
`+0x1210`) continue to load those words; their lifetime versus
either free remains the unproven allocator/lifetime boundary s3602
already parked.

## Result

`H-NextClassComplete` is selected. The 4-byte `$s0` scratch is a
matching malloc/free. `0x4674` is the matching
`initMusyXVoiceTable` malloc store; shutdown frees that same word
and sequential double-free is blocked by the generated
init/finalize pairing. `0x467C` is either that pairing's DMA malloc
or a KSEG0 interior pointer that both frees skip via `0x5120`.
`H-NextClassGap` is not selected: no free can pass the KSEG0
interior pointer, and no concrete sibling-free of a non-allocator
or already-freed value is exposed. `H-NextClassUnevaluable` is not
selected: the three BSS words and the header scratch are plain
slots with classified writers.

This is static evidence. Runtime allocator state, `0x5120`/`0x5121`
on the validated route, re-init overwrite, and live contents after
either free remain unproven, matching s3586–s3606. No guard or
runtime change is authorized.

ORIGIN: writers are `loadSpeechFile` (`$s0` from `rs_malloc(4, 8)`;
DMA `rs_malloc(count<<2)` of `0x467C`; KSEG0 `a0+4` of `0x467C`
with `0x5120=0`) and `initMusyXVoiceTable` (zero of `0x467C`;
`rs_malloc` of `0x4674`). No mitigation was added.
