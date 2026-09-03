# M3 s3624 — freeEffectAssetBuffers globals rs_free

## Work unit

Static census of `freeEffectAssetBuffers` `jal rs_free` at
`0x8005EBB4` (`$a0 = 0x8013961C` / `-0x69E4($v0)` with
`$v0=0x80140000`) and `0x8005EBC4` (`$a0 = 0x80139740` /
`-0x68C0($v0)`). Enumerated every original load/store of
those two globals and every `jal rs_free` that can receive
them. Classified each pointer's writer and whether a free
can run on a non-allocator or already-freed value. No build
or runtime run was performed.

The discriminator was the single complete original census of
those two `jal rs_free` sites plus every original `lw`/`sw`
of `0x8013961C` and `0x80139740` (including `-0x69E4`/
`-0x68C0` from `0x80140000`) and every `jal rs_free` that
can receive them:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: loadSkyHorizonHob stack
scratch, cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
spawnCutsceneObjectsFromList 0x6C, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor `+0x4C`, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table, loadCharTextureSet
DMA-array, load_asset-then-free, texture-scratch `rs_free`,
text-texture `rs_free`, format-message `rs_free`, speech-file
`rs_free`, speech/cache `rs_free`, destructor skipped-NULL,
destructor unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_13.c`: 7 sites. Two are
this class (`0x8005EBB4`, `0x8005EBC4`). The other five are
`loadSkyHorizonHob` `0x8005B350`/`0x8005B364` (closed s3623),
`cinematicSplineWalkerNpcHandler` `0x8005C35C`/`0x8005C368`
(closed s3622), and `loadExplosionTextures` `0x80061254`.
None of those five loads `0x8013961C` or `0x80139740`.

No absolute `0x8013961C`/`0x80139740` encodings exist in the
generated tree. Every `-0x69E4`/`-0x68C0` site uses
`lui 0x8014` as the base, so all hits are these two words.

Original word accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc | `0x8005E898`/`0x8005E8C4` | `jal rs_malloc(0x400, 0)`; `sw $v0, -0x68C0($s1)` | `0x80139740` | only heap-pointer writer |
| DMA dest | `0x8005E8E8` | `lw $v1, -0x68C0($s1)` into `setupAssetDma` `0x14($sp)` | `0x80139740` | consumer; fills the buffer |
| load_asset | `0x8005E938`/`0x8005E960` | `jal load_asset`; `sw $v0, -0x69E4($v1)` | `0x8013961C` | only heap-pointer writer (`load_asset` returns its `rs_malloc`) |
| cue table | `0x8005E474`..`0x8005E628` | eight `lw $v1, -0x69E4` then `lhu` at `+0x0/+0x8/+0x10/+0x18/+0x20/+0x28/+0x38` | `0x8013961C` | consumer; index is `0x80137CE4<<1` |
| destructor | `0x8005EBA8`/`0x8005EBB4` | `lw $a0, -0x69E4`; `jal rs_free` | `0x8013961C` | destructor; no NULL skip; no post-free NULL |
| destructor | `0x8005EBC0`/`0x8005EBC4` | `lw $a0, -0x68C0`; `jal rs_free` | `0x80139740` | destructor; no NULL skip; no post-free NULL |
| spawn default | `0x8005EC00` | `lw` into `0x24($sp)` of `spawnNpcOfType` | `0x80139740` | consumer |
| spawn param | `0x8005EC84` | `lw` into `0x24($sp)` of `spawnNpcOfType` | `0x80139740` | consumer |
| guided effect | `0x8005FC00` | `lw` into `0x3C($sp)` of `spawnNpcOfType` | `0x80139740` | consumer |
| audio cue | `0x8005CC34` | `lw` into `0x3C($sp)` of `spawnNpcOfType` | `0x80139740` | consumer |
| scaled triple | `0x800756B0` | `lw` into `0x3C($sp)` of `spawnNpcOfType` | `0x80139740` | consumer |

`freeEffectAssetBuffers` is `0x8005EBA4`..`0x8005EBD4`. One
generated caller: `endMissionCleanup` `jal 0x8005EBA4` at
`0x800FBA5C`. Single `jr $ra` at `0x8005EBD0`.

## Object identity

`loadWeaponsHobObjects` (`0x8005E7EC`..`0x8005E978`) is the
only original writer of both words.

`$s1 = lui 0x8014` at `0x8005E8C0` immediately before the
`-0x68C0` store; the earlier `$s1 = 0x8009ED00` name-table
walk has ended. `$v1 = lui 0x8014` at `0x8005E95C`
immediately before the `-0x69E4` store.

`0x80139740` is `rs_malloc(0x400, 0)` at `0x8005E898`. The
following `findAssetAcrossSegments` / `setupAssetDma` /
`teardownAssetDma` sequence uses that pointer as the DMA
destination (`lw` at `0x8005E8E8`) and does not store a
second pointer into the global.

`0x8013961C` is the `load_asset` return at `0x8005E938`
(`$a0 = 0x8003B190`). `load_asset` (`0x8006488C`) does
`rs_malloc(get_asset_size_extra(...), 0)`, DMA-fills that
buffer, and returns it in `$v0`. Saved-register restores
between the jal and the `sw` do not clobber `$v0`.

`dispatchCueByCategory` loads `0x8013961C` as a halfword
table base. The eight sites are category arms of one
function; each does `index = *(0x80137CE4) << 1` then
`lhu` at a fixed row offset. None `jal rs_free`.

The five `0x80139740` spawn consumers copy the pointer into
a `spawnNpcOfType` extra-arg slot. None `jal rs_free`.

No other generated `jal 0x80001C98` loads either global
into `$a0`.

## Pairing

`loadWeaponsHobObjects` has two generated callers:
`initMission` (`0x800FA55C`) and `setupCutsceneLevel`
(`0x800A6F78`). It always overwrites both globals with
fresh allocator returns and does not free the previous
values.

`endMissionCleanup` has two generated callers, both in
`mainGameLoop`: `0x8003E2C4` (arm `L_8003E250`, taken when
`0x18($s3) & 0x02000000`) and `0x8003E388` (arm
`L_8003E2E8`). The first arm `j L_8003E114` after the
teardown, so the two sites do not fall through in one
iteration. `freeEffectAssetBuffers` does not NULL either
word after the free.

A second `endMissionCleanup` without a matching
`loadWeaponsHobObjects` would pass an already-freed
pointer; a BSS-zero first call would pass NULL. Neither
is a second original pointer source. Sequential pairing
and allocator/NULL legitimacy remain unproven at runtime.

## Classification

Every remaining free of these two words is a destructor of
the matching `loadWeaponsHobObjects` allocator store. No
original non-allocator writer exists. No other `jal rs_free`
receives either pointer. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: both words have a
single original heap-pointer writer.

No guard was added. Runtime allocator state, DMA fill, cue
index bound versus `0x80137CE4`, and load/free pairing
remain unproven.

## Next remaining `funcs_13.c` `jal rs_free`

`loadExplosionTextures` `0x80061254`. `$a0` is the
`load_asset` return at `0x8006119C`, kept as the source
base of the 16-iter copy into `0x801398C0`/`0x80139920`.
