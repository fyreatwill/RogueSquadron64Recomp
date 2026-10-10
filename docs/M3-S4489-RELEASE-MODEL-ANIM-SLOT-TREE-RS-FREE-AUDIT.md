# M3 s4489 — releaseModelAnimSlot rs_free of the flattened tree

## Work unit

Static census of the third original `jal rs_free` in
`releaseModelAnimSlot` (`0x80082CFC`, size `0x11C`), at
`0x80082DC0`. ROM: `lw $a0, -0x5670($at)` at `0x80082DBC`
(`0x8C24A990`), jal word `0x0C000726`, delay `nop` at
`0x80082DC4` (`0x00000000`). The delay does not write
`$a0`. The freed value is the word at slot `+0x00`. The
jal is reached only when `lbu $v0, -0x565F($at)` at
`0x80082DA8` is nonzero. No build or runtime run was
performed. The per-channel free at `0x80082D5C` (s4487)
and the channel-array free at `0x80082D98` (s4488) were
not re-audited.

The discriminator was every original assignment of the
slot base and of the word at `+0x00` from the prologue
through the free, every store that can produce that
word, the gate byte's stores, plus every callee
`jal rs_free` and every caller argument:

- H-NextClassGap: that word can be a non-allocator
  value, or a pointer a sibling already freed, with
  the writer named.
- H-NextClassComplete: that word is a matching
  allocator return on every path that reaches the jal,
  and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer
  identity can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98`
comment scan still locates closed `0x80082430`, closed
`0x80082D5C`, closed `0x80082D98`, and this site in
`funcs_20.c`, still locates closed `0x8007A814`, closed
`0x8007B23C`, and closed `0x8007BE50` in `funcs_19.c`,
still locates `0x80072E40` in `funcs_18.c`, and still
locates `0x8006F378` in `funcs_17.c`. The ROM word
`0x0C000726` matches `0x80082D98` and `0x80082DC0`, and
the closed sites above. A scan that missed `0x80082D98`
or `0x8007BE50` would have been invalid. ROM and the
generated listing agree on the free sequence. The
generated `beq` target is `L_80082DC8`, which is the
instruction after the delay slot.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_20.c`, `0x80082DC0` | word at slot `+0x00` (`D_8013A990 + (id - 1) * 0x14`) | delay `nop`; skipped when byte `+0x11` is 0 | sole free of that slot's flattened-tree `rs_malloc`, once per call |

`$a0` on entry is a 1-based slot id. `$s3 = $a0 - 1` at
`0x80082D04`. The byte offset is recomputed at
`0x80082D80` as `($s3 * 5) << 2`, which is `$s3 * 0x14`.
`rs_free` saves and restores `$s0`, and the array-free
delay is `nop`, so that offset is still in `$s0` at
this load. `lui $at, 0x8014` plus that offset addresses
`D_8013A990`. The load immediate `-0x5670` is slot
`+0x00`.

The gate is `beqz` at `0x80082DAC` (ROM `0x10400006`,
target `0x80082DC8`). The delay is `nop`. The target is
the `lui` after this jal, so a zero byte skips the jal
and does not free in the delay slot. Nothing in this
function writes `$a0` between the load and the jal.
There is no branch back to the jal.

## What the word is

The only `lui $at, 0x8014` stores of immediate
`-0x5670` in the main image (`0x80000400` through
`0x800FC71C`) are:

| PC | Store | Function |
|---|---|---|
| `0x80082898` | `sw $zero` | `resetModelAnimSlotTable`, all 32 slots |
| `0x80082944` | `sw $a0` | `allocateModelAnimSlot`, the found slot |
| `0x80082DD0` | `sw $zero` | this function, after the jal |

The only other memory op in that range with the same
immediate and a nearby `lui $at, 0x8014` is the load at
this jal and `lw $v0, -0x5670($at)` at `0x800835E4` in
`parseModelAnimType2Entry`. The `lwc1` at `0x8004E7EC`
uses `lui $at, 0x8004` and is a float pool
(`0x8003A990`), not this table.

`$a0` at `0x80082944` is `allocateModelAnimSlot`'s
incoming argument. From the prologue at `0x800828D0`
through that store there is no jal and no write of
`$a0`. A full table leaves `$s3` at 0. `beqz` at
`0x80082928` (target `0x80082A6C`) returns 0 and does
not store.

