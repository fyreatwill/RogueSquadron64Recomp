# M3 s3618 — remaining playerAtStUpdate 0xA4 / 0xBC rs_free

## Work unit

Static census of every generated original `jal rs_free` in
`playerAtStUpdate`. Remaining funcs_37 frees after the closed
actor +0x4C class: `0x800D25A0` of `0xA4($s2)` and `0x800D25D4`
of `0xBC($s4)`. Classified each pointer's writer and whether a
free can run on a non-allocator or already-freed value. No build
or runtime run was performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original `sw` of
`0xA4($s2)` and `0xBC($s4)`:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: actor +0x4C,
tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`, speech/cache
`rs_free`, destructor skipped-NULL, destructor unchecked-free,
`-0x6904` alias, remaining-indexer, `-0x6908` non-a0,
release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT
publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `playerAtStUpdate`: two sites, both
this class. `funcs_37.c` has no later `rs_free`.

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| Player AT-ST 0x168 template backup | `0xA4($s2)`, `$s2=0x4($a0)` | opcode-1 delay-slot `sw $a0, 0xA4($s2)` `0x800D22B8` | `rs_malloc(0x168)` `0x800D2298` (`$a1` flags 0), `$a0=$v0` | teardown `0x800D25A0` of `$a0`; no skip, no post-free NULL |
| Player-craft table slot 0 context | `0xBC($s4)`, `$s4=0x80137DBC` | opcode-1 `sw $v0, 0xBC($s4)` `0x800D23F4` | `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` `0x8006BD44`, returned `$v0=$s1` | teardown `0x800D25D4` of `$a0`; no skip, no post-free NULL |

Those two stores are the only original stores of those malloc
returns as heap pointers on these words. `rs_free` itself
`beq $s0, $zero` at `0x80001CA4` and returns, so a NULL `$a0`
is a skip, not a Gap.

Other original `0xA4($s2)` / `0xBC($s4)` accesses are not a
second pointer source. `npcAtStUpdate` `sw $v0, 0xA4($s2)`
`0x800D0F14` copies `0x4($s0)` onto the NPC AT-ST actor with
adjacent `+0xA0/+0xA8..+0xAB` packed fields, not a heap
pointer. `0xBC($sp)` is the `$s5` spill. Teardown
`lw $a1, 0xA4($s2)` then `zmemcpy` of 0x168 restores the
template at `0x8009E5F8` from the backup before the free.
Tick `lw $a3, 0xBC($s4)` `0x800D2B0C` is a consumer of
`advanceNpcOnCurvedPath`.

## Remaining function

`playerAtStUpdate` (`0x800D2208`) is table-dispatched on
`(a1-1)<0xF`. `$s3=$a0` is the wrapper; `$s2=0x4($s3)` is the
actor. `$s4` is loaded once at `L_800D2260` as `0x80137DBC`
(player-craft table base, slot 0) and opcode 1 reloads the
same address. Case 0 is setup (opcode 1), case 1 is teardown
(opcode 2). No generated `jal 0x800D2208`. The only generated
address materialization is `choosePlayerCraftAssets`
`0x800FB77C`, which `spawnNpcOfType`s this update.

### Opcode 1 (`L_800D2294`) — matching stores

`rs_malloc(0x168)` at `0x800D2298`. `$a0=$v0`, then
`zmemcpy` from `0x8009E5F8` of size 0x168, delay-slot
`sw $a0, 0xA4($s2)` at `0x800D22B8`. A second `zmemcpy`
copies `0x8010A6DC` over that same template. Later
`jal allocateAndInitCraftNpcContext` at `0x800D23C4` with
`$a2=0xA` and `sw $v0, 0xBC($s4)` at `0x800D23F4`. The
function does not `sw` wrapper `+0x4`; the actor is
`0x4(wrapper)` from the spawn contract, matching s3617.

### Opcode 2 (`L_800D2588`) — both frees

`zmemcpy` dest `0x8009E5F8` src `0xA4($s2)` size 0x168, then
`lw $a0, 0xA4($s2)` and `jal rs_free` at `0x800D25A0` with no
NULL skip and no post-free NULL. It then copies `+0xA8` and
optionally ORs flag `0x80` into `0x80130B4C`. `lw $a0,
0xBC($s4)` and `jal rs_free` at `0x800D25D4` with no NULL
skip and no post-free NULL. It then `releaseMeshAsset` of
`0x0($s4)`, `teardownHudInstancesAndUnbindNpcs`, and returns
1. The two frees are one switch case of one invocation.

Opcode 12 (`L_800D2560`) re-inits movement and does not
`jal rs_free`.

## Pairing / double-free

`spawnNpcOfType` (`0x8003FFEC`) may `destroyNpcSlotByIndex`
existing live slots, then zeros wrapper `+0x4/+0x8/+0xC/+0x10`,
stores this update at wrapper `+0x0`, and
`slotDispatcherIter`s opcode 1. `destroyNpcSlotByIndex`
(`0x8003ED74`) is the generated teardown dispatcher. If
wrapper `+0x1A != 0` it ORs flag `0x8` onto `+0x14` and
returns without `jalr`. Otherwise it `jalr` wrapper `+0x0`
with `$a1=2`, then `reinsertNpcIntoSortedFreeList`, which
`sw $zero, 0x4($a0)` of the wrapper. Sequential opcode-2 is
one send per destroy, then the wrapper leaves the live list.

Neither free NULLs its word. That leaves a dangling 0xA4 on
an actor the wrapper then detaches, and a dangling 0xBC on
table slot 0; those are not a second pointer source. Opcode 1
overwriting a live 0xA4 or 0xBC without a prior free would
leak, matching the unproven re-init / allocator edges
s3604–s3617 left open.

Sibling player-craft updates
(`playerSnowSpeederUpdate`, `playerXwingUpdate`,
`playerAwingUpdate`, `playerYwingUpdate`,
`playerVwingUpdate`, `playerFalconUpdate`,
`playerTieInterceptorUpdate`, `playerT16Update`,
`playerNabooStarfighterUpdate`) store and free
`0xBC($s1)` of `0x80137DBC + 0x2A0*index`. Those are
`0xBC($s1)`, not `0xBC($s4)`, and are a remaining class.
Their writers are the same `allocateAndInitCraftNpcContext`
return, not a non-allocator store of this function's word.

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: every remaining free is the matching
`rs_malloc(0x168)` or `rs_malloc(0x1E4)`, or NULL.
`H-NextClassUnevaluable` is not selected: `$s2` is
`0x4(wrapper)` and `$s4` is table slot 0. Runtime
allocator/lifetime legitimacy remains unproven. No guard or
runtime change followed.

`funcs_37.c` has no later `rs_free`. The next class is the
remaining player-craft table `+0xBC` family.
