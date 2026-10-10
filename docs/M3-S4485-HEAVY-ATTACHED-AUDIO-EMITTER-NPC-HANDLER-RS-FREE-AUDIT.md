# M3 s4485 — heavyAttachedAudioEmitterNpcHandler rs_free of the emitter vertex buffer

## Work unit

Static census of the one original `jal rs_free` in
`heavyAttachedAudioEmitterNpcHandler` (`0x8007BC18`, size
`0x650`), at `0x8007BE50`. The instruction before the jal
is `lw $a0, 0x38($s2)` at `0x8007BE4C`. The delay slot is
`nop` at `0x8007BE54`. It does not write `$a0`. No build
or runtime run was performed. `npcShieldUpdate` (s4484)
was not re-audited.

The discriminator was every original assignment of `$s2`
from the prologue through the free, every store that can
produce the word at `0x38($s2)`, every callee `jal rs_free`,
and every caller argument:

- H-NextClassGap: that word can be a non-allocator value,
  or a pointer a sibling already freed, with the writer
  named.
- H-NextClassComplete: that word is the matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates closed `0x8007A814`, closed `0x8007B23C`,
and this site in `funcs_19.c`, still locates `0x80072E40`
in `funcs_18.c`, and still locates `0x8006F378` in
`funcs_17.c`. The ROM word `0x0C000726` matches `0x8007B23C`
and `0x8007BE50`. A scan that missed `0x8007A814` or
`0x8007B23C` would have been invalid. ROM and the generated
listing agree on the free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_19.c`, `0x8007BE50` | word at `0x38($s2)` | `lw $a0, 0x38($s2)` at `0x8007BE4C`; delay `nop` | sole free of that word; the `rs_malloc` vertex buffer |

`$s2` is assigned three times in the function. Only the
prologue load reaches the free.

| PC | Instruction | Reaches `0x8007BE4C`? |
|---|---|---|
| `0x8007BC48` | `lw $s2, 0x4($s3)` | yes, on every entry |
| `0x8007BC7C` | `addu $s2, $v0, $zero` | no; mode 1 only |
| `0x8007C24C` | `lw $s2, 0x1A0($sp)` | no; epilogue, after the free |

`$s3` is the incoming NPC (`addu $s3, $a0` at
`0x8007BC20`). `sw $s2, 0x1A0($sp)` at `0x8007BC38` saves
the incoming register and does not assign it. Mode 5's
`addu $s3, $a2` at `0x8007BF88` replaces `$s3` after the
free's address and does not run on the mode-2 path.

## Mode dispatch

`a1` is masked to 16 bits, then decremented. Values
outside 1..5 branch to the epilogue at `0x8007BC4C` and
do not free. The other five values `jr` through the table
at `0x8003D5D8`:

| `a1` | Target | Role |
|---|---|---|
| 1 | `0x8007BC6C` | allocate the emitter object |
| 2 | `0x8007BE4C` | this free |
| 3 | `0x8007BE6C` | update |
| 4 | `0x8007BEE0` | update |
| 5 | `0x8007BF88` | update |

No PC-relative branch targets `0x8007BE4C`. Mode 1's
exit is the unconditional `j 0x8007C240` at `0x8007BE44`.
Its delay slot is `nop`. It does not fall into the `lw`.
The generated listing has the same `goto` before
`L_8007BE4C`. Mode 1's `addu $s2, $v0` is therefore not
a value that reaches this jal. At the free, `$s2` is the
word mode 1 published at NPC+4.

## What is allocated, and who writes the word

Mode 1 calls `rs_malloc` at `0x8007BC74` with size
`0x180` and flags 0 (`addiu $a0, $zero, 0x180` at
`0x8007BC6C`, `addu $a1, $zero` at `0x8007BC70`). The
delay slot `addu $s1, $a2` does not write `$a0`. The
return is stored to NPC+4 at `0x8007BC8C`. That `0x180`
block is not the pointer this jal frees.

The copy that follows writes `$s2+8` through `$s2+0x34`
(source `$a2`, end `$a2+0x30`, 16 bytes per step). It
does not write `$s2+0x38`.

`addiu $a0, $s2, 0x38` at `0x8007BCE0` is the delay of
`jal allocateNpcMeshVertexBuffer` at `0x8007BCDC`. `$a1`
is `lw $a1, 0($s2)` at `0x8007BCD8`, the mesh pointer
just stored from `walkMeshdef0List`. Inside that callee:

- `$s2` is `$a0` (`addu $s2, $a0` at `0x8007A88C`).
- `addu $a1, $zero` at `0x8007A8A0` sets flags 0. No
  instruction before the jal writes `$a1` again.
- The size in the delay slot `sll $a0, $a0, 2` at
  `0x8007A8B8` is `(word at 0x14 of (mesh+0x1C)->8, plus
  4 times the word at 0xC of that object's +0x20) << 2`.
- `sw $t0, 0($s2)` at `0x8007A8C0` stores the
  `rs_malloc` return at emitter+0x38. `$t0` is `$v0`.
  Nothing else in the callee stores to `0($s2)`.

The generated listing has that same `sw` through the
field pointer. The callee's later `sh $zero, 0x28($a0)`
loop steps back by `0x3C` from field+`0xB4` and writes
halfwords at field+`0xDC`, `+0xA0`, `+0x64`, and `+0x28`.
It does not write field+0. The callee contains
`jal rs_malloc` and no `jal rs_free`.

The only other call of `allocateNpcMeshVertexBuffer` is
`0x8007AFF0`, in `npcShieldUpdate`, with `$a0` equal to
that function's own shield+0x38. It does not write this
emitter field.

## Stores that do not hit the word

The function's only store with immediate `0x38` is
`swc1 $f2, 0x38($s1)` at `0x8007C1A0`. It is in mode 5.
The record scan sets `$a2 = $s2+0x38` at `0x8007C054`
and, when a record's halfword at `+0x28` is zero, jumps
to `addiu $v0, $a0, 8` / `addu $s1, $a2, $v0` at
`0x8007BFE8`. `$a0` is `0`, `0x3C`, `0x78`, or `0xB4`.
The float store therefore lands at `$s2+0x78`,
`$s2+0xB4`, `$s2+0xF0`, or `$s2+0x12C`, never at
`$s2+0x38`. The scan fall-through zeroes `$s1` and the
next instruction branches away on that zero, so those
stores are not reached with `$s1 == 0`. The inner jump
table at `0x8003D5F0` targets `0x8007BFCC` and
`0x8007BFD8` only. Both jump to `0x8007BFF8` and do not
enter the `$s1` setup.

Mode 3 calls `npcDeformingMeshUpdate` (`0x8007AD30`)
with `$a0 = $s2+0x38` at `0x8007BED0`. It sets
`$s0 = $a0+0x28` and does not store to `0($a0)`. It has
no `jal rs_free`. Its stores through `$s2` in the caller
are at `+0x2C`, `+0x30`, and `+0x34`.

Mode 4 calls `transformMeshVerticesForNpc` (`0x8007A9C8`)
with `$a0 = $s2+0x38` at `0x8007BF40`. It copies `$a0`
to `$t5`, loads the buffer pointer from `0($t5)`, and
never stores through `$t5`. `sw $v1, 0($v0)` at
`0x8007ACD0` writes a word loaded from the buffer.
`sw $v0, 0xC($a0)` at `0x8007AD14` uses `$a0` reloaded
from `4($t5)`, which is field+4, not field+0. It has no
`jal rs_free`.

Every other direct callee was scanned at its symbol
size. The only one that contains `jal rs_free` is
`releaseMeshAsset`.

## One free of this pointer

This function contains one `jal rs_free`. It is not in a
loop. Mode 2's first instruction is the `lw`; no callee
runs before it. After the free, mode 2 does
`lw $a0, 0($s2)` and `jal releaseMeshAsset`. That `$a0`
is the mesh pointer stored at object+0 by
`walkMeshdef0List`, not emitter+0x38.
`releaseMeshAsset` assigns `$s5` from its `$a0` only.
Its `jal rs_free` at `0x8005794C` has delay
`addu $a0, $s5`, so it frees that mesh. Mode 2 then
jumps to `0x8007C240` and does not execute the mode-5
`jal destroyNpcSlotByIndex` at `0x8007C238`.

`destroyNpcSlotByIndex` is what enters mode 2, and only
when byte NPC+0x1A is 0. It then calls
`reinsertNpcIntoSortedFreeList` with the NPC pointer.
This handler is registered with `$a2 = 4`, and
`spawnNpcOfType` stores that halfword at NPC+0x14, so
bit 2 is set. On that bit, reinsert does `lw $a0, 4($a0)`
and `jal rs_free` on the `0x180` emitter object. That is
the parent block, after the vertex buffer has already
been freed. The bit-2 path jumps to the epilogue and
does not execute `sw $zero, 4($a0)`.

## Callers

The ROM has no `jal 0x8007BC18` encoding and no data
word `0x8007BC18`. The only `lui`/`addiu` or `lui`/`ori`
materialization in `0x80000400..0x80100000` is
`0x8007D798` in `spawnNamedTexturedEmitterNpc`, passed
to `spawnNpcOfType` with `$a2 = 4`. Spawn zeroes NPC+4,
stores the handler at NPC+0, then calls
`slotDispatcherIter` with `$a1 = 1`. The same function
then calls `slotDispatcherIter` with `$a1 = 3` on the
returned index. Two earlier dispatcher calls in that
function install `npcVortexUpdate` (`0x80081ABC`), not
this handler.

Of 144 `jal slotDispatcherIter` sites, the nearest `$a1`
immediate is never 2. The modes are 1, 3, 4, 5, 6, 8,
9, 0xA, 0xB, 0xC, 0xE, 0xF, and 0x1000. The dispatcher
passes that `$a1` through (`andi $a1, $s7, 0xFFFF`
before `jalr` of NPC+0). The only `jalr` reached from
`addiu $a1, $zero, 2` is `destroyNpcSlotByIndex` at
`0x8003EDDC`, and only when byte NPC+0x1A is 0. Update
dispatch does not enter mode 2.

`rs_free` branches away when `$a0 == 0` (`beq $s0, $zero`
at `0x80001CA4`). A NULL vertex-buffer malloc is stored
by the same `sw` and is the same unproven
allocator-failure edge left open by s3604–s4484, not a
second pointer identity. A destroy before mode 1 loads
`$s2` from the zero spawn wrote at NPC+4 and faults on
the `lw` before `rs_free`. A NULL `0x180` malloc is the
same fault, not a second identity that reaches the jal.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static
scope: the only value stored at emitter+0x38 is the
`rs_malloc` return written at `0x8007A8C0`, no callee
frees that pointer before this jal, and mode 2 is the
destroy entry rather than an update mode.
H-NextClassUnevaluable is not selected. The `0x180`
parent free in reinsert, and the mesh free in
`releaseMeshAsset`, are different blocks and are not
this jal. Runtime allocator legitimacy remains unproven.
No guard was added.

A second `destroyNpcSlotByIndex` of the same index is
not skipped: the refcount byte is written back to 0,
and the bit-2 reinsert path does not clear NPC+4. That
would re-enter this same jal. It is not a second
pointer identity and not a sibling free.
`spawnNamedTexturedEmitterNpc` does not call
`destroyNpcSlotByIndex`. Mode 5 can destroy the index
in halfword `0($a2)`, but mode 2 jumps over that jal,
and no `slotDispatcherIter` site passes `$a1 = 5` for
the index this installer just returned. No caller in
this census destroys one index twice.

The next unaudited site in address order is
`applyCheatCodeFromInput` at `0x80082430` (entry
`0x80082270`, size `0x248`, `funcs_20.c`). The delay
slot `addu $a0, $s5` at `0x80082434` does write `$a0`,
so the freed value is `$s5`. A first scan, not a
classification: the only `$s5` assignment before the
free is `addu $s5, $v0` at `0x800822AC`, after
`jal make_crc32_lut` (`0x80082544`) at `0x800822A4`.
The delay of that jal is `sw $s1, 0x14($sp)` and does
not write `$s5`. `sw $s5, 0x24($sp)` at `0x800822A0`
saves the incoming register. `bne` at `0x80082428`
skips the free. `j 0x80082430` at `0x80082418` also
reaches it; its delay `sw` does not write `$a0` or
`$s5`.