That incoming `$a0` is the return from `jal rs_malloc`
at `0x80082B2C` in `flattenAnimTreeAndAllocateSlot`.
The delay `sll $a0, $s3, 2` is the size. Flags are 0
(`addu $a1, $zero, $zero` at `0x80082B28`). `$s3` is
`lhu $s3, 0xE($v0)` and `$v0` is `lw $v0, 4($s2)`, so
the size is the halfword at `+0xE` of `*($a1 + 4)`,
shifted left by 2. `addu $s0, $v0` at `0x80082B34` is
the only write of `$s0` before the call to allocate.
`appendAnimHandleAndDescendantsToBuffer` saves and
restores `$s0` and contains no `jal rs_free`. Its two
calls pass a child node, not this pointer.

Both arms of the `beql` at `0x80082B64` pass `$s0` as
`$a0`. The taken delay is `addu $a0, $s0, $zero` and
the branch target is `0x80082B78`. The fall-through
executes the same `addu` at `0x80082B74`. The next
instruction sets `$a1` to the header and the delay of
`jal allocateModelAnimSlot` sets `$a2` to the same
halfword. `allocateModelAnimSlot` has one caller (jal
word `0x0C020A34` at `0x80082B7C`). The raw pointer
`0x800828D0` occurs zero times.

`allocateModelAnimSlot`, `flattenAnimTreeAndAllocateSlot`,
and `appendAnimHandleAndDescendantsToBuffer` contain
no `jal rs_free`. The two `jal rs_malloc` calls inside
allocate (`0x80082968`, `0x80082A00`) create the
channel array and the per-channel buffers. Those
returns are stored at slot `+0x0C` and at record
`+0x0C`. They are not this `$a0`.

## The gate byte

`allocateModelAnimSlot` clears byte `+0x11` at
`0x800829A0` (`sb $zero, -0x565F($at)`) after storing
the pointer and after setting the occupied byte at
`+0x10`. `flattenAnimTreeAndAllocateSlot` then sets
that byte to the constant 1 at `0x80082BA8`, and only
when allocate's id is nonzero. `beqz` at `0x80082B88`
(target `0x80082BAC`) skips the store and returns 0.
Those are the only `lui $at, 0x8014` stores of
immediate `-0x565F` in the main image. The only load
is the gate at `0x80082DA8`.

A zero byte therefore means this call did not finish
a successful allocate of that slot. The jal is not
taken. The post-jal `sw $zero` at `0x80082DD0` is on
the far side of the jal and is not reloaded. It does
not feed this jal on the same call.

## The other two frees are different blocks

`0x80082D5C` frees record `+0x0C` of the channel array
(s4487). `0x80082D98` frees slot `+0x0C` itself
(s4488). Both load immediate `-0x5664`, not
`-0x5670`. The tree buffer is allocated before
allocate's own mallocs and is a different size
(`halfword << 2`, not `count << 4` and not
`$a2 << 3`).

`parseModelAnimType2Entry` loads the tree at
`0x800835E4`, adds an index, and reads a node. The
function contains no `jal rs_free` and does not store
the pointer back to the slot. The words it writes are
inside nodes reached from the tree, not slot `+0x00`.

## Zero size and a full table

`rs_malloc` copies the size to `$s0` at `0x80001AD4`,
clears `$s2` at `0x80001AE4`, and `beqz $s0` at
`0x80001AF0` (target `0x80001C74`) returns `$v0 = $s2`.
The delay stores `$ra` and does not write `$s2`. A
zero halfword therefore returns 0. `flatten` then
executes `sw $v0, 0($s0)` at `0x80082B48` before
allocate. That is a store through address 0, so this
edge faults before the pointer is published, or
allocate stores 0. `rs_free` returns on `$a0 == 0`
(`beq` at `0x80001CA4`). The value is still that
allocator return.

If all 32 slots are occupied, allocate returns 0
without storing `$a0`, and flatten does not set the
gate. The tree pointer is not published and this jal
does not see it. That is a leak of an unstored block,
not a second value at slot `+0x00`.

## Reset writes 0, not another pointer

`resetModelAnimSlotTable` zeros `+0x00`, `+0x04`,
`+0x08`, and the occupied byte. It does not clear
`+0x11` or `+0x0C`. Two callers, jal word
`0x0C020A1C`: `reset_model_animations` at `0x800F9F34`
and `reset_and_free_model_animations` at `0x800F9FB0`.
The latter first frees 16 words at `0x8010C4A0` (stride
`0x24`). That is a different table. The tree pointer
is not copied there: flatten's only publication of
`$s0` is the `$a0` passed into allocate.

