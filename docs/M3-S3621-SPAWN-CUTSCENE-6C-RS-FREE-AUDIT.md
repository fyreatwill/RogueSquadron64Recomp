# M3 s3621 — leftover spawnCutsceneObjectsFromList 0x6C store

## Work unit

Static census of the leftover `allocateAndInitCraftNpcContext`
store that has no same-function `jal rs_free`:
`spawnCutsceneObjectsFromList` `sw $v0, 0x6C($v1)` at
`0x800A826C`. Enumerated every original load/store of that
cutscene-object `+0x6C` word and every `jal rs_free` that can
receive it, including `cutsceneActorNpcHandler` `0x800447C4` /
`0x80044B08`. Classified the pointer's writer and whether a
free can run on a non-allocator or already-freed value. No
build or runtime run was performed.

The discriminator was the single complete original census of
that `0x6C($v1)` store plus every original `lw`/`sw` of the
same cutscene-object `+0x6C` word and every `jal rs_free` that
can receive it:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor `+0x4C`, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`, speech/cache
`rs_free`, destructor skipped-NULL, destructor unchecked-free,
`-0x6904` alias, remaining-indexer, `-0x6908` non-a0,
release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x8006BD18` (`allocateAndInitCraftNpcContext`)
across all `funcs_*.c`: 24 sites. Twenty-three are the closed
player-craft / AT-AT / AT-ST / `playerAtStUpdate` / NPC
destructor stores. One is this leftover:
`spawnCutsceneObjectsFromList` `0x800A8254`.

Original non-stack word `lw`/`sw` of `0x6C($reg)`: 101 sites.
Two functions both load `gCutsceneEntries` at `0x800B1900` and
touch a non-stack `+0x6C` word: `spawnCutsceneObjectsFromList`
and `cutsceneDispatchSlotsByFlag`. No function both loads
`0x800B1900` and `jal rs_free`. No `jal rs_free` has a nearby
original `lw` of a non-stack `0x6C` word.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| `spawnCutsceneObjectsFromList` | `0x800A826C` | `sw $v0, 0x6C($v1)` | `*0x800B1900 + index*0x13C` | `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` `0x8006BD44` |
| `spawnCutsceneObjectsFromList` | `0x800A8274` | `lw $v0, 0x6C($v1)` | same entry | reload to write context `+0x10` |
| `cutsceneDispatchSlotsByFlag` | `0x800A86A4` | `lw $a3, 0x6C($a2)` | `$a2=*0x800B1900+$s0`, `$s0` is the same `0x13C` stride | `$a3` of `advanceNpcOnCurvedPath` |

`load_cutscene` `0x800A6728` `rs_malloc(count*0x13C)` stores the
table at `0x800B1900` and `rs_memset`s it, so `+0x6C` is zero
until the spawn store. That memset is the only other original
writer of the word. `freeCutsceneResources` does not load
`0x800B1900` and does not `jal rs_free`.

## Object identity

`$fp = 0x800B0000`. `$s1` at the store is
`index*0x13C` (`0x800A81A4..0x800A81BC`). `$v1 = MEM_W(0x800B1900) + $s1`.
The architecture label `gCutsceneEntries` is a pointer to that
allocated table, not the table itself.

The allocate is gated on entry byte `+0x3` bit `0x4`
(`0x800A821C..0x800A822C`), the same word-0 bit `0x4` that
dispatch requires (`0x800A861C..0x800A8634`, mask
`0xFF000004 == 0x4`) before loading `+0x6C`. Dispatch also
requires source flag `0x80` at `+0x13F7`, matching spawn's
entry walk. `$a2` of `allocateAndInitCraftNpcContext` is
`lhu 0x2` of the `0x14`-stride row at `0x800B04AC + 20*$s0`.

After the store, spawn writes floats into the returned context
at `+0x14` then `+0x10`. That `$v0` is not stored on any other
original word.

## cutsceneActorNpcHandler 0x6C is a different object

`cutsceneActorNpcHandler` does not load `0x800B1900`. Opcode 1
`rs_malloc(0x118)` at `0x80044780`, stores it at `0x4($a0)`,
and `sw $zero, 0x6C($s2)` at `0x800447C4` as init of that
0x118-byte actor. Opcode 4 `sw $s3, 0x6C($s2)` at `0x80044B08`
stores `buildVisibleTerrainGridAroundCamera`'s return, or
skips when that return is 0 / when `gCurrentLevel==0xA`.
Opcode 2 is epilogue only (`L_80044BC4`). Actor size `0x118`
is not the cutscene-entry stride `0x13C`. This word is a
terrain-grid field on the cinematic actor, not the
`allocateAndInitCraftNpcContext` pointer.

Opcode 1 `spawnNpcOfType` `$a0=0x8005BCC4` is
`cinematicSplineWalkerNpcHandler`; that handler's `rs_free`
sites are not this class.

## Frees that can receive the pointer

None. `advanceNpcOnCurvedPath` takes the dispatch `$a3` as
`$s1` and does not `jal rs_free`. NPC opcode-2 destructors
free a separate opcode-1 malloc on `0x4(wrapper)+field`, not
this entry word. `rs_free` itself `beq $s0, $zero` at
`0x80001CA4`, so a memset-NULL `+0x6C` is a skip, not a Gap.

A second `load_cutscene` would replace `0x800B1900` without
freeing the old table or its `+0x6C` mallocs. That is a leak
of a detached table, not a second pointer source and not a
free of a non-allocator value.

## Classification

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: there is no `jal rs_free` of this
word, and the only heap-pointer writer is the matching
`rs_malloc(0x1E4)`. `H-NextClassUnevaluable` is not selected:
the entry register is `*0x800B1900 + index*0x13C`, the
handler `+0x6C` is a different object, and the word has a
single original heap-pointer writer. Runtime
allocator/lifetime legitimacy remains unproven. No guard or
runtime change followed.

Leftover `jal rs_free` after this class include
`cinematicSplineWalkerNpcHandler` `0x8005C35C` /
`0x8005C368` (`0x2B44(0xF00($s2))` then `0xF00($s2)`), plus
`loadCraftShadowTextures` and `load_naboo_starfighter`.
All 24 `allocateAndInitCraftNpcContext` callers are now
classified.
