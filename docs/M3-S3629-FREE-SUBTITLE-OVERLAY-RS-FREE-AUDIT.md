# M3 s3629 — freeSubtitleOverlay rs_free of *0x80139010

## Work unit

Static census of `freeSubtitleOverlay` `jal rs_free` at
`0x800562CC` (`$a0` = `*0x80139010` / `-0x6FF0` from
`lui 0x8014`). Enumerated every original load/store of that
word (including `initVoiceSubtitleSystem` `rs_malloc(0x20, 0)`
at `0x80055A78` and every overlay consumer) and every
`jal rs_free` that can receive it. The preceding
`resetPlayerSlotChannelTransform` of `lhu *0x80139014`
(`-0x6FEC`) is a sibling lifetime edge, not a second
`rs_free`. No build or runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw` of
`0x80139010` (`-0x6FF0` from `0x80140000`) and every
`jal rs_free` that can receive that word:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeTxtFile globals,
loadSpriteSheetTextureFrames inlined-malloc, loadAndRelocateAsset
load_asset, loadExplosionTextures load_asset,
freeEffectAssetBuffers globals, loadSkyHorizonHob stack scratch,
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

Original `jal 0x80001C98` in `funcs_12.c`: 10 sites. One is
this class (`0x800562CC`). The other nine are
`loadSpriteSheetTextureFrames` `0x80055450` (closed s3627),
`loadAndRelocateAsset` `0x800555C4` (closed s3626),
`freeTxtFile` `0x800558F8`/`0x80055910` (closed s3628),
`load_hmt_and_hob` `0x80056798`/`0x80056D60`/`0x80056D6C`,
`releaseMeshAsset` `0x8005794C`, and
`freeAllHobFiles` `0x80059244`. None of those nine loads
`0x80139010`. Across the generated tree, 205 `jal 0x80001C98`
comments exist; the only one whose nearby original window
mentions `-0x6FF0` is `0x800562CC`.

No absolute `0x80139010` encoding exists as `lw`/`sw` in the
generated tree. Every `-0x6FF0` site in `funcs_12.c` uses
`lui 0x8014` as the last write of its base register, so all
31 unique original hits are this word. The `funcs_49.c`
`lb $t2, -0x6FF0($zero)` at `0x8010B3AC` is mis-disassembled
data with base `$zero` (physical `0xFFFF9010`), not this word.

Original word accesses of `0x80139010`:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc store | `0x80055A78` | `sw $v0, -0x6FF0($v1)` | `0x80139010` | only heap-pointer writer; `$v0` is `rs_malloc(0x20, 0)` from `0x80055A64`; `$v1` is `lui 0x8014` |
| init copy | `0x80055B70` | `lw $v1, -0x6FF0($v1)` then `sb` overlay `+0x5` | overlay | consumer; copies player-slot `+0x7` |
| HUD link | `0x80055BA0`/`0x80055BEC` | `lw $a0`/`$a1` | overlay | consumer; line-id / screen-pos fields; stores the HUD node, not this pointer |
| tick | `0x80055CC0`..`0x80056150` (20 `lw`) | overlay fields `+0x0`..`+0x1C` | overlay | consumer; display/progress state |
| screen pos | `0x80056204`/`0x80056244`/`0x80056270` | `sh` overlay `+0x12`/`+0x14`/`+0x16` | overlay | consumer |
| destructor | `0x800562C8`/`0x800562CC` | `lw $a0`; `jal rs_free` | overlay | destructor; no NULL skip; no post-free NULL |
| set line | `0x800562EC`/`0x80056308`/`0x80056310` | `sh` `+0x0`; `sb` `+0x3`/`+0x2`; `sw` `+0x8` | overlay | consumer; `+0x8` is the incoming voice key |
| clear line | `0x80056334` | `sh 0xFFFF` overlay `+0x0` | overlay | consumer |

`freeSubtitleOverlay` is `0x800562AC`..`0x800562DC`. One
generated caller. Single `jr $ra` at `0x800562D8`, immediately
after the free.

## Object identity

`initVoiceSubtitleSystem` (`0x80055A30`..`0x80055B88`) is the
only original writer of the heap word. Sequence:

1. `loadVoiceTxtFile` (`0x80055A58`).
2. `rs_malloc(0x20, 0)` at `0x80055A64`.
3. `sw $v0, -0x6FF0($v1)` at `0x80055A78` (`$v1` = `lui 0x8014`).
4. Delay-slot `sh 0xFFFF, 0x0($v0)` then
   `setSubtitleOverlayScreenPos`.
5. Boot-config aspect selects sibling halfword `0x80139014`
   (`-0x6FEC`) as `0xA`, `0x4`, or `0xB`.
6. That halfword is `$a0`/`$a1` to `loadCharTextureSet`,
   `setMenuOverlayHeaderState`, `setPlayerSlotEntryRGB`,
   `setPlayerSlotAnimationFlag`, and `getPlayerSlotFieldAt34`.
7. Player-slot `+0x10` byte `+0x7` is copied to overlay `+0x5`.

`$v0` is not clobbered between `rs_malloc` and the store.
The 0x20-byte overlay layout matches the malloc size:

| Off | Width | Role |
|---|---|---|
| `+0x0` | half | active line id; `0xFFFF` = none |
| `+0x2` | byte | display flag |
| `+0x3` | byte | progress/counter |
| `+0x4` | byte | derived line count |
| `+0x5` | byte | slot-copied scale |
| `+0x8` | word | voice-playback key (`-1` or `setActiveVoiceLine` `$a1`) |
| `+0xC`..`+0x16` | halfs | layout / screen pos |
| `+0x18`/`+0x1C` | float | interpolated screen pos |

No consumer stores the overlay pointer itself to another
global. Interior `+0x8` is a voice key passed to
`getVoicePlaybackProgressByKey`, not a heap pointer and not
an `rs_free` argument.

## Sibling `0x80139014` (`-0x6FEC`)

`freeSubtitleOverlay` first `lhu $a0, -0x6FEC` and
`jal resetPlayerSlotChannelTransform` (`0x80063BEC`). That
callee indexes `0x8009FC10 + (slot << 2)`, loads the slot
object, and zeros `+0x20`/`+0x24`/`+0x28`/`+0x30`. It has
no `jal rs_free`. The halfword is a slot index written only
by init (`0xA`/`0x4`/`0xB`), also consumed by overlay
helpers, `tickVoiceSubtitleDisplay`, and nine
`runPauseMenuStateMachine` `lhu $a0, -0x6FEC($t8)` sites
(each `$t8` is `lui 0x8014`). `addiu $fp, $s3, -0x6FEC`
takes the address of that halfword. None of these is a
second free of `0x80139010`.

## Consumers (not the heap pointer)

| Function | Generated callers | Uses overlay as |
|---|---|---|
| `linkHudNodeAndComputeScreenPos` | `slotEffectHandlerDispatch` twice, `runInMissionFrame` | line-id gate and screen-pos base; stores HUD node `+0x8` |
| `tickVoiceSubtitleDisplay` | `cinematicLoopBody`, `runInMissionFrame` | display/progress fields; `getVoiceText` of the line id |
| `setSubtitleOverlayScreenPos` | init, `initSceneForMission`, `initMission`, two transition helpers | writes `+0x12`/`+0x14`/`+0x16` |
| `setActiveVoiceLine` | `tickSpeechSubsystem` | writes `+0x0`/`+0x2`/`+0x3`/`+0x8` |
| `clearActiveVoiceLine` | `tickSpeechSubsystem` | writes `+0x0 = 0xFFFF` |

None `jal rs_free`. No other generated `jal 0x80001C98`
loads this global into `$a0`.

## Pairing

`initVoiceSubtitleSystem` has two generated callers:
`initSceneForMission` `0x800A9CC0` and `initMission`
`0x800FA32C`. `freeSubtitleOverlay` has one generated
caller: `endMissionCleanup` `0x800FBA54`.
`endMissionCleanup` has two `mainGameLoop` arms
(`0x8003E2C4`, `0x8003E388`), each `initMission` then
`endMissionCleanup`, the same mutually exclusive teardown
pair as s3624.

A second init without this destructor overwrites the live
global with a fresh `rs_malloc` and leaks the previous
return. Cinematic `initSceneForMission` has no generated
`freeSubtitleOverlay` (cinematic teardown frees txt files
via `freeCutsceneResources`, not this overlay). That is a
leak of the first allocator return, not a second pointer
source and not a free of a non-allocator value.

No NULL skip and no post-free NULL. Sequential double-free
of the dangling word would require `endMissionCleanup`
twice without an intervening init. The two `mainGameLoop`
arms each pair one init with one destructor. Runtime
pairing across scene transitions remains unproven.

`rs_free` itself `beq $s0, $zero` and returns, so a BSS-zero
first free is a skip, not a Gap. There is no original
non-allocator store that would put a non-NULL non-malloc
value in the word.

## Classification

The only `jal rs_free` site that can receive this pointer is
`0x800562CC`. `$a0` is the matching `initVoiceSubtitleSystem`
`rs_malloc(0x20, 0)` store. Consumers load the word as the
overlay object and do not free it. No original non-allocator
writer exists. The sibling `-0x6FEC` reset is a slot-index
lifetime edge, not a second heap free. This selects
`H-NextClassComplete`. `H-NextClassGap` is refuted at
static scope. `H-NextClassUnevaluable` is not selected:
one original heap-pointer writer.

No guard was added. Runtime allocator state, cinematic-vs-
mission pairing, and sequential double-free without a
post-free NULL remain unproven.

## Next remaining `jal rs_free`

`load_hmt_and_hob` in `funcs_12.c`: `0x80056798`
(`$a0` = `$s3`, the `get_asset_size_extra` `rs_malloc` at
`0x80056580`/`0x80056598`), `0x80056D60`
(`$a0` = `0x6C($sp)`, gated by `0x8F($sp)`), and
`0x80056D6C` (`$a0` = `0x74($sp)`).
