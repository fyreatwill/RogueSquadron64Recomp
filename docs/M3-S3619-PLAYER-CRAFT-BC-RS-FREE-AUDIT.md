# M3 s3619 — remaining player-craft table +0xBC rs_free

## Work unit

Static census of every generated original `jal rs_free` of
player-craft table field `+0xBC` outside the closed
`playerAtStUpdate` slot-0 path. Remaining sibling teardown
frees: `playerSnowSpeederUpdate` `0x800AD168`,
`playerXwingUpdate` `0x800B56EC`, `playerAwingUpdate`
`0x800B7410`, `playerYwingUpdate` `0x800B8748`,
`playerVwingUpdate` `0x800BA228`, `playerFalconUpdate`
`0x800BBAD8`, `playerTieInterceptorUpdate` `0x800BCAB8`,
`playerT16Update` `0x800BD7D8`, and
`playerNabooStarfighterUpdate` `0x800BEA8C`, each of
`0xBC($s1)` where `$s1 = 0x80137DBC + 0x2A0*index`.
Classified each pointer's writer and whether a free can run
on a non-allocator or already-freed value, including whether
index 0 aliases the closed AT-ST slot-0 word. No build or
runtime run was performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original `sw` of
`0xBC($s1)` in those nine updates:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: playerAtStUpdate 0xA4/0xBC,
actor +0x4C, tickMultiPartVoiceLine, freeModelViewerMeshChain,
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

Original `lw $a0, 0xBC($s1)` plus `jal 0x80001C98` in the nine
updates: nine sites, one per function, all this class. Each
function has exactly one `jal rs_free`. Matching original
`sw $v0, 0xBC($s1)`: nine sites, one per function.

| Function | Free PC | Store PC | `$s1` | Matching malloc |
|---|---|---|---|---|
| `playerSnowSpeederUpdate` | `0x800AD168` | `0x800AD07C` | `0x80137DBC+0x2A0*index` | `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` `0x8006BD44`, returned `$v0=$s1`; `$a2=4` |
| `playerXwingUpdate` | `0x800B56EC` | `0x800B55F0` | same | same; `$a2=2` |
| `playerAwingUpdate` | `0x800B7410` | `0x800B7324` | same | same; `$a2=0` |
| `playerYwingUpdate` | `0x800B8748` | `0x800B865C` | same | same; `$a2=3` |
| `playerVwingUpdate` | `0x800BA228` | `0x800BA13C` | same | same; `$a2=1` |
| `playerFalconUpdate` | `0x800BBAD8` | `0x800BB9EC` | same | same; `$a2=5` |
| `playerTieInterceptorUpdate` | `0x800BCAB8` | `0x800BC9CC` | same | same; `$a2=7` |
| `playerT16Update` | `0x800BD7D8` | `0x800BD6EC` | same | same; `$a2=6` |
| `playerNabooStarfighterUpdate` | `0x800BEA8C` | `0x800BE990` | same | same; `$a2=8` |

Those nine stores are the only original stores of that malloc
return as a heap pointer on these words. Other original
`sw …, 0xBC(*)` are different objects (stack spills, effect
records, `initCraftSelectScreen` zero of `0x800CDB20+0xBC`).
`rs_free` itself `beq $s0, $zero` at `0x80001CA4` and returns,
so a NULL `$a0` is a skip, not a Gap. No destructor NULLs
`0xBC` after the free.

Tick `lw $a3, 0xBC($s1)` in each update is a consumer of
`advanceNpcOnCurvedPath`, matching s3618's AT-ST tick load.

## Remaining functions

Each update is table-dispatched on `(a1-1)<0xC`. `$s3=$a0` is
the wrapper; `$s0=0x4($s3)` is the actor. Case 0 is setup
(opcode 1), case 1 is teardown (opcode 2). Snowspeeder also
has a cinematic-flag preamble: when `lbu 0x800AEBBC` is
nonzero, opcode 2 jumps to `L_800ACE18`, which computes `$s1`
the same way and joins the shared free at `L_800AD15C`. That
path is mutually exclusive with jump-table case 1.

### Opcode 1 — matching stores

Opcode 1 `rs_malloc`s a craft-sized actor (`0x120` snowspeeder,
`0x28` X-wing, `0x4C` A-wing, `0x18` Y-wing, `0x30` V-wing,
`0xC4` Falcon, `0x18` TIE, `0x8` T-16, `0x24` Naboo), stores
it at `0x4(wrapper)`, and sets
`$s1 = 0x80137DBC + 0x2A0*trunc(float at 0x0($a2))`.
`player*Init($a0=actor, $a1=that index)` then
`sw $a1, 0x0(actor)` in every listed init. Later
`jal allocateAndInitCraftNpcContext` and
`sw $v0, 0xBC($s1)`. The actor malloc is a different word
and is not this class.

### Opcode 2 — the free

`lw $v0, 0x0($s0)` reloads the init-stored index, recomputes
the same `$s1`, then `lw $a0, 0xBC($s1)` and `jal rs_free`
with no NULL skip and no post-free NULL. It then
`releaseMeshAsset` of `0x0($s1)` and returns 1. Jump-table
cases 2/3/4/11 do not `jal rs_free` (engine/sound, mesh
cleanup, `destroyNpcSlotByIndex` of a message halfword, or
re-init).

## Pairing / double-free / slot-0 alias

`spawnNpcOfType` may `destroyNpcSlotByIndex` existing live
slots, then zeros wrapper `+0x4/+0x8/+0xC/+0x10`, stores this
update at wrapper `+0x0`, and `slotDispatcherIter`s opcode 1.
`destroyNpcSlotByIndex` `jalr`s wrapper `+0x0` with `$a1=2`
once, then `reinsertNpcIntoSortedFreeList`, which
`sw $zero, 0x4($a0)` of the wrapper. Sequential opcode-2 is
one send per destroy.

When `index==0`, `$s1` is `0x80137DBC`, the same word as
closed AT-ST `0xBC($s4)`. That is the per-player table slot 0,
not a second pointer source: AT-ST hardcodes slot 0, and these
updates index the same table from `0x0(actor)`. Sequential
double-free of that shared word is still blocked by
`destroyNpcSlotByIndex`. Opcode 1 overwriting a live `0xBC`
without a prior free would leak, matching the unproven re-init
/ allocator edges s3604–s3618 left open.

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: every remaining free is the matching
`rs_malloc(0x1E4)`, or NULL. `H-NextClassUnevaluable` is not
selected: `$s1` is `0x80137DBC+0x2A0*index` with `index` the
init-stored `0x0(actor)` word. Runtime allocator/lifetime
legitimacy remains unproven. No guard or runtime change
followed.

`funcs_28.c` leftover `jal rs_free` after this class are
`loadBackdropAsset` (closed texture-scratch),
`initCinematicSceneAssets` (closed cinematic scratch), and
`freeEffectModelInstancePool` of `-0x4920`. Remaining
`allocateAndInitCraftNpcContext` callers that still `jal
rs_free` are NPC updates outside the closed AT-AT/AT-ST
`+0x4C` and this player-craft `+0xBC` family.
