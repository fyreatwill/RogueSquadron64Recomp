# M3 s3620 — remaining NPC allocateAndInitCraftNpcContext destructor rs_free

## Work unit

Static census of every generated original `jal rs_free` in
remaining `allocateAndInitCraftNpcContext` callers outside the
closed AT-AT/AT-ST `+0x4C` and player-craft table `+0xBC`
paths: `splineWalkerCraftNpcHandler` `0x8006C4A8`,
`stubNpcHandler` `0x8006C650`, `npcProbeDriod` `0x800CAF3C`,
`npcWingmanUpdate` `0x800D9854`, `npcTieVariantUpdate`
`0x800DB760`, `npcGroundTransportUpdate` `0x800DEE4C`,
`npcTrainCarUpdate` `0x800E2E3C`, `npcWaterCraftUpdate`
`0x800E678C`, `npcGroundTroopUpdate` `0x800E7FF8`,
`tickCraftWithPhasedDestruction` `0x800E9400`, and
`npcAtPtUpdate` `0x800EAAE4`. Classified each pointer's writer
and whether a free can run on a non-allocator or already-freed
value. No build or runtime run was performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original store of the
`allocateAndInitCraftNpcContext` return in those eleven
functions:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: player-craft table `+0xBC`,
playerAtStUpdate 0xA4/0xBC, actor +0x4C, tickMultiPartVoiceLine,
freeModelViewerMeshChain, shutdownModelViewer header-word,
lookup-table, loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`, speech/cache
`rs_free`, destructor skipped-NULL, destructor unchecked-free,
`-0x6904` alias, remaining-indexer, `-0x6908` non-a0,
release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x8006BD18` across all `funcs_*.c`: 24 sites.
Thirteen are the closed player-craft / AT-AT / AT-ST /
`playerAtStUpdate` stores. Eleven are this class. The leftover
`spawnCutsceneObjectsFromList` `0x800A8254` stores `$v0` at
`0x6C($v1)` and does not `jal rs_free` in that function; it is
not this destructor class.

Original `jal 0x80001C98` in the eleven functions: eleven
sites, one per function, all this class. Matching original
stores of the malloc return: eleven sites, one per function.

| Function | Free PC | Store PC | Actor | Field | Matching malloc |
|---|---|---|---|---|---|
| `splineWalkerCraftNpcHandler` | `0x8006C4A8` | `0x8006C41C` `sw $s0, 0xC($s1)` | `$s1=0x4($s3=$a0)` | `+0xC` | `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` `0x8006BD44`; `$a2=lhu 0xC(params)` |
| `stubNpcHandler` | `0x8006C650` | `0x8006C590` `sw $s0, 0xC($s1)` | `$s1=0x4($s3=$a0)` | `+0xC` | same; `$a2=lhu 0x10(params)` |
| `npcProbeDriod` | `0x800CAF3C` | `0x800CAEB8` `sw $v0, 0x3C($s1)` | `$s1=0x4($s5=$a0)` | `+0x3C` | same; `$a2=0xA` |
| `npcWingmanUpdate` | `0x800D9854` | `0x800D9804` `sw $v0, 0x3C($s0)` | `$s0=0x4($s3=$a0)` | `+0x3C` | same; `$a2=4` or `6` |
| `npcTieVariantUpdate` | `0x800DB760` | `0x800DB6C4` `sw $v0, 0x3C($s1)` | `$s1=0x4($s6=$a0)` | `+0x3C` | same; `$a2=9` |
| `npcGroundTransportUpdate` | `0x800DEE4C` | `0x800DED60` `sw $v0, 0x7C($s1)` | `$s1=0x4($fp=$a0)` | `+0x7C` | same; `$a2=lhu 0x1A(table)` |
| `npcTrainCarUpdate` | `0x800E2E3C` | `0x800E2D64` `sw $v0, 0xA4($s2)` | `$s2=0x4($a0)` | `+0xA4` | same; `$a2=lhu 0x1A(table)` |
| `npcWaterCraftUpdate` | `0x800E678C` | `0x800E66CC` `sw $v0, 0x8C($s3)` | `$s3=0x4($a0)` | `+0x8C` | same; `$a2=lhu 0x1A(table)` |
| `npcGroundTroopUpdate` | `0x800E7FF8` | `0x800E7FC8` `sw $v0, 0x3C($s1)` | `$s1=0x4($s4=$a0)` | `+0x3C` | same; `$a2=0xA` |
| `tickCraftWithPhasedDestruction` | `0x800E9400` | `0x800E9350` `sw $v0, 0x54($s1)` | `$s1=0x4($s4=$a0)` | `+0x54` | same; `$a2=lhu 0x1A(table)` |
| `npcAtPtUpdate` | `0x800EAAE4` | `0x800EA900` `sw $v0, 0x4C($s1)` | `$s1=0x4($s4=$a0)` | `+0x4C` | same; `$a2=0xA` |