If reset runs while the gate is still 1, a later
release loads 0 from `+0x00` and `rs_free` skips it.
The original pointer was dropped by the clear, not
freed twice. The same call's `sw $zero` at
`0x80082DD0` has the same shape after a normal free.
This function also does not clear `+0x11`. A second
call still sees the gate set, but the word is already
0, and it first reloads the header word that this
function stored as 0. That is not a new writer of the
tree pointer.

## id 0

An id of 0 makes `$s3 = -1` and the byte offset
`-0x14`. This jal would load `0x8013A97C`. The gate
byte would be `0x8013A98D`. Both sit in the unnamed
gap between the four words of `gNewButtonsPressed`
(`0x8013A960` through `0x8013A970`; `sltiu` bound
`0x4`, stride 4, in `setNewAndPreviousButtonsPressed`
and `initNewAndPreviousButtonsPressed`) and
`D_8013A990`.

No `lui`/`addiu` pair in the main image builds an
address in `0x8013A970`..`0x8013A990`. No store of
immediate `-0x5684` or `-0x5673` has a nearby
`lui` of `0x8013` or `0x8014`. Allocate only writes
ids 1..32. The gap bytes are not stored by this idiom,
so the id-0 gate stays 0 and the `beqz` skips the jal.
That address is not a second identity of a published
slot's tree pointer.

## Callers

Seven ROM hits of jal word `0x0C020B3F`. The raw
pointer `0x80082CFC` occurs zero times. Each passes an
object field. `flattenAnimTreeAndAllocateSlot` returns
allocate's id (`addu $v0, $a0` at `0x80082BAC`, and
`$a0` there is that id). It does not return the tree
pointer. Each of these fields is that returned id:

| Caller | Release PC | Field | Stored from flatten's return |
|---|---|---|---|
| `tickAtAtAudioAndWeaponState` | `0x800CC9DC` | `0x78($s0)` | `0x800CCAA4` |
| `npcAtAtUpdate` | `0x800CDE64` | `0x78($s1)` | `0x800CDD80` |
| `npcAtStHandleDestruction` | `0x800CF8F4` | `0x8C($s1)` | same offset as `advanceAtStDeathAnimPhase` |
| `advanceAtStDeathAnimPhase` | `0x800CFD2C` | `0x8C($s0)` | `0x800CFE44` |
| `npcAtStUpdate` | `0x800D0450` | `0x8C($s2)` | `0x800D03AC` |
| `npcAtPtPlaySkywalkerErrorCallout` | `0x800EA490` | `0x94($s0)` | `0x800EA5A8` |
| `npcAtPtUpdate` | `0x800EAAD8` | `0x94($s1)` | `0x800EAA44` |

An eighth `jal flattenAnimTreeAndAllocateSlot`, at
`0x800D24C4` in `playerAtStUpdate`, stores the id at
`0x80($s2)` (`0x800D24D8`). No `jal releaseModelAnimSlot`
uses offset `0x80`. That path does not pass the tree
pointer to a free. If nothing else releases the id,
the block leaks. It is not a second value at this jal.

`npcAtPtUpdate`'s next `jal rs_free`, at `0x800EAAE4`,
loads `0x4C($s1)`. That is a different field.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at
static scope: the only nonzero store of slot `+0x00`
is the `rs_malloc(halfword << 2, 0)` return, no callee
frees that pointer before the jal, and the other two
jals in this function free different blocks. A later
0 is the named clear in reset or the post-jal clear,
and `rs_free` skips 0. H-NextClassUnevaluable is not
selected. id 0 names a gap address this idiom never
stores, and its gate byte stays 0. Runtime allocator
legitimacy remains unproven. No guard was added.

The next unaudited `jal rs_free` in address order is
`audioSeqFree` at `0x80083C58` (entry `0x80083C50`).
ROM delay is `nop`. The prologue saves `$ra` and does
not write `$a0`, so the freed value is the incoming
argument. A first scan, not a classification: jal word
`0x0C020F14` occurs zero times in the ROM, and the
32-bit constant `0x80083C50` occurs zero times.
`audioSeqMallocZero` returns at `0x80083C48` and does
not fall into this function.
