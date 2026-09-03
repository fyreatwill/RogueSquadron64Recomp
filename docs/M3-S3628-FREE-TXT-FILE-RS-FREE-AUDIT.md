# M3 s3628 — freeTxtFile globals rs_free

## Work unit

Static census of `freeTxtFile` `jal rs_free` at `0x800558F8`
(`$a0` = `*0x8009ECA0` / `-0x1360($s3)` with `$s3=0x800A0000`)
and `0x80055910` (`$a0` = `*0x8009ECA8` / `-0x1358($s2)`).
Enumerated every original load/store of those two words
(including `loadVoiceTxtFile` / `loadTxtFile` and any other
writer) and every `jal rs_free` that can receive them.
Classified each pointer's writer and whether a free can run
on a non-allocator or already-freed value. The following
`teardownAssetDma` of `*0x8009ECA4` when that word is not
`-1` is a sibling lifetime edge, not a third `rs_free`. No
build or runtime run was performed.

The discriminator was the single complete original census of
those two `jal rs_free` sites plus every original `lw`/`sw`
of `0x8009ECA0` and `0x8009ECA8` (including `-0x1360`/
`-0x1358` from `0x800A0000`) and every `jal rs_free` that
can receive either word:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadSpriteSheetTextureFrames
inlined-malloc, loadAndRelocateAsset load_asset,
loadExplosionTextures load_asset, freeEffectAssetBuffers
globals, loadSkyHorizonHob stack scratch,
cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
spawnCutsceneObjectsFromList 0x6C, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor `+0x4C`, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`,
speech/cache `rs_free`, destructor skipped-NULL, destructor
unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table,
pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_12.c`: 10 sites. Two are
this class (`0x800558F8`, `0x80055910`). The other eight are
`loadSpriteSheetTextureFrames` `0x80055450` (closed s3627),
`loadAndRelocateAsset` `0x800555C4` (closed s3626),
`freeSubtitleOverlay` `0x800562CC`,
`load_hmt_and_hob` `0x80056798`/`0x80056D60`/`0x80056D6C`,
`releaseMeshAsset` `0x8005794C`, and
`freeAllHobFiles` `0x80059244`. None of those eight loads
`0x8009ECA0` or `0x8009ECA8`.

No absolute `0x8009ECA0`/`0x8009ECA8` encodings exist as
`lw`/`sw` in the generated tree. Every `-0x1360`/`-0x1358`
site uses `lui 0x800A` as the base, so all hits are these
two words. The `funcs_27.c` bytes at those VAs are data
words mis-disassembled as code (`nop` at both heap words).

Original word accesses of `0x8009ECA0` / `0x8009ECA8` /
sibling `0x8009ECA4`:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| game malloc | `0x800557A0`/`0x800557A4` | `jal setupAssetDma`; delay `sw $v0, -0x1360($s0)` | `0x8009ECA0` | only heap-pointer writer; `$v0` is `rs_malloc($s1, 0)` from `0x80055770` |
| game decode | `0x800557BC` | `lw $v1, -0x1360($s0)` then XOR-walk bytes | `0x8009ECA0` | consumer; does not store the advanced cursor back |
| voice handle | `0x800557FC` | `sw $s3, -0x135C($v0)` | `0x8009ECA4` | `findAssetAcrossSegments` return; not a heap pointer |
| voice malloc | `0x80055834`/`0x80055838` | `jal setupAssetDma`; delay `sw $v0, -0x1358($v1)` | `0x8009ECA8` | only heap-pointer writer; `$v0` is `rs_malloc($s1, 0)` from `0x80055804` |
| game getter | `0x800558B4` | `lw $v1, -0x1360($v0)`; return `$v1 + lhu` | `0x8009ECA0` | consumer; interior string pointer |
| destructor | `0x800558E0`/`0x800558F8` | `lw $a0, -0x1360`; `beq` zero; `jal rs_free` | `0x8009ECA0` | destructor; NULL skip |
| destructor | `0x80055904`/`0x80055910` | `lw $a0, -0x1358`; `beq` zero; `jal rs_free` | `0x8009ECA8` | destructor; NULL skip |
| sibling DMA | `0x80055918`/`0x8005592C` | `lw $a1, -0x135C`; skip if `-1`; `teardownAssetDma` | `0x8009ECA4` | not `rs_free` |
| sibling reset | `0x80055934` | `sw $s0, -0x135C` (`$s0 = -1`) | `0x8009ECA4` | post-teardown sentinel |
| post-free NULL | `0x8005593C` | `sw $zero, -0x1360($s3)` | `0x8009ECA0` | after both frees |
| post-free NULL | `0x80055944` | `sw $zero, -0x1358($s2)` | `0x8009ECA8` | after both frees |
| voice getter | `0x80055994` | `lw $v0, -0x1358`; `lhu 0x0/0x2($a0)` | `0x8009ECA8` | consumer; table base |
| voice getter | `0x80055998` | `lw $a2, -0x135C` into `setupAssetDma` | `0x8009ECA4` | consumer; asset handle |

