# M3 s4488 — releaseModelAnimSlot rs_free of the channel array

## Work unit

Static census of the second original `jal rs_free` in
`releaseModelAnimSlot` (`0x80082CFC`, size `0x11C`), at
`0x80082D98`. ROM: `lw $a0, -0x5664($at)` at `0x80082D94`
(`0x8C24A99C`), jal word `0x0C000726`, delay `nop` at
`0x80082D9C` (`0x00000000`). The delay does not write
`$a0`. The freed value is the word at slot `+0x0C`. No
build or runtime run was performed. The per-channel free
at `0x80082D5C` (s4487) was not re-audited. The later jal
at `0x80082DC0` was not classified.

The discriminator was every original assignment of the
slot base and of the word at `+0x0C` from the prologue
through the free, every store that can produce that word,
plus every callee `jal rs_free` and every caller argument:

- H-NextClassGap: that word can be a non-allocator value,
  or a pointer a sibling already freed, with the writer
  named.
- H-NextClassComplete: that word is a matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates closed `0x80082430`, closed
`0x80082D5C`, and this site in `funcs_20.c`, still locates
closed `0x8007A814`, closed `0x8007B23C`, and closed
`0x8007BE50` in `funcs_19.c`, still locates `0x80072E40`
in `funcs_18.c`, and still locates `0x8006F378` in
`funcs_17.c`. The ROM word `0x0C000726` matches
`0x80082D5C` and `0x80082D98`. A scan that missed
`0x80082D5C` or `0x8007BE50` would have been invalid.
ROM and the generated listing agree on the free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_20.c`, `0x80082D98` | word at slot `+0x0C` (`D_8013A990 + (id - 1) * 0x14`) | delay `nop` does not write `$a0` | sole free of that slot's `rs_malloc(count << 4, 0)` block, once per call |

`$a0` on entry is a 1-based slot id. `$s3 = $a0 - 1` at
`0x80082D04`. The slot byte offset is `($s3 * 5) << 2`
(`sll` / `addu` / `sll` at `0x80082D80`–`0x80082D88`),
which is `$s3 * 0x14`. That offset is recomputed at
`L_80082D80`; it does not depend on the per-channel loop.
`lui $at, 0x8014` plus that offset addresses
`D_8013A990`. The load immediate `-0x5664` is slot
`+0x0C`.

The count check at `0x80082D34` (`beqz`, ROM
`0x10400012`, target `0x80082D80`) skips the per-channel
loop when the word at 0 of slot `+0x08` is 0. Both arms
fall through to this jal. Nothing in this function writes
`$a0` between the load and the jal.

## What the word is

The only store in the ROM whose immediate is `-0x5664`
and whose preceding `lui` is `0x8014` is `sw $v0,
-0x5664($at)` at `0x80082984` (ROM `0xAC22A99C`), inside
`allocateModelAnimSlot`. Twenty-seven loads use that
same pair. No other store does. `lwc1` hits of the same
immediate at `0x8004EA54` use `lui $at, 0x8004` and are
a float pool.

`$v0` at `0x80082984` is the return of `jal rs_malloc`
at `0x80082968`. The delay `sll $a0, $a0, 4` runs before
the call. The instructions between the return and the
store reload the header into `$v1` and rebuild `$at`.
They do not write `$v0`. `$s0` is the slot byte offset,
computed before the jal and preserved across it. The
size is the word at 0 of the header (`lw $a0, 0($a1)`
at `0x80082960`) shifted left by 4. Flags are 0
(`addu $a1, $zero, $zero` at `0x80082964`).

`allocateModelAnimSlot` has one caller,
`flattenAnimTreeAndAllocateSlot` at `0x80082B7C` (one
ROM hit of jal word `0x0C020A34`). The raw pointer
`0x800828D0` occurs zero times. It returns the 1-based
slot id in `$s3` (`addu $v0, $s3` at `0x80082A6C`), not
this pointer.

## Count zero

`rs_malloc` sets `$s2` to 0 at `0x80001AE4`, then
`beqz $s0` at `0x80001AF0` (ROM `0x12000060`, target
`0x80001C74`) returns `$v0 = $s2` when the size is 0.
The delay stores `$ra` and does not write `$s2`. A zero
channel count therefore stores 0 at slot `+0x0C`.

`allocateModelAnimSlot` then reloads that count and
`beqz` at `0x800829A8` (target `0x80082A6C`) skips the
per-channel mallocs. `releaseModelAnimSlot`'s count
check takes the same skip and still executes this jal.
`rs_free` returns on `$a0 == 0` (`beq` at `0x80001CA4`).
The value in `$a0` is still that allocator return.

## The per-channel free is a different block

`0x80082D5C` loads the array (`lw $v1, -0x5664($at)` at
`0x80082D4C`), adds `$s1 << 4`, and frees the word at
`0xC` of that record (`lw $a0, 0xC($v0)`, ROM
`0x8C44000C`). `$a0` there is not the array pointer.
That record word is the `rs_malloc($a2 << 3, 0)` return
stored at `0x80082A18` (s4487). The array is stored at
`0x80082984` before those per-channel mallocs, and the
loop indexes it, so the two returns are different live
blocks. The element free runs first. No other function
that loads `-0x5664` after `lui $at, 0x8014` contains
`jal rs_free`.

Readers do not replace the slot word. The only load
that puts it directly in `$a0`, other than this jal, is
`setModelAnimSlotCycleDuration` at `0x800832DC`. The
next instruction adds `$a1 << 4` and `swc1` writes
channel `+0x04`. That function has no `jal`. The other
loads index the array or reload record `+0x0C`. None
of them stores the array pointer back to the slot.

## id 0

An id of 0 makes `$s3 = -1` and the byte offset
`-0x14`. This jal then loads `0x8013A988`. The count
load is `0x8013A984`. Both sit in the unnamed gap
between `gNewButtonsPressed` (`0x8013A960`) and
`D_8013A990`. No `lui $at, 0x8014` access uses either
immediate, and neither address occurs as a 32-bit
constant in the ROM. The float-pool `lwc1`s at
`0x8004E3EC` and `0x8004E3FC` use `lui $at, 0x8004`.

The gap words are not a second allocated pointer. The
count load still dereferences address 0 when the gap
word is the initial zero. Runtime contents of address
0 were not read. If that word is 0, the count-zero
branch is taken and this jal frees the word at
`0x8013A988`, which nothing in this idiom stores. That
is not a second identity of a published slot's array.

## Not cleared after the free

After this jal the function zeros slot `+0x00`,
`+0x04`, `+0x08`, and the occupied byte. It does not
store slot `+0x0C`. A later call with the same id
therefore still sees the freed pointer, but only after
loading the header word that this function has already
set to 0 and then loading address 0. That is the same
allocator return, not a new writer. No guard was added.

Seven ROM hits of jal word `0x0C020B3F`. The raw
pointer `0x80082CFC` occurs zero times. Each passes an
object field, which this function consumes as a slot
id. `allocateModelAnimSlot` returns that id, not the
array pointer.

| Caller | PC | Argument |
|---|---|---|
| `tickAtAtAudioAndWeaponState` | `0x800CC9DC` | `0x78($s0)` |
| `npcAtAtUpdate` | `0x800CDE64` | `0x78($s1)`, after `0x70($s1)` is nonzero; the preceding delay clears `0x70` |
| `npcAtStHandleDestruction` | `0x800CF8F4` | `0x8C($s1)`, after `0x80($s1)` is nonzero; the preceding delay clears `0x80` |
| `advanceAtStDeathAnimPhase` | `0x800CFD2C` | `0x8C($s0)` |
| `npcAtStUpdate` | `0x800D0450` | `0x8C($s2)`, after `0x80($s2)` is nonzero; the preceding delay clears `0x80` |
| `npcAtPtPlaySkywalkerErrorCallout` | `0x800EA490` | `0x94($s0)` |
| `npcAtPtUpdate` | `0x800EAAD8` | `0x94($s1)`, after `0x88($s1)` is nonzero; the preceding delay clears `0x88` |

`npcAtPtUpdate`'s next `jal rs_free`, at `0x800EAAE4`,
loads `0x4C($s1)`. That is a different field.
s4487 already traced these fields to
`flattenAnimTreeAndAllocateSlot`'s returned id. This
pass re-disassembled the seven windows and did not
find a caller that passes the array pointer.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at
static scope: the only store of slot `+0x0C` is the
`rs_malloc(count << 4, 0)` return, no other function
frees that pointer, and the per-channel jal frees a
different block. Count zero stores and frees the NULL
that `rs_malloc` returns for a zero size. id 0 names a
different address that this idiom never stores, not a
second pointer. H-NextClassUnevaluable is not
selected. Runtime allocator legitimacy remains
unproven. No guard was added.

The next unaudited `jal rs_free` in address order is
still in `releaseModelAnimSlot`, at `0x80082DC0`
(`lw $a0, -0x5670($at)`, ROM `0x8C24A990`; delay
`nop`). It is gated by `lbu $v0, -0x565F($at)` at
`0x80082DA8`. A first scan, not a classification: the
`lui $at, 0x8014` stores of immediate `-0x5670` are
`sw $zero` at `0x80082898` (`resetModelAnimSlotTable`),
`sw $a0` at `0x80082944` (`allocateModelAnimSlot`), and
`sw $zero` at `0x80082DD0` (after this jal). The byte
at `-0x565F` is cleared at `0x800829A0` and set to 1
by `flattenAnimTreeAndAllocateSlot` at `0x80082BA8`.
`parseModelAnimType2Entry` only loads `-0x5670`.
