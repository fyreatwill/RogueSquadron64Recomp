# M3 s4491 — handleHUD rs_free of the radar block

## Work unit

Static census of `handleHUD` (`.ovl.mission`, entry `0x800C0084`,
size `0x1AE0`) at its only `jal rs_free`, `0x800C1084`. The
generated name in `funcs_33.c` is `initHudStruct`. Mission ROM
bytes were used. Menu VRAM `0x800C1084` is `addiu $a0, $zero, 0x8`
in another function; that word is not this jal. No build or
runtime run was performed. `audioSeqFree` and the s3602–s3607
destructor and speech frees were not re-audited.

The discriminator was every original assignment of `$s2` and of
the word at body `+0x230` from the prologue through the free,
every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value,
  or a pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator
  return, freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can
  reach `$a0`, or a possible indirect entry cannot be accepted
  or rejected.

Same-scan positive control: `funcs_20.c` still has
`jal 0x80001C98` at closed `0x80082DC0` and closed `0x80083C58`.
`funcs_19.c` still has it at closed `0x8007BE50`. `funcs_33.c`
has it at `0x800C1084`. The ROM word at all four PCs is
`0x0C000726`. A scan that missed `0x80083C58` or `0x8007BE50`
would have been invalid.

## What is freed

The function is a jump table on `(a1 - 1)` when that value is
below 12, otherwise the epilogue. The table at `0x800A6458` is
referenced only by the `lui`/`addiu` pair at `0x800C00DC`. Slot 1
(`a1 == 2`) is `0x800C1074`. That arm is straight-line:

```
lw   $a0, 0x250($s2)
jal  releaseMeshAsset     # 0x8005779C
nop
lw   $a0, 0x230($s2)      # 0x800C1080
jal  rs_free              # 0x800C1084
nop                       # delay does not write $a0
j    0x800C1B20
```

`$s2` on this arm is the prologue `lw $s2, 4($a0)` at
`0x800C00C4`. The only other `$s2` write before the epilogue
restore is mode 1 (`a1 == 1`): `rs_malloc(0xF80, 0)` at
`0x800C00FC`, then `sw $s2, 4($t0)` at `0x800C0110` (`$t0` is the
saved NPC pointer). That is the body. It is not the word freed
here.

Inside this function the only store of offset `0x230` is
`sw $v0, 0x230($s2)` at `0x800C05C8`, on the mode-1 arm. `$v0`
there is the return of `initializeRadar` (`jal 0x800C44D0` at
`0x800C05A8`). The delay of that jal stores the old `$v0` at
`+0x1D0`. Between the return and `0x800C05C8` nothing writes
`$v0` (`mfc1` writes `$a1`).

`initializeRadar` (`0x800C44D0`, size `0x8BC`) does
`addiu $a0, $zero, 0xDD4` and `jal rs_malloc` at `0x800C451C`
with `$a1 = 0`. Nothing between the `addiu` and the jal writes
`$a0`. It copies `$v0` to `$s2`, stores that pointer at
`0x8010BFE0`, and returns it with `addu $v0, $s2, $zero` at
`0x800C4D2C`. The epilogue restores `$s2` after that copy and
does not change `$v0`. The only `jal rs_free` among its twelve
direct callees is inside `loadAndRelocateAsset` (`0x800554D8`),
called with `$a0 = 0x800A673C`, not the radar block. That free
is of `loadAndRelocateAsset`'s own pointer (s3626). Caller `$s2`
is callee-saved and is not passed in.

The other three loads of `0x230($s2)` in this function are not
frees. `0x800C6468` only adds a float at `+0xDCC` and returns.
`0x800C5F90` and `0x800C6498` contain no `jal rs_free` before
`jr $ra`. `releaseMeshAsset` is called with `+0x250`, a
different word (s3631).

Immediate `0xBFE0` occurs twice in the CPU sections: the store
of the malloc at `0x800C4530`, and `lw $s1, -0x4020($v0)` at
`0x800C63CC`. That reader writes radar fields and returns. It
does not `jal rs_free`.

`rs_free` skips a NULL argument. A failed `rs_malloc(0xDD4)`
faults inside `initializeRadar` (`sh` through `$s2`) before the
pointer is stored, so the stored word is not a failed malloc.

## Who reaches mode 2

No `jal` or `j` encodes `0x800C0084`. The only materialization
of the entry is `spawnHudNpc` (`0x800C3F70`): `lui $a0, 0x800C`
/ `addiu $a0, $a0, 0x84`, then `jal spawnNpcOfType` with
`$a1 = 0`, `$a2 = 4`, `$a3 = 0x64`. Spawn zeros NPC `+0x4` and
byte `+0x1A`, stores flags `4` at `+0x14`, and calls the handler
once with mode 1. The returned slot index is stored at
`0x8010BFD0`.

Immediate `0xBFD0` occurs three times, all in `.ovl.mission`:
that store, `lhu $a0, -0x4030` at `0x800C3FF8` (`a1 = 12`,
`jal slotDispatcherIter`), and the same load at `0x800C4048`
(`a1 = 5`). Mode 12 (`0x800C1024`) and mode 5 (`0x800C1050`)
jump to the epilogue without `jal rs_free`.

Mode 2 is `destroyNpcSlotByIndex` (`0x8003ED74`). If the slot's
NPC is NULL it returns. If byte `+0x1A` is nonzero it ors flag
bit 3 and returns without `jalr`. If the byte is 0 it increments
the byte, `jalr`s the handler with `$a1 = 2`, then decrements
the byte. A nested destroy sees the byte nonzero and does not
enter mode 2 again.

Flag bit 2 is set (spawn passed `4`). `reinsertNpcIntoSortedFreeList`
then `jal rs_free`s NPC `+0x4`, the `0xF80` body, and does not
clear `+0x4` (s3647). That is a different block from `+0x230`,
and it runs after this free. `allocateNpcSlot` records the
returned index as child 0 of the new NPC. `popNpcSlotFromTail(0, npc)`
links a second slot whose `+0` is the same NPC. Destroy's child
loop unlinks those indices from the slot chain. The next
`destroyTransientNpcSlots` walk (the loop in
`destroyNpcContextArrays`) therefore does not select this NPC
again.

## Verdict

H-NextClassComplete. Body `+0x230` is `initializeRadar`'s
`rs_malloc(0xDD4, 0)` return, stored once, freed once on mode 2.
The mode-1 body (`0xF80`) and the mesh at `+0x250` are different
blocks. No guard was added.

H-NextClassGap is refuted at static scope: no store of this
word except that malloc return, and no second `jal rs_free` of
it. H-NextClassUnevaluable is not selected. The handler entry
is only `spawnHudNpc`, and the saved index is not passed to
`destroyNpcSlotByIndex`. Runtime allocator failure remains
unproven; a NULL body would fault on `+0x230($s2)` before this
jal, which is not a second pointer.

Mission `jal rs_free` sites from `0x800CABB0` through
`0x800EAAE4` are already classified in s3617–s3620. The next
site with no M3 audit is `unlinkAndFreeChildNpcNode` at
`0x800EC404` (entry `0x800EC388`, size `0x150`). The delay is
`nop`. The instruction before the jal does not write `$a0`.
s1814 only renamed that function.