`freeTxtFile` is `0x800558D4`..`0x80055958`. Four generated
callers. Single `jr $ra` at `0x80055954`, after both NULLs.

## Object identity

`loadTxtFile` (`0x800556A0`..`0x8005587C`) is the only
original writer of both heap words. `$s1` is the incoming
`$a1` mode byte.

`andi $s1, 0xFF` at `0x80055740` splits the function:

- `$a1 == 0` (`loadGameOrFrontTxtFile`): `rs_malloc` of
  `(header[(idx+1)] - header[idx])` at `0x80055770`, store
  to `0x8009ECA0` in the `setupAssetDma` delay slot, DMA
  fill, `teardownAssetDma` of the *local* find-result `$s3`,
  XOR-decode, return. Does not write `0x8009ECA8` or
  `0x8009ECA4`.
- `$a1 != 0` (`loadVoiceTxtFile` passes `1`): skip the
  `0x8009ECA0` malloc, store `$s3` to `0x8009ECA4`,
  `rs_malloc(lhu(header+2) << 1)` at `0x80055804`, store
  to `0x8009ECA8` in the `setupAssetDma` delay slot, keep
  the DMA live, return. Does not write `0x8009ECA0`.

`$s0`/`$v0`/`$v1` immediately before each store are
`lui 0x800A`. Saved-register restores between each
`rs_malloc` and its delay-slot `sw` do not clobber `$v0`.

`0x8009ECA4` is the `findAssetAcrossSegments` return kept
in `$s3` from `0x800556F0`. It is the same asset handle
passed as `$a2` to `setupAssetDma`, not a malloc. The
voice getter reuses it as the DMA source id. `freeTxtFile`
only `teardownAssetDma`s it.

ROM data at `0x8009ECA0`/`0x8009ECA8` is `nop` (zero).
`rs_free` itself `beq $s0, $zero` and returns, so a NULL
malloc store is a skip, not a Gap.

## Consumers (not the heap pointer)

`getGameOrFrontText` (`0x8005589C`) loads `0x8009ECA0` as
a halfword-offset table and returns `base + lhu(base +
index*2)`, or 0 on a negative / out-of-range index. 161
generated callers. None `jal rs_free` in the post-return
window. Callers that copy `$v0` into `$a0` pass the interior
string to print/format helpers, not `rs_free`.

`getVoiceText` (`0x80055978`) loads `0x8009ECA8` as a
two-halfword range table and `0x8009ECA4` as the DMA
source. Dest is `0x80138E90` (`0x8014 + -0x7170`). Two
generated callers (`tickVoiceSubtitleDisplay` `0x80055D2C`,
`setActiveVoiceLine` `0x80056300`). Neither `jal rs_free`.

`getVoiceTxtStringPtr` returns that dest address and does
not load either heap word.