Those eleven stores are the only original stores of that malloc
return as a heap pointer on these actor words. Other original
`sw` of the same numeric offsets are different objects (stack
spills, packet bitfields, `sw $zero` of the same word on a
skip-allocate path). `rs_free` itself `beq $s0, $zero` at
`0x80001CA4` and returns, so a NULL `$a0` is a skip, not a Gap.
No opcode-2 destructor NULLs the word after the free.

Tick `lw $a3` of the same field in several updates is a
consumer of `advanceNpcOnCurvedPath`, matching s3617–s3619.

## Remaining functions

`splineWalkerCraftNpcHandler` (`0x8006C3A0`) and
`stubNpcHandler` (`0x8006C4FC`) dispatch on `$a1` directly.
Opcode 1 allocates and `addu $s0, $v0` then delay-slot
`sw $s0, 0xC($s1)` even on malloc-NULL (the `bne $s0, $zero`
skip still stores). Opcode 2 `lw $a0, 0xC($s1)` and
`jal rs_free` with no call-site NULL skip and no post-free
NULL. Opcode 4 ticks consume `0xC($s1)` and do not free.

The other nine are table-dispatched on `(a1-1)`. Case 0 is
setup (opcode 1), case 1 is teardown (opcode 2). Opcode 1
stores the `allocateAndInitCraftNpcContext` return. Opcode 2
loads that word and frees it. Probe, wingman, tie, transport,
train, water, troop, and phased skip the free when the word
is NULL. AT-PT does not skip; `rs_free` still skips NULL.

Wingman `0x800D97E4` / tie `0x800DB6A4` jump past the allocate
with delay-slot `sw $zero` of `+0x3C`. Water `0x800E66A0` and
phased `0x800E9324` `bc1tl` skip the allocate with delay-slot
`sw $zero` of `+0x8C` / `+0x54`. Those are legitimate NULL
writers of the same word, not a second heap-pointer source.

## Sibling frees of `+0x3C`

`updateProbeDroidHopState` (`0x800CABB0`) `lw $a0, 0x3C($s1)`
then `jal rs_free` and `sw $zero, 0x3C($s1)`. Its only
generated callers are three `npcProbeDriod` tick sites that
pass `$a0=$s1` (the same actor). `npcWingmanSteerToward`
(`0x800D8F24`) does the same of `0x3C($s2)` with a post-free
NULL; its only generated caller is `npcWingmanUpdate` tick
passing `$a0=$s0`. Both helpers are different switch cases
from opcode 2, so they cannot run in the same invocation.
After a helper NULLs the word, opcode 2's NULL skip does not
free again. Opcode 2 first detaches the wrapper via
`destroyNpcSlotByIndex`, so the tick helper is not then
called. That matches the closed AT-ST opcode-5 NULL then
opcode-2 skip.

`npcAtPtUpdate` `0x4C($s0)` loads are bitfield tests of
`0x48($s1)` (`andi` 1/2/4/9), not this heap pointer. AT-PT
`+0x4C` is the same actor offset as closed AT-AT/AT-ST but a
different spawn type, not a shared word.

## Pairing / double-free

`destroyNpcSlotByIndex` `jalr`s wrapper `+0x0` with `$a1=2`
once, then `reinsertNpcIntoSortedFreeList`, which
`sw $zero, 0x4($a0)` of the wrapper. Sequential opcode-2 is
one send per destroy.

Opcode 1 overwriting a live context word without a prior free
would leak the 0x1E4 object, matching the unproven re-init /
allocator edges s3604–s3619 left open. A dangling word after
opcode 2 is on an actor the wrapper then detaches; it is not
a second pointer source.

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: every remaining free is the matching
`rs_malloc(0x1E4)` or NULL, and the two sibling `+0x3C` frees
NULL after release. `H-NextClassUnevaluable` is not selected:
each actor register is `0x4(wrapper)` and each field has a
single original heap-pointer writer. Runtime
allocator/lifetime legitimacy remains unproven. No guard or
runtime change followed.

Leftover `jal rs_free` in the searched files after this class
are `loadCraftShadowTextures`, `load_naboo_starfighter`,
`buildModelViewerTextPage` (closed model-viewer), plus the
two sibling helpers above. The remaining
`allocateAndInitCraftNpcContext` caller that does not
`jal rs_free` in the same function is
`spawnCutsceneObjectsFromList` `sw $v0, 0x6C($v1)`
`0x800A826C`.
