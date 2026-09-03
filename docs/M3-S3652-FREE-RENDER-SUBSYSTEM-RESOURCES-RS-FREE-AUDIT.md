# M3 s3652 — freeRenderSubsystemResources rs_free of *0x8011A444 and four siblings

## Work unit

Static census of `freeRenderSubsystemResources`
`jal rs_free` at `0x80018668` (`$a0` =
`*0x8011A444`, `lui 0x8012; lw -0x5BBC`).
Enumerated every original load/store of
that word (including the matching allocator,
every later store, whether any caller holds
the buffer, and the four sibling `jal rs_free`
in the same wrapper at `0x80018680` /
`0x80018698` / `0x800186A8` / `0x800186B8`
of `*0x801163B4`, `*0x801143AC`,
`*0x8010E8A8`, `*0x8010E8AC`) and every
`jal rs_free` that can receive those
pointers. Other loads were classified as
consumers or as a second free. No build or
runtime run was performed.

Absolute `0x8011A444` never appears in
generated code. The word is gp-relative
from `0x80120000`: `-0x5BBC` =
`0x8011A444`. s3650's `*0x8012A444` label
for this same `-0x5BBC` load is a
transcription error; the lui/offset math
is `0x8011A444`.

The discriminator was the single complete
original census of those five `jal rs_free`
sites plus every original `lw`/`sw` of the
five globals that can become this `$a0`,
and every `jal rs_free` that can receive
those pointers. No overlay duplicate of
`freeRenderSubsystemResources` /
`0x80018650` exists as a second generated
body.

- H-NextClassGap: a remaining free can pass a
  pointer that is not the matching allocator
  store, or can free it after a sibling already
  released it without a NULL.
- H-NextClassComplete: every remaining free is
  a destructor of a matching init store, and
  only runtime allocator legitimacy remains.
- H-NextClassUnevaluable: mixed object
  identities or unshared writers prevent a
  complete classification of a pointer source.

Closed classes were not repeated. Host
`MATERIAL_ARRAY_PTR_GUARD` at `0x80018664`
is not an original skip of this free. Do
not land a skip-path NULL store for the
s3636 overlay Gap unless this census
identifies that same writer as this word.

## Census size

Original `jal 0x80001C98` in `funcs_4.c`: 5
sites, all in this wrapper. `funcs_5.c` and
`funcs_3.c` have zero sites.

`freeRenderSubsystemResources` is
`0x80018650`..`0x800186D4`, frame `-0x18`.
Zero generated `jal 0x80018650`. Zero
`LOOKUP_FUNC(0x80018650)`. Zero `lui`/`addiu`
function-pointer constructions of
`0x80018650`. One overlay-table entry
(rom offset `0x18210`, size `0x88`); not a
second generated body. Single `jr $ra` at
`0x800186D0`. `data_gap_800186D8` starts at
`0x800186D8` immediately after. Zero
`static_*` clones of these PCs. The
destructor is original code reachable only
through that overlay mapping.

Sequence, all straight-line after
`destroyTextureLUTs` (closed s3650):

1. Load `*0x8011A444`; `jal rs_free`. No
   original NULL skip. No post-free NULL.
2. Load `*0x801163B4`; `beq` zero skip;
   else `jal rs_free`. No post-free NULL.
3. Load `*0x801143AC`; `beq` zero skip;
   else `jal rs_free`. No post-free NULL.
4. Load `*0x8010E8A8`; `jal rs_free`. No
   original NULL skip. No post-free NULL.
5. Load `*0x8010E8AC`; `jal rs_free`. No
   original NULL skip. No post-free NULL.
6. `selectAndApplyViMode`; return 1.

Host `MATERIAL_ARRAY_PTR_GUARD` at
`0x80018664` replaces an OOB loaded value
with `0x80000000` and still calls
`rs_free`; that is not an original skip.

## `*0x8011A444` accesses

31 original `lui 0x8012` `-0x5BBC` sites.
`funcs_9.c` `lwc1` `0x80040BBC` uses
`$at = 0x8004` (`0x8003A444`), not this
word.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| malloc | `0x80017D1C`/`0x80017D28` | `jal rs_malloc($t0<<2, 0)`; `sw $v0, -0x5BBC` | `*0x8011A444` | live heap-pointer writer |
| zero-fill | `0x80017DAC` | `lw -0x5BBC`; `sh $zero, 0x0` stride `4` | `*0x8011A444` | consumer of the just-stored table |
| destructor | `0x80018664`/`0x80018668` | `lw -0x5BBC`; `jal rs_free` | `*0x8011A444` | destructor; no NULL skip; no post-free NULL |
| 28 other loads | see consumers | `lw -0x5BBC` | `*0x8011A444` | table-base consumers; none `jal rs_free` of this pointer |

