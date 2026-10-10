# M3 s4487 — releaseModelAnimSlot rs_free of the per-channel keyframe buffer

## Work unit

Static census of the first original `jal rs_free` in
`releaseModelAnimSlot` (`0x80082CFC`, size `0x11C`), at
`0x80082D5C`. ROM: `lw $a0, 0xC($v0)` at `0x80082D58`
(`0x8C44000C`), jal word `0x0C000726`, delay
`addiu $s1, $s1, 1` at `0x80082D60` (`0x26310001`). The
delay does not write `$a0`. The freed value is the word
at `0xC($v0)`. No build or runtime run was performed.
`applyCheatCodeFromInput` (s4486) was not re-audited.
The two later jals in this function (`0x80082D98`,
`0x80082DC0`) were not classified.

The discriminator was every original assignment of the
record base and of `$s1` from the prologue through the
free, every store that can produce the word at `0xC` of
that `0x10`-stride record, plus every callee `jal rs_free`
and every caller argument:

- H-NextClassGap: that word can be a non-allocator value,
  or a pointer a sibling already freed, with the writer
  named.
- H-NextClassComplete: that word is a matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates closed `0x80082430` and this site in
`funcs_20.c`, still locates closed `0x8007A814`, closed
`0x8007B23C`, and closed `0x8007BE50` in `funcs_19.c`,
still locates `0x80072E40` in `funcs_18.c`, and still
locates `0x8006F378` in `funcs_17.c`. The ROM word
`0x0C000726` matches `0x80082430` and `0x80082D5C`. A
scan that missed `0x80082430` would have been invalid.
ROM and the generated listing agree on the free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_20.c`, `0x80082D5C` | word at `0xC` of `array + ($s1 << 4)` | delay `addiu $s1, $s1, 1` does not write `$a0` | sole free of that record's `rs_malloc` block, once per index |

`$v0` at the load is not an incoming argument. `$a0` on
entry is a 1-based slot id. `$s3 = $a0 - 1` at
`0x80082D04`. The slot byte offset is `($s3 * 5) << 2`
(`sll` / `addu` / `sll` at `0x80082D0C`–`0x80082D14`),
which is `$s3 * 0x14`. `$s1` is set to 0 by
`addu $s1, $zero, $zero` at `0x80082D38`, the delay of
the count check, on the path that enters the loop. The
only later write of `$s1` before the back-edge is the
jal delay, which increments it after `$a0` has been
loaded.

The slot table is `D_8013A990` (`lui $at, 0x8014`, then
the negative offsets below). `resetModelAnimSlotTable`
walks 32 slots (`sltiu` bound `0x20`).

| Slot offset | Address for slot 0 | Role |
|---|---|---|
| `+0x00` (`-0x5670`) | `0x8013A990` | flattened-tree pointer; freed later at `0x80082DC0` |
| `+0x04` (`-0x566C`) | `0x8013A994` | halfword size factor, not a pointer |
| `+0x08` (`-0x5668`) | `0x8013A998` | anim header; word 0 is the channel count |
| `+0x0C` (`-0x5664`) | `0x8013A99C` | channel-array base |
| `+0x10` (`-0x5660`) | `0x8013A9A0` | occupied byte |
| `+0x11` (`-0x565F`) | `0x8013A9A1` | gates the `+0x00` free |

The loop loads the array from slot `+0x0C`
(`lw $v1, -0x5664($at)` at `0x80082D4C`), adds
`$s1 << 4`, and loads `0xC` of that record. The back-edge
`bne` at `0x80082D78` repeats while `$s1` is below the
word at `0` of slot `+0x08`. `$s1` strictly increases.
Each index is freed once per call.

## What the word is

`allocateModelAnimSlot` (`0x800828D0`) is the only
publisher of this array. Its only caller is
`flattenAnimTreeAndAllocateSlot` at `0x80082B7C` (one
ROM hit of jal word `0x0C020A34`). The raw pointer
`0x800828D0` occurs zero times.

For a free slot it stores:

- `$a0` at slot `+0x00` (`0x80082944`).
- `$a2` at slot `+0x04` (`0x80082950`). From the only
  caller this is the halfword at `0xE` of `*($a1 + 4)`.
- `$a1` at slot `+0x08` (`0x8008295C`).
- `rs_malloc(*($a1) << 4, 0)` at slot `+0x0C`
  (`jal` `0x80082968`, delay `sll $a0, $a0, 4` at
  `0x8008296C`, flags set by `addu $a1, $zero, $zero`
  at `0x80082964`, store at `0x80082984`).

It then loops `i` from 0 while `i < *($a1)`. For each
index it builds the same `array + (i << 4)` address and:

- stores 0 at record `+0x00` (`0x800829D0`);
- stores `1.0` (`0x3F800000` at `0x8003DB18`) at
  record `+0x04` (`0x800829E4`);
- stores 0 at record byte `+0x08` in the malloc delay
  (`0x80082A04`);
- calls `rs_malloc($a2 << 3, 0)` (`0x800829F4`,
  `0x800829F8`, jal `0x80082A00`);
- stores that return at record `+0x0C` (`sw $v0, 0xC($v1)`
  at `0x80082A18`, ROM `0xAC62000C`).

`$s0` at that store is still `i << 4`. `$v0` is still
the malloc return: the delay `sb` uses the channel
pointer computed before the jal, and the instructions
before the `sw` only rebuild the channel address into
`$v1`. The next two instructions reload record `+0x0C`
and write 0 to words 0 and 4 of that block
(`0x80082A30`, `0x80082A48`). A NULL malloc faults on
that store inside `allocateModelAnimSlot`, before a
slot is published. `rs_free` still skips `$a0 == 0`
(`beq` at `0x80001CA4`). That edge does not reach this
jal from a completed allocate. Same unproven
allocator-failure edge as s3604–s4486.

## No other writer of record `+0x0C`

Every `lui $at, 0x8014` access of slot `+0x0C` in the
main image is in `findModelAnimKeyframeByPhase`,
`allocateModelAnimSlot`, `releaseModelAnimSlot`,
`markModelAnimChannelEntryActive`,
`clearModelAnimChannelEntry`,
`seekModelAnimChannelToTime`,
`seekAllModelAnimChannelsInSlotToTime`,
`setModelAnimChannelEntryDuration`,
`getModelAnimChannelEntryDuration`,
`setModelAnimSlotCycleDuration`,
`sampleModelAnimKeyframeVec3`, and
`parseModelAnimType2Entry`. The `0x8004E*` `lwc1`
hits of the same immediate use `lui $at, 0x8004` and
are a float pool, not this table.

The only store whose base is `array + (index << 4)` and
whose offset is `0xC` is `0x80082A18`. The other
offset-`0xC` store in this range is `swc1 $f2, 0xC($s2)`
at `0x80083AD4`. `$s2` there is `lw $s2, 0($v1)` at
`0x800835F8`, and `$v1` was rebuilt from slot `+0x00`
(the flattened tree) plus `$s5 << 2`. That store writes
a tree node. It also writes offsets `0x10`, `0x14`, and
`0x24`, which do not fit in a `0x10`-byte channel
record.

Readers of the channel word do not replace it and do
not free it:

- `findModelAnimKeyframeByPhase` reloads it
  (`0x80082780` and three later copies) and writes
  words inside the malloc block. Its `+0xC` base is
  `array + ($a1 << 4)` (`sll $a2, $a1, 4` at
  `0x800826D8`). The `swc1` at `0x80082860` writes
  channel `+0x00`, not `+0x0C`. The function has no
  `jal`.
- `parseModelAnimType2Entry` reloads it
  (`lw $a1, 0xC($v1)` at `0x800835C0`; `$s7` starts at
  0 and steps by `0x10` at `0x80083BC8`) and reads
  floats through `a2 +` that pointer. Its `jal`s
  (`0x8001D850`, `0x8001D548`) pass `$s0` and stack
  addresses, not this pointer.
- `setModelAnimSlotCycleDuration`'s `lw $a0, -0x5664`
  at `0x800832DC` is the array base. The loop stores a
  float at channel `+0x04` only.
- `model_animation_offset_convert`'s `sw` at
  `0x80082C5C` relocates a file-internal offset. It
  runs on the anim file, not on the heap array this
  malloc creates afterwards.

No function that loads the channel word contains
`jal rs_free` except this loop. The count word at
`*(slot+0x08)` is read, not stored, by those functions
(`find` and `sampleModelAnimKeyframeVec3` read header
`+4` instead). `model_animation_offset_convert` does
not store offset 0 of its file. This subsystem does not
change the count between the per-channel mallocs and
this free.

## The later jal does not free this pointer

`0x80082D98` loads slot `+0x0C` itself
(`lw $a0, -0x5664($at)` at `0x80082D94`, ROM
`0x8C24A99C`) and frees that word. That is the array
from `rs_malloc(count << 4, 0)`, not record `+0x0C`.
The array is still live when the per-channel mallocs
run, so the two returns are different blocks. The
element free runs first. `0x80082DC0` frees slot
`+0x00` when byte `+0x11` is nonzero. That is the
flattened tree, a third block. Neither is classified
here.

## Callers

Seven ROM hits of jal word `0x0C020B3F`. The raw
pointer `0x80082CFC` occurs zero times. Each passes a
saved slot id, not the channel pointer.

| Caller | PC | Argument |
|---|---|---|
| `tickAtAtAudioAndWeaponState` | `0x800CC9DC` | `0x78($s0)`, stored from `flattenAnimTreeAndAllocateSlot`'s return at `0x800CCAA4` |
| `npcAtAtUpdate` | `0x800CDE64` | `0x78($s1)`, stored at `0x800CDD80`; that alloc path `j`s to the epilogue and does not fall into this free |
| `npcAtStHandleDestruction` | `0x800CF8F4` | `0x8C($s1)` |
| `advanceAtStDeathAnimPhase` | `0x800CFD2C` | `0x8C($s0)`, stored at `0x800CFE44` |
| `npcAtStUpdate` | `0x800D0450` | `0x8C($s2)`, stored at `0x800D03AC` |
| `npcAtPtPlaySkywalkerErrorCallout` | `0x800EA490` | `0x94($s0)`, stored at `0x800EA5A8` |
| `npcAtPtUpdate` | `0x800EAAD8` | `0x94($s1)`, stored at `0x800EAA44` |

`playerAtStUpdate` stores a slot id at `0x80($s2)`
(`0x800D24D8`) and an unnamed caller at `0x80139B38`
stores one at `0x58`. Neither address is a release
argument. That is a leak of the same class of block,
not a second free at this jal.

`releaseModelAnimSlot` does not range-check `$a0`.
`clearModelAnimChannelEntry` does (`0 < high_half < 0x21`).
An id of 0 computes a count pointer at `0x8013A984`,
in the gap between `gNewButtonsPressed` (`0x8013A960`)
and `D_8013A990`. No main-segment store uses that
address (`lui $at, 0x8014` never pairs with immediate
`0xA984`). The word stays the BSS zero, so the next
`lw` reads address 0 and is not a load of a channel
record. That path is not a second identity of the word
this jal frees for a published slot. Runtime contents
of address 0 were not read. No guard was added: the
published channel word's only writer is the allocator
return, and it is legitimate.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at
static scope: the only store of record `+0x0C` is the
`rs_malloc($a2 << 3, 0)` return, no callee frees that
pointer before this jal, and the loop frees each index
once. H-NextClassUnevaluable is not selected. The later
jal frees the array, not this pointer. Runtime
allocator legitimacy remains unproven. No guard was
added.

The next unaudited `jal rs_free` in address order is
still in `releaseModelAnimSlot`, at `0x80082D98`
(`lw $a0, -0x5664($at)`, delay `nop`). That frees the
channel array from `rs_malloc(count << 4, 0)` at
`0x80082968`. `0x80082DC0` remains a separate site
after it.
