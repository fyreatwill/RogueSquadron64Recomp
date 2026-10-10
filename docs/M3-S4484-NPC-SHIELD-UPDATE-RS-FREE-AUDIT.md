# M3 s4484 — npcShieldUpdate rs_free of the shield vertex buffer

## Work unit

Static census of the one original `jal rs_free` in
`npcShieldUpdate` (`0x8007AEF8`, size `0xD20`), at
`0x8007B23C`. The instruction before the jal is
`lw $a0, 0x38($s3)` at `0x8007B238`. The delay slot is
`nop` at `0x8007B240`. It does not write `$a0`. No build
or runtime run was performed. `downscaleImageHalfResBoxFilter`
(s4483) was not re-audited.

The discriminator was every original assignment of `$s3`
from the prologue through the free, every store that can
produce the word at `0x38($s3)`, every callee `jal rs_free`,
and every caller argument:

- H-NextClassGap: that word can be a non-allocator value,
  or a pointer a sibling already freed, with the writer
  named.
- H-NextClassComplete: that word is the matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates closed `0x8007A814` and this site in
`funcs_19.c` (and the later site `0x8007BE50`), still
locates `0x80072B8C` and `0x80072E40` in `funcs_18.c`, and
still locates `0x8006DA28` and `0x8006F378` in `funcs_17.c`.
The ROM word `0x0C000726` matches `0x8007A814` and
`0x8007B23C`. A scan that missed `0x8007A814` would have
been invalid. ROM and the generated listing agree on the
free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_19.c`, `0x8007B23C` | word at `0x38($s3)` | `lw $a0, 0x38($s3)` at `0x8007B238`; delay `nop` | sole free of that word; the `rs_malloc` vertex buffer |

`$s3` is assigned twice before the free's address, and
only one of those assignments reaches the free.

| PC | Instruction | Reaches `0x8007B238`? |
|---|---|---|
| `0x8007AF2C` | `lw $s3, 4($s4)` | yes, on every entry |
| `0x8007AF70` | `addu $s3, $v0, $zero` | no; mode 1 only |
| `0x8007BBF8` | `lw $s3, 0xA4($sp)` | no; epilogue, after the free |

`$s4` is the incoming NPC (`addu $s4, $a0` at
`0x8007AF00`). `sw $s3, 0xA4($sp)` at `0x8007AF18` saves
the incoming register and does not assign it.

## Mode dispatch

`a1` is masked to 16 bits, then decremented. Values
outside 1..5 branch to the epilogue at `0x8007AF30` and
do not free. The other five values `jr` through the table
at `0x8003D520`:

| `a1` | Target | Role |
|---|---|---|
| 1 | `0x8007AF60` | allocate the shield object |
| 2 | `0x8007B238` | this free |
| 3 | `0x8007B27C` | update |
| 4 | `0x8007B8CC` | update |
| 5 | `0x8007B930` | update |

No branch instruction in the function targets
`0x8007B238`. Mode 1's exit is the unconditional
`j 0x8007BBF0` at `0x8007B230`. Its delay slot
`addiu $v0, $zero, 1` sets the return value and does not
fall into the `lw`. The generated listing has the same
`goto` before `L_8007B238`. Mode 1's `addu $s3, $v0` is
therefore not a value that reaches this jal. At the free,
`$s3` is the word mode 1 published at NPC+4.

## What is allocated, and who writes the word

Mode 1 calls `rs_malloc` at `0x8007AF68` with size
`0x180` and flags 0 (`addiu $a0, $zero, 0x180` at
`0x8007AF64`, `addu $a1, $zero` in the delay slot). The
return is stored to NPC+4 at `0x8007AF78`. That `0x180`
block is not the pointer this jal frees.

`addiu $s0, $s3, 0x38` at `0x8007AFE0` is the only
derivation of that field address on the create path.
`allocateNpcMeshVertexBuffer` is called at `0x8007AFF0`
with `$a0` equal to it and `$a1` equal to the mesh
pointer at `0($s3)`. Inside that callee:

- `$s2` is `$a0` (`addu $s2, $a0` at `0x8007A88C`).
- `addu $a1, $zero` at `0x8007A8A0` sets flags 0. No
  instruction before the jal writes `$a1` again.
- The size in the delay slot `sll $a0, $a0, 2` at
  `0x8007A8B8` is `(word at 0x14 of (mesh+0x1C)->8, plus
  4 times the word at 0xC of that object's +0x20) << 2`.
- `sw $t0, 0($s2)` at `0x8007A8C0` stores the
  `rs_malloc` return at shield+0x38. `$t0` is `$v0`.

The generated listing has that same `sw` through `r18`.
The callee's later `sh $zero, 0x28($a0)` loop steps back
by `0x3C` from `$s2+0xB4` and writes halfwords at
`$s2+0xDC`, `+0xA0`, `+0x64`, and `+0x28`. It does not
write `$s2+0`. The callee contains `jal rs_malloc` and
no `jal rs_free`.

The only other call of `allocateNpcMeshVertexBuffer` is
`0x8007BCDC`, in `heavyAttachedAudioEmitterNpcHandler`,
with `$a0 = $s2+0x38` of that function's own object. It
does not write this shield field.

## Stores that do not hit the word

The function's only stores with immediate `0x38` are
`swc1` through `$s1`, at `0x8007B168`, `0x8007B4D4`,
`0x8007B788`, `0x8007B7A8`, and `0x8007BB4C`. There is
no `sw`/`sh`/`sb` with immediate `0x38` and base `$s3`.

On the update paths the record scan sets `$s0 = $s3+0x38`
and, when a record's halfword at `+0x28` is zero, jumps
to `addiu $v0, $a0, 8` / `addu $s1, $s0, $v0`. `$a0` is
`0`, `0x3C`, `0x78`, or `0xB4`. The float store at
`0x38($s1)` therefore lands at `$s3+0x70+$a0`, never at
`$s3+0x38`. The scan fall-through zeroes `$s1` and the
next instruction branches away on that zero, so those
stores are not reached with `$s1 == 0`.

`npcDeformingMeshUpdate` (`0x8007AD30`) is called with
`$a0 = $s3+0x38` at `0x8007B8BC`. It sets `$s0 = $a0+0x28`
and does not store to `0($a0)`. It has no `jal rs_free`.
`transformMeshVerticesForNpc` (`0x8007A9C8`) is called
the same way at `0x8007B8E8`. It copies `$a0` to `$t5`,
loads the buffer pointer from `0($t5)`, and never stores
through `$t5`. Its `sw $v1, 0($v0)` writes a word loaded
from the buffer, not the field. It has no `jal rs_free`.

## One free of this pointer

This function contains one `jal rs_free`. It is not in a
loop. Mode 2's first instruction is the `lw`; no callee
runs before it. After the free, mode 2 calls
`parseDatItemCommon` (no `jal rs_free`) and
`releaseMeshAsset`. `releaseMeshAsset` assigns `$s5`
from its `$a0` only, and that `$a0` is `0($s3)`, the
mesh pointer, not shield+0x38. Its `jal rs_free` at
`0x8005794C` frees `$s5`.

`destroyNpcSlotByIndex` then calls
`reinsertNpcIntoSortedFreeList` with the NPC pointer.
Shields are registered with `$a2 = 4`, and
`spawnNpcOfType` stores that halfword at NPC+0x14, so
bit 2 is set. On that bit, reinsert does `lw $a0, 4($a0)`
and `jal rs_free` on the `0x180` shield object. That is
the parent block, after the vertex buffer has already
been freed. It is not a second free of the word at
`+0x38`. The bit-2 path jumps to the epilogue and does
not execute `sw $zero, 4($a0)`.

## Callers

The ROM has no `jal 0x8007AEF8` encoding and no data
word `0x8007AEF8`. The only address materialization is
`lui`/`addiu` at `0x800655A0` in `setupNpcUpdateFunctions`,
passed to `spawnNpcOfType` with `$a2 = 4` and `$a3 = 0x64`.
Spawn zeroes NPC+4, stores the handler at NPC+0, then
calls `slotDispatcherIter` with `$a1 = 1`.

Of 144 `jal slotDispatcherIter` sites, the nearest `$a1`
immediate is never 2. The modes are 1, 3, 4, 5, 6, 8,
9, 0xA, 0xB, 0xC, 0xE, 0xF, and 0x1000. The only `jalr`
reached from `addiu $a1, $zero, 2` is
`destroyNpcSlotByIndex` at `0x8003EDDC`, and only when
byte NPC+0x1A is 0. That call passes the NPC in `$a0`
and 0 in `$a2`. Update dispatch does not enter mode 2.

`rs_free` branches away when `$a0 == 0` (`beq $s0, $zero`
at `0x80001CA4`). A NULL vertex-buffer malloc is stored
by the same `sw` and is the same unproven
allocator-failure edge left open by s3604–s4483, not a
second pointer identity. A destroy before mode 1 loads
`$s3` from the zero spawn wrote at NPC+4 and faults on
the `lw` before `rs_free`.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static
scope: the only value stored at shield+0x38 is the
`rs_malloc` return written at `0x8007A8C0`, no callee
frees that pointer, and mode 2 is the destroy entry
rather than an update mode. H-NextClassUnevaluable is
not selected. The `0x180` parent free in reinsert is a
different block and is not this jal. Runtime allocator
legitimacy remains unproven. No guard was added.

A second `destroyNpcSlotByIndex` of the same index is
not skipped: the refcount byte is written back to 0,
and the bit-2 reinsert path does not clear NPC+4. That
would re-enter this same jal. It is not a second
pointer identity and not a sibling free. No caller in
this census destroys one index twice.

The next unaudited site in address order is
`heavyAttachedAudioEmitterNpcHandler` at `0x8007BE50`
(entry `0x8007BC18`, size `0x650`, `funcs_19.c`). `$a0`
is `lw $a0, 0x38($s2)` at `0x8007BE4C`. The delay slot
is `nop`. `j 0x8007C240` at `0x8007BE44` skips the free.
A first scan, not a classification: `$s2` is loaded
from `4($s3)` at `0x8007BC48` and then replaced by
`addu $s2, $v0` at `0x8007BC7C`. The jal between those
is `rs_malloc` at `0x8007BC74`. `addiu $a0, $zero, 0x180`
at `0x8007BC6C` and `addu $a1, $zero` at `0x8007BC70`
set size and flags before that jal. The delay slot
`addu $s1, $a2` does not write `$a0`. `addiu $a0, $s2,
0x38` at `0x8007BCE0` is the delay of the other
`allocateNpcMeshVertexBuffer` call.