There is no `sw $zero` of `-0x5BBC`. Failed
malloc still stores `$v0 == 0`.

## Sibling accesses

Only original stores of the four siblings
are in `buildAndRegisterDefaultMaterial`.
`initHudStruct` `addiu $a1, 0x63B4` at
`0x800C0D7C` has no `lui 0x8011`; it is a
different object.

| Global | Allocator PC | Size / flags | Flag-skip NULL | Destructor |
|---|---|---|---|---|
| `*0x801163B4` (`lui 0x8011; 0x63B4`) | `0x80017D40`/`0x80017D4C` | `(*0x8011A8B4)<<4`, flags 0 | `$s1 & 0x1000` → `sw $zero` `0x80017D5C` | `0x80018680`; `beq` zero skip |
| `*0x801143AC` (`lui 0x8011; 0x43AC`) | `0x80017D74`/`0x80017D80` | `(*0x8011A8B4)<<4`, flags 0 | `$s1 & 0x800` → `sw $zero` `0x80017D90` | `0x80018698`; `beq` zero skip |
| `*0x8010E8A8` (`lui 0x8011; -0x1758`) | `0x80017E54`/`0x80017E64` | `(count+1)<<3`, flags 0 | none; skipped only if `registerHmtTextureInTable` returns `0xFFFF` | `0x800186A8`; no NULL skip |
| `*0x8010E8AC` (`lui 0x8011; -0x1754`) | `0x80017E68`/`0x80017E74` | `(count+1)<<1` from saved `*0x8011A8B8`, flags 0 | same early-out | `0x800186B8`; no NULL skip |

`0x80017FB0` walks `*0x8010E8AC` with
`sb $zero, 0x0($base+$a2)` after the
second malloc. Consumer, not a store of
the global.

No other function contains a `jal 0x80001C98`
that loads these four words.
`uploadTextureDescriptorData` `0x800232CC`
(closed s3651) frees `$s1`, not these
globals. Its `-0x5BBC` load at `0x80023290`
is a table-base consumer.

## Object identity

### Live allocator — `buildAndRegisterDefaultMaterial`

`buildAndRegisterDefaultMaterial` is
`0x80017B88`..`0x80018188`, frame `-0x70`.
Two generated `jal 0x80017B88`
(`advanceVideoFrame` `0x800183F8`,
`initVideoBootWrapper` `0x800185DC`).
Zero `LOOKUP_FUNC(0x80017B88)`. Zero
`lui`/`addiu` constructions. One
overlay-table entry (rom offset `0x17748`,
size `0x604`); not a second generated body.

`$t0` is incoming `lhu 0xB2($sp)`, stored
to `*0x8011A8B4` (`-0x574C` from `0x8012`)
at `0x80017D08`. Material-array malloc
size is that count `<< 2` (word-stride
slots). Flags `0` is not flags-4 and not
flags-8. No original NULL check of `$v0`
before the store. If the count is `> 0`,
walk `*0x8011A444` with stride `4` and
`sh $zero, 0x0`.

The `$s1` flag bits that skip the two
count`<<4` mallocs store NULL instead;
those NULLs are the destructor's `beq`
zero skips. The last two mallocs run only
after `registerHmtTextureInTable`
(`0x80017DF8`) returns a slot other than
`0xFFFF`. The early-out at `0x80017E10`
returns 0 without storing
`*0x8010E8A8` / `*0x8010E8AC`, leaving
BSS zero or a previous matching store.

The only live original heap-pointer writer
of `*0x8011A444` is the flags-0 malloc
store at `0x80017D28`. The only live
heap-pointer writers of the four siblings
are the four stores above (or the two
flag-skip NULLs).

Neither generated caller of the allocator
holds these pointers across the call. A
second init overwrites the globals without
freeing the previous set. That is a leak
of the first mallocs, not a second free.
The destructor still receives the latest
matching allocator store.

