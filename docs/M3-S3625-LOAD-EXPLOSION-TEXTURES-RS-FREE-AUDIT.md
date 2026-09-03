# M3 s3625 — loadExplosionTextures load_asset rs_free

## Work unit

Static census of `loadExplosionTextures` `jal rs_free` at
`0x80061254` (`$a0` = `load_asset` return copied at
`0x8006119C`). Enumerated every original load/store of that
pointer (including the 16-iter copy that uses it as a source
base into `0x801398C0` / `-0x6740` and `0x80139920` /
`-0x66E0`) and every `jal rs_free` that can receive it.
Classified the pointer's writer and whether a free can run
on a non-allocator or already-freed value. No build or
runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of the `load_asset` return kept in `$a0` (and any store of
it to a global or stack word) and every `jal rs_free` that
can receive it:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeEffectAssetBuffers
globals, loadSkyHorizonHob stack scratch,
cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
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

Original `jal 0x80001C98` in `funcs_13.c`: 7 sites. One is
this class (`0x80061254`). The other six are
`loadSkyHorizonHob` `0x8005B350`/`0x8005B364` (closed s3623),
`cinematicSplineWalkerNpcHandler` `0x8005C35C`/`0x8005C368`
(closed s3622), and `freeEffectAssetBuffers` `0x8005EBB4`/
`0x8005EBC4` (closed s3624). None of those six receives the
`loadExplosionTextures` `$a0`.

No absolute `0x801398C0`/`0x80139920` encodings exist in the
generated tree. No original `lw`/`sw` uses `-0x6740` or
`-0x66E0` as a memory operand. Every `lui 0x8014` plus
`addiu -0x6740`/`-0x66E0` forms the color-table *address*,
not a load of a heap pointer stored there.

`loadExplosionTextures` is `0x8006108C`..`0x80061264`. One
generated caller: `loadWeaponsHobObjects` `jal 0x8006108C`
at `0x8005E88C`. Single `jr $ra` at `0x80061260`, after the
free. Both `0x80130B63` arms reach `load_asset` and the free.

Original word/byte accesses of the malloc pointer and the
two dest bases:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| load_asset | `0x80061194`/`0x8006119C` | `jal load_asset("smkexp_PAL")`; `addu $a0, $v0` | `$a0` | only heap-pointer writer |
| copy src | `0x800611C4`/`D8`/`EC`/`0x80061204`/`18`/`30` | `addu $v0, $v0, $a0` then `lbu` at `+0/+1/+2/+0x80/+0x81/+0x82` | `$a0` | consumer; index is `0x80130B70<<2` |
| copy dest B | `0x800611B8` then 16 `sb` at `$v1+0..+3` | `$v1 = 0x80139920` | `0x80139920` | RGB bytes + alpha; not the heap pointer |
| copy dest A | `0x800611AC` then 16 `sb` at `$a1+0..+3` | `$a1 = 0x801398C0` | `0x801398C0` | RGB bytes + alpha; not the heap pointer |
| destructor | `0x80061254` | `jal rs_free` of `$a0` | `$a0` | destructor; no store; no post-free NULL |

The 16-iter walk (`$t0` `slti 0x10`) writes 16 words at
`0x801398C0..0x801398FC` and 16 words at
`0x80139920..0x8013995C`. `$a2` starts at `-1` and subtracts
`0x10` each iter; its low byte is stored as the fourth
channel. No `jal` occurs between `addu $a0, $v0` and
`rs_free`, so `$a0` is not clobbered.

`load_asset` (`0x8006488C`) calls `get_asset_size_extra`,
`rs_malloc` that size, DMA-fills, `teardownAssetDma`, and
returns `$s2` (`$v0`). That contract was classified in
s3606/s3611; there is no second pointer source. `rs_free`
itself `beq $s0, $zero` and returns, so a NULL malloc is a
skip, not a Gap. The copy dereferences `$a0` before the
free, so a NULL return would fault first; that is the same
unproven allocator-failure edge s3604–s3624 left open.

## Dest-array consumers (not the heap pointer)

Every remaining `-0x6740`/`-0x66E0` with `lui 0x8014` passes
the color-table *address* into a spawn extra-arg. None
`lw`s a word from those bases as a pointer, and none
`jal rs_free`:

| Function | PC | Address passed | Consumer |
|---|---|---|---|
| `triggerObjectDestructionEffects` | `0x800748A8` | `0x80139920` as `$a2` | `spawnMinimalRandomNpc` → `spawnNpcOfType` `0x18($sp)` |
| `triggerObjectDestructionEffects` | `0x80074A90` | `0x801398C0` as `$a2` | same |
| `npcPowerGeneratorHandleDestruction` | `0x800767B0` | `0x801398C0` as `$a2` | same |
| `spawnGatedDistanceEffectPair` | `0x8007730C` | `0x80139920` into `0x18`/`0x1C($sp)` | `spawnNpcOfType` |
| `emitPresetSparkBurst` | `0x8007DE80`/`84` | terrain-select `0x80139920` vs `0x801398C0` into `0x78($sp)` | spawn extra-arg |
| `spawnAtAtFootstepDustBurst` | `0x800CD47C`/`80` | same select into `0x78($sp)` | spawn extra-arg |

`orientVwingSubmodelByQuat` `0x800B98F4` is `lui 0x8011` +
`-0x66E0` = `0x80109920`, a different object. Excluded.

`spawnMinimalRandomNpc` (`0x80061380`) stores `$a2` at
`0x18($sp)` and calls `spawnNpcOfType`; it has no
`jal rs_free`.

## Pairing

The pointer is never stored, so no sibling can free it and
no post-free NULL is required. `loadWeaponsHobObjects` does
not keep `$v0`/`$a0`. A second `loadExplosionTextures` would
malloc, recopy, and free a new buffer; the previous buffer
is already freed at the first return.

## Classification

The only `jal rs_free` that can receive this pointer is
`0x80061254`, and `$a0` is the matching `load_asset`
`rs_malloc`. The 16-iter dest tables are RGB copies, not
the heap pointer. No original non-allocator writer exists.
This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope. `H-NextClassUnevaluable` is not
selected: one original heap-pointer writer, never stored.

No guard was added. Runtime allocator state, DMA fill, and
`0x80130B70` index legitimacy remain unproven.

## Next remaining `jal rs_free`

`funcs_13.c` is exhausted. Next: `loadAndRelocateAsset`
`0x800555C4` in `funcs_12.c`. `$s1` is the `load_asset`
return at `0x800554F8`; an 8-iter relocate walk uses
`$s1+4` as base, then `registerHmtTextureInTable` and
`rs_free($s1)`. Sibling call from the same
`loadWeaponsHobObjects` parent (`0x8005E880`).