`setupAssetDma` (`0x80004E70`) stores dest in a command
slot at `+0x24`. `teardownAssetDma` (`0x80004C70`) posts
cmd `0x8001` and waits; it has no `jal rs_free`. That dest
word is the same transient fill target `load_asset` uses.

No other generated `jal 0x80001C98` loads either global
into `$a0`.

## Pairing

`loadTxtFile` has two generated wrappers and no other
callers:

| Wrapper | `$a1` | Writes | Generated callers |
|---|---|---|---|
| `loadGameOrFrontTxtFile` `0x80055880` | 0 | `0x8009ECA0` | `initSceneForMission` `0x800A9CB8` (`$a0=0x800A5410`), `initMission` `0x800FA324` (`$a0=0x800A8F70`), `menuOverlayInit` `0x800C5A44` (`$a0=0x800A7568`), `menuControllerInput` `0x800B5830` (`$a0=0x800A6664`) |
| `loadVoiceTxtFile` `0x8005595C` | 1 | `0x8009ECA8` + `0x8009ECA4` | only `initVoiceSubtitleSystem` `0x80055A58` |

`initVoiceSubtitleSystem` has two generated callers:
`initSceneForMission` `0x800A9CC0` and `initMission`
`0x800FA32C`. Both inits load game text then voice text
without an intervening `freeTxtFile`. That leaves both
heap words live; `freeTxtFile` is the destructor of both.

`freeTxtFile` has four generated callers:

| Caller | PC | Pairing |
|---|---|---|
| `freeCutsceneResources` | `0x800AEB40` | from `cinematicLoopBody` `0x800A64F4`; tears down `initSceneForMission` |
| `menuControllerInput` | `0x800B5808` | free then `loadGameOrFrontTxtFile` at `0x800B5830` (reload) |
| `menuOverlayInit` | `0x800C5CFC` | load at `0x800C5A44`; free on the post-`waitForAnyAudioSlot` arm; `beq` to `L_800C5928` re-enters the load after the free |
| `endMissionCleanup` | `0x800FBA6C` | tears down `initMission`; two `mainGameLoop` arms as in s3624 |

`loadTxtFile` overwrites the live global with a fresh
`rs_malloc` and does not free the previous value. A second
load of the same mode without `freeTxtFile` is a leak of
the first allocator return, not a second pointer source
and not a free of a non-allocator value.

Sequential double-free of either word is blocked by the
post-free NULLs at `0x8005593C`/`0x80055944`, which run
even when the corresponding `beq`-zero skip was taken.
`menuControllerInput` and the `menuOverlayInit` loop
reload only after that NULL.

The two heap words cannot alias inside one `loadTxtFile`
call: the mode split writes exactly one of them. Across
calls they are two live mallocs (game then voice) or a
leak-and-replace of one mode.

## Classification

The only `jal rs_free` sites that can receive these
pointers are `0x800558F8` and `0x80055910`. Each `$a0` is
the matching `loadTxtFile` `rs_malloc` store. Consumers
load the words as table bases or DMA handles and do not
free them. No original non-allocator writer exists. The
sibling `0x8009ECA4` teardown is an asset-handle lifetime
edge, not a third heap free. This selects
`H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected:
one original heap-pointer writer per word.

No guard was added. Runtime allocator state, DMA fill,
filename/mode pairing across scene transitions, and the
BSS-vs-`-1` first teardown of `0x8009ECA4` remain
unproven.

## Next remaining `jal rs_free`

`freeSubtitleOverlay` `0x800562CC` in `funcs_12.c`.
`$a0` is `*0x80139010` (`lui 0x8014` + `-0x6FF0`).
`initVoiceSubtitleSystem` stores `rs_malloc(0x20, 0)`
there at `0x80055A78`. No NULL skip and no post-free
NULL. One generated caller (`endMissionCleanup`
`0x800FBA54`).
