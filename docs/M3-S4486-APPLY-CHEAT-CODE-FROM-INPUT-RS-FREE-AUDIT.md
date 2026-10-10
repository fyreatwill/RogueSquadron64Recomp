# M3 s4486 — applyCheatCodeFromInput rs_free of the CRC32 lookup table

## Work unit

Static census of the one original `jal rs_free` in
`applyCheatCodeFromInput` (`0x80082270`, size `0x248`),
at `0x80082430`. The delay slot is `addu $a0, $s5, $zero`
at `0x80082434` (ROM `0x02A02021`). It writes `$a0`, so
the freed value is `$s5`. No build or runtime run was
performed. `heavyAttachedAudioEmitterNpcHandler` (s4485)
was not re-audited.

The discriminator was every original assignment of `$s5`
from the prologue through the free, the return value of
`make_crc32_lut`, every callee `jal rs_free`, and every
caller argument:

- H-NextClassGap: `$s5` can be a non-allocator value, or
  a pointer a sibling already freed, with the writer
  named.
- H-NextClassComplete: `$s5` is a matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates this site in `funcs_20.c`, still
locates closed `0x8007A814`, closed `0x8007B23C`, and
closed `0x8007BE50` in `funcs_19.c`, still locates
`0x80072E40` in `funcs_18.c`, and still locates
`0x8006F378` in `funcs_17.c`. The ROM word `0x0C000726`
matches `0x8007BE50` and `0x80082430`. A scan that missed
`0x8007BE50` would have been invalid. ROM and the
generated listing agree on the free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_20.c`, `0x80082430` | `$s5` | delay `addu $a0, $s5, $zero` at `0x80082434` | sole free of the `make_crc32_lut` block, on every path that reaches the jal |

`$s5` is assigned twice in the function. Only the
post-call move reaches the free.

| PC | Instruction | Reaches `0x80082434`? |
|---|---|---|
| `0x800822AC` | `addu $s5, $v0, $zero` | yes, on every entry |
| `0x80082498` | `lw $s5, 0x24($sp)` | no; epilogue, after the free |

`sw $s5, 0x24($sp)` at `0x800822A0` is the only store of
`$s5`. It runs before `jal make_crc32_lut` and saves the
incoming register. The delay of that jal is
`sw $s1, 0x14($sp)` at `0x800822A8`. It does not write
`$s5`. No instruction from `0x800822B0` through the free
writes `$s5`.

## What make_crc32_lut returns

`make_crc32_lut` (`0x80082544`, size `0x7C`) is a leaf
apart from one call. ROM:

- `addiu $a0, $zero, 0x400` at `0x8008254C`.
- `jal rs_malloc` (`0x80001ACC`) at `0x80082550`.
- Delay `addu $a1, $zero, $zero` at `0x80082554` sets
  flags 0.
- `addu $t0, $v0, $zero` at `0x80082564` is the only
  write of `$t0`.
- The body fills 256 words (`sltiu` bound `0x100`, store
  stride 4) with the reflected CRC-32 recurrence,
  polynomial `0xEDB88320` (`lui $a3, 0xEDB8` /
  `ori $a3, $a3, 0x8320`).
- `addu $v0, $t0, $zero` at `0x800825B4` returns that
  `rs_malloc` pointer. The function contains no
  `jal rs_free`.

`$s5` at the free is that user pointer. `0x400` bytes is
256 table words. The pointer is never stored to memory
after `0x800822AC`, so no other function is given the
address.

The only ROM hit of `jal make_crc32_lut`
(`0x0C020951`) is `0x800822A4` in this function. The raw
pointer word `0x80082544` occurs zero times.

## Callees, and which paths reach the jal

Straight-line code calls `rs_crc32` (`0x800824F8`) with
`$a0 = $s5`, `$a1 = $s0` (the incoming buffer), and
`$a2 = 8` before any branch. `rs_crc32` is a leaf: no
`jal`, no `$s5` write. It loads table words and does not
store the pointer. Because `$a2` is 8, the length-zero
exit is not taken, and `lw` at `0x80082524` reads the
table on the first byte. A NULL `rs_malloc` return faults
there, before this function reaches `rs_free`. That is
the same unproven allocator-failure edge as s3604–s4485,
not a second pointer identity.

`rs_free` itself still branches away when `$a0 == 0`
(`beq` at `0x80001CA4`). That branch is not reached with
NULL on this original stream.

After the CRC, `lw $v1, 0x18($s1)` reads the cheat-flag
word at `0x80130B58` (`$s1 = 0x80130B40`). Bit `0x10`
splits the function:

| Path | Control | Frees `$s5`? |
|---|---|---|
| bit `0x10` set | `jal load_naboo_starfighter` at `0x800822E0`, then `j 0x80082490` at `0x800822EC` | no; jumps to the epilogue |
| bit `0x10` clear | `beqz` at `0x800822D4` to `0x800822F4`, then the 29-entry compare loop | yes, exactly once |

`load_naboo_starfighter` is not on a path that reaches
this jal. Its own `jal rs_free` at `0x8006C8C4` frees the
`pl_crafts/koelsch_HMT` block classified in s4478. It
does not write `$s5`, and its argument is the CRC in
`$v0`, not the lookup table. The `j 0x80082490` delay
`addu $v0, $zero, $zero` does not write `$a0` or `$s5`.

On the compare path the lookup table is still `$s5`.
These instructions reach the jal, and none of them writes
`$s5`:

| PC | Instruction | Delay | Delay writes `$a0` or `$s5`? |
|---|---|---|---|
| `0x800823A8` | `beqz $a0, 0x80082430` | `addu $s4, $v0, $zero` | no |
| `0x800823B4` | `bnez $v0, 0x80082430` | `sltiu $v0, $a1, 0x13` | no |
| `0x800823BC` | `beqz $v0, 0x80082430` | `addiu $a1, $zero, 0x7` | no |
| `0x80082418` | `j 0x80082430` | `sw $a0, 0x18($v0)` | no |
| `0x80082428` | fall through when `$s0 >= 0x1D` | the not-taken `bnez` delay `andi $v1, $s0, 0xFF` | no |

`bnez` at `0x80082428` targets `0x80082310` and skips the
jal while entries remain. Its delay writes `$v1`, not
`$a0` or `$s5`. The compare loop writes `$a0` with flag
words. The jal delay replaces `$a0` with `$s5` before
`rs_free` runs.

`isCheatCodeIndexAllowed` (`0x800824B8`) is called only
after the free, with `$a0 = $s0` (the matched index). It
is a leaf. It does not free the table.

## Callers

One definition. One generated call. One uncompressed-ROM
hit of jal word `0x0C02089C`, at file offset `0x12C01C`.
Those bytes are `applyMenuCheatCode` at linked VRAM
`0x800C4E7C` (file-to-VRAM delta `0x7FF98E60`, not the
main-segment `0x7FFFF400`). The raw pointer word
`0x80082270` occurs zero times.

| Caller | Site | Argument |
|---|---|---|
| `applyMenuCheatCode` | `0x800C4E7C` | incoming `$a0`; `$a1 = 0`; `$a2` = a stack byte zeroed in the delay |

`applyMenuCheatCode` does not write `$a0` before the jal.
Its only caller is `menuControllerInput` at `0x800B56D8`
(`lw $a0, 8($s4)`, delay `nop`). One ROM hit of jal word
`0x0C03139B`, at file offset `0x11C878`, same delta. The
PC also falls inside the `playerXwingUpdate` symbol
range; the generated function is `menuControllerInput`.
That `$a0` becomes `$s0` here and is the 8-byte buffer
`rs_crc32` hashes. It is not `$s5`. The caller restores
nothing related to the lookup table, because this
function restores the incoming `$s5` before `jr`. After
the call, `menuControllerInput` copies 9 bytes from
`0x800A6658` over that buffer. It does not free the
table.

The bit-`0x10` path therefore abandons the `0x400` block.
The pointer dies in the restored `$s5`. That is one leak
of a legitimate allocator return on that original path,
not a second identity at this jal and not a pointer a
sibling already freed.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static
scope: the only value in `$s5` at the jal is the
`rs_malloc(0x400, 0)` return, no callee frees it before
this jal, and the function frees it once on every path
that reaches the jal. H-NextClassUnevaluable is not
selected. The bit-`0x10` early-out does not reach the
jal; it leaks that block instead of freeing a different
one. Runtime allocator legitimacy remains unproven. No
guard was added.

The next unaudited `jal rs_free` in address order is
`releaseModelAnimSlot` at `0x80082D5C` (entry
`0x80082CFC`, size `0x11C`, `funcs_20.c`). ROM:
`lw $a0, 0xC($v0)` at `0x80082D58`, jal word
`0x0C000726`, delay `addiu $s1, $s1, 1` at `0x80082D60`.
The delay does not write `$a0`. The same function has
two later jals, at `0x80082D98` (`lw $a0, -0x5664($at)`,
delay `nop`) and `0x80082DC0` (`lw $a0, -0x5670($at)`,
delay `nop`). Those are separate sites.
