# M3 s3617 — remaining actor +0x4C rs_free in npcAtAtUpdate / npcAtStUpdate

## Work unit

Static census of every generated original `jal rs_free` of actor
field `+0x4C` in `npcAtAtUpdate` and `npcAtStUpdate`. Remaining
funcs_37 actor frees after the closed tickMultiPartVoiceLine
class: `0x800CDE8C` of `0x4C($s1)` and `0x800D0480` of
`0x4C($s2)`, plus the sibling `0x800D0DC0` of `0x4C($s2)` in
the same AT-ST update. Classified each pointer's writer and
whether a free can run on a non-allocator or already-freed
value. `playerAtStUpdate`'s `0xA4`/`0xBC` frees were not
included. No build or runtime run was performed.

The discriminator was the single complete original census of
those `jal rs_free` sites plus every original `sw` of `+0x4C`:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: tickMultiPartVoiceLine,
freeModelViewerMeshChain, shutdownModelViewer header-word,
lookup-table, loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`, format-message
`rs_free`, speech-file `rs_free`, speech/cache `rs_free`,
destructor skipped-NULL, destructor unchecked-free, `-0x6904`
alias, remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT publication,
mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `npcAtAtUpdate` / `npcAtStUpdate`:
three sites, all this class. `funcs_37.c` still has later
`rs_free` in `playerAtStUpdate` (`0xA4($s2)` and `0xBC($s4)`).

| Pointer | Slot | Original writers | Matching malloc | Destructors |
|---|---|---|---|---|
| AT-AT craft NPC context | `0x4C($s1)`, `$s1=0x4($a0)` | opcode-1 `sw $v0, 0x4C($s1)` `0x800CDB6C` | `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` `0x8006BD44`, returned `$v0=$s1` | teardown `0x800CDE8C` of `$a0`; no skip, no post-free NULL |
| AT-ST craft NPC context | `0x4C($s2)`, `$s2=0x4($a0)` | opcode-1 `sw $v0, 0x4C($s2)` `0x800D0264`; lethal opcode-5 `sw $zero, 0x4C($s2)` `0x800D0DD4` | same `rs_malloc(0x1E4)` | teardown `0x800D0480` of `$a0` (NULL skip, no post-free NULL); lethal opcode-5 `0x800D0DC0` of `$a0` (NULL skip, then NULL) |

Those two `sw $v0, 0x4C` are the only original stores of the
malloc return as a heap pointer on these actors. `rs_free`
itself `beq $s0, $zero` at `0x80001CA4` and returns, so a NULL
`$a0` is a skip, not a Gap.

Other original `+0x4C` word stores in these two functions are
not this pointer: `npcAtAtHandleDestruction` `0x800CD35C` and
`npcAtAtUpdate` `0x800CED9C` `or` flag bits `0x40000000` /
`0x80000000` into `0x4C(0x34(actor))`. `playerAtStUpdate`
`sw $zero, 0x4C($s2)` `0x800D2434` is a different object.

## Remaining functions

Both updates are table-dispatched on `(a1-1)<9`. `$a0` is the
wrapper; the actor is `0x4($a0)`. Case 0 is setup (opcode 1),
case 1 is teardown (opcode 2), case 4 is damage (opcode 5).
No generated `jal` reaches either update.

### `npcAtAtUpdate` (`0x800CD71C`) — one free

Frame is `-0x120`. `$s4=$a0` (wrapper), `$s1=0x4($s4)`.

Opcode 1 (`L_800CD78C`, also case 7) ORs wrapper `+0x14` with
`0x100`, then `jal allocateAndInitCraftNpcContext` at
`0x800CDB58` with `$a2=0xB` and stores `$v0` to `0x4C($s1)` at
`0x800CDB6C`. It then writes floats into `+0x14/+0x4/+0x10/+0x18`
of that return.

Opcode 2 (`L_800CDE48`): optional anim-slot cleanup, then
`lw $a0, 0x4C($s1)` and `jal rs_free` at `0x800CDE8C` with no
NULL skip and no post-free NULL. It then `destroyNpcSlotByIndex`
of `+0xE0`/`+0xE2` when not `0xFFFF`, `clearPendingAndDestroyChildNpc`
of `+0x38`, `releaseMeshAsset` of `+0x30`, and returns 1.

Opcode 5 (`L_800CEA0C`) calls `npcAtAtHandleDestruction` and
does not `jal rs_free`.

### `npcAtStUpdate` (`0x800CFE7C`) — two frees

Frame is `-0xF8`. `$s4=$a0`, `$s2=0x4($s4)`.

Opcode 1 (`L_800CFEE8`, also case 7) matches the AT-AT setup.
`jal allocateAndInitCraftNpcContext` at `0x800D024C` with
`$a2=0xA` and stores `$v0` to `0x4C($s2)` at `0x800D0264`.

Opcode 2 (`L_800D0434`): optional anim-slot cleanup, then
`lw $a0, 0x4C($s2)`; `beq $a0, $zero` skips; `jal rs_free` at
`0x800D0480` with no post-free NULL. It then
`destroyNpcSlotByIndex` of `+0x7A` when not `0xFFFF`,
`clearPendingAndDestroyChildNpc` of `+0x38`, `releaseMeshAsset`
of `+0x30`, and returns 1.

Opcode 5 (`L_800D0CBC`): on lethal `dealDamageToNpc` (`bgtz`
skip), `npcAtStHandleDestruction($s2)`, then `lw $a0, 0x4C($s2)`;
`beq $a0, $zero` skips; `jal rs_free` at `0x800D0DC0`; delay-slot
`sw $zero, 0x4C($s2)` of the following
`unregisterAndFreeNpcSlot(+0x72)`. Same NULL of `+0x4C` then
unregisters `+0x76`.

The two AT-ST frees are different switch cases of one
invocation, so they cannot both run in the same call.

## Matching init

### `allocateAndInitCraftNpcContext` (`0x8006BD18`) — only allocator

`rs_malloc(0x1E4)` at `0x8006BD44` (`$a1` flags 0) is captured
in `$s1`. The function does not NULL-check `$v0` before the
init stores. It writes shadow/texture, zeroed vecs, and
inlined sub-object pointers, then `addu $v0, $s1, $zero` at
`0x8006BE60` and returns that `$s1` through `0x8006BEC0`.

Generated `jal 0x8006BD18` that store the return to these
actors: `npcAtAtUpdate` `0x800CDB58` and `npcAtStUpdate`
`0x800D024C`. Other callers (`playerAtStUpdate` stores to
`0xBC($s4)`, plus unrelated NPC types) write different
objects and are not this class.

## Pairing / double-free

`destroyNpcSlotByIndex` (`0x8003ED74`) is the generated
teardown dispatcher. If wrapper `+0x1A != 0` it ORs flag
`0x8` onto `+0x14` and returns without `jalr`. Otherwise it
`jalr` wrapper `+0x0` with `$a1=2`, then
`reinsertNpcIntoSortedFreeList`, which `sw $zero, 0x4($a0)`
of the wrapper. Sequential opcode-2 is one send per destroy,
then the wrapper leaves the live list.

The live walk (`0x8003E92C`) increments `+0x1A` before `jalr`
and, after decrement to 0, calls `destroyNpcSlotByIndex` only
when flag `0x8` is set. A destroy requested during opcode 5
is therefore deferred until after that opcode returns.

AT-ST lethal opcode 5 NULs `+0x4C` before any deferred
opcode 2. Opcode 2's NULL skip then skips `rs_free`.
Teardown-first cannot then take opcode 5: the wrapper is
already on the free list. AT-AT never frees `+0x4C` on
opcode 5; only opcode 2 does. A NULL word is `rs_free`'s
own skip.

AT-AT opcode 2 does not NULL `+0x4C`. That leaves a dangling
word on an actor the wrapper then detaches; it is not a
second pointer source. Opcode 1 overwriting a live `+0x4C`
without a prior free would leak the 0x1E4 object, matching
the unproven re-init / allocator edges s3604–s3616 left
open.

This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope: every remaining free is the
matching `rs_malloc(0x1E4)` or NULL. `H-NextClassUnevaluable`
is not selected: `$s1`/`$s2` are `0x4(wrapper)` and the
`+0x4C` pointer is that one craft-context object. Runtime
allocator/lifetime legitimacy remains unproven. No guard
or runtime change followed.

`funcs_37.c` still has later `rs_free` in `playerAtStUpdate`
(`0xA4($s2)` and `0xBC($s4)`).