`initTextureMaterialPools` (`0x80022844`)
loads `-0x5BBC` at `0x80022968` as a
zero-fill walk of slot `+4`; it does not
store any of the five globals. Zero
generated `jal 0x80022844`. Unreferenced
consumer, not a second writer.

### Consumers — table-base reloads, not a second free

28 remaining 0x8012-base `-0x5BBC` loads
(18 functions besides the allocator and
destructor) use the global as a table
base (`index << 2`, then `lhu 0x0` /
field reads). None of those functions
contains a `jal 0x80001C98` of this
pointer.

`releaseTextureLutEntry` is the most
free-shaped name: its `-0x5BBC` load is
followed by `index << 2`, `lhu 0x0`, and
`sh $zero` of that slot; it does not
`jal rs_free`. The other 17
(`emitMaterialTexturedDL` /
`emitMaterialTexturedDLAlt`,
`transformSceneLights`,
`renderFlatMeshFaceGroup`,
`renderUnlitMeshFaces`,
`resetVertexCacheSlot`,
`renderLitMeshFaceGroup`,
`drawSubtitleText`,
`getTextureDimsBySlot`,
`parseHmtMaterials`,
`registerHmtTextureInTable`,
`findMatchingTextureRecursive`,
`findTextureByName`,
`copyTextureDescriptorWithData`,
`fillTextureDescriptorNoCopy`,
`loadAndDecodeTexture`,
`uploadTextureDescriptorData`,
`getTextureDataByMaterialId`,
`getTextureAttrBySlot`,
`flushDebugTextOverlay`) are the same
index-into-table shape.

Sibling consumers (`heapFreeListDequeue`,
`emitTexturedFaceGeometry`,
`parseHmtMaterials`, `findTextureByName`,
mesh/subtitle/light walks of `-0x1758` /
`-0x1754`) likewise contain no
`jal 0x80001C98` of those pointers.

### Caller-side stores

`freeRenderSubsystemResources` does not
publish `$v0` other than returning 1. It
does not reload any of the five globals
after freeing them. Sequential double-free
of the dangling post-free globals would
require a second call of this destructor;
it has no generated caller.

These words are not the s3636 overlay
`0x1C` / `0x20` writer.

Failed malloc (`$v0 == 0`) still stores
NULL and a later destructor call reaches
`rs_free`, which skips. The zero-fill
walks and every consumer would dereference
first. That is the same unproven
allocator-failure edge s3604–s3651 left
open.

## Pairing

One generated destructor of all five
words. There is no second `jal rs_free` of
any of them. The unreferenced
`initTextureMaterialPools` consumer cannot
fire as a writer. Same unchecked-NULL
destructor shape already closed as
Complete for `destroyTextureLUTs` (s3650)
and earlier classes. Runtime allocator
legitimacy and whether every call's malloc
succeeds remain unproven. Re-init without
an intervening destroy leaks the previous
set; it does not feed a non-allocator
pointer to the free.

## Classification

The only `jal rs_free` sites that can
receive these pointers are `0x80018668`,
`0x80018680`, `0x80018698`, `0x800186A8`,
and `0x800186B8`. The only live original
heap-pointer writers are the flags-0
malloc stores at `0x80017D28`,
`0x80017D4C`, `0x80017D80`, `0x80017E64`,
and `0x80017E74` (plus the two flag-skip
NULLs for `0x63B4` / `0x43AC`). All other
loads are table-base consumers. Host
`MATERIAL_ARRAY_PTR_GUARD` substitutions
are not original skips. This selects
`H-NextClassComplete`. `H-NextClassGap`
is refuted at static scope.
`H-NextClassUnevaluable` is not selected:
five globals, one live allocator function,
one destructor wrapper.

No guard was added. Runtime allocator
state remains unproven. The s3636 overlay
skip-path NULL store was not landed: these
words are not that writer.

## Next remaining `jal rs_free`

`funcs_4.c` original `jal 0x80001C98` is
exhausted. `funcs_3.c`, `funcs_5.c`, and
`funcs_0.c` have zero sites. The next
remaining original sites are in
`funcs_2.c`: `initSaveData` `0x8000671C`
(`$a0` = `$s2`) and the sibling at
`0x8000672C` (same `$s2`), then
`freeSaveDataBuffer` `0x80006774`
(`$a0` = `*0x80112724`).
