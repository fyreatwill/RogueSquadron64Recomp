# M3 s4483 — downscaleImageHalfResBoxFilter rs_free of the half-res temp

## Work unit

Static census of the one original `jal rs_free` in
`downscaleImageHalfResBoxFilter` (`0x8007A260`, size `0x60C`),
at `0x8007A814`. The instruction before the jal is
`addu $a0, $s5, $zero` at `0x8007A7F8`. Nothing between
that instruction and the jal writes `$a0`. The delay slot
is `sb $v1, 1($v0)` at `0x8007A818`. `$v0` there is
`$s0+$s2`, the output cursor in the caller's pixel
buffer, so the slot stores one filtered byte and does not
write `$a0`. No build or runtime run was performed.
`initWaterSprayParticles` (s4482) was not re-audited.

The discriminator was every original assignment of `$s5`
from the prologue through the free, every callee
`jal rs_free`, and every caller argument:

- H-NextClassGap: `$s5` can be a non-allocator value, or a
  pointer a sibling already freed, with the writer named.
- H-NextClassComplete: `$s5` is the matching allocator
  return, and that pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates this site in `funcs_19.c` (and the two
later sites `0x8007B23C`, `0x8007BE50`), still locates
closed `0x80072B8C` and `0x80072E40` in `funcs_18.c`, and
still locates `0x8006DA28` and `0x8006F378` in
`funcs_17.c`. The ROM word `0x0C000726` matches
`0x80072E40`, `0x80072B8C`, `0x8006F378`, and
`0x8007A814`. A scan that missed `0x80072E40` would have
been invalid. ROM and the generated listing agree on the
free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_19.c`, `0x8007A814` | `$s5` | `addu $a0, $s5` at `0x8007A7F8`; delay stores a filtered byte through `$v0` | sole free; the `rs_malloc` temp of `width * height * 3` bytes |

`$s5` is assigned once before the free: `addu $s5, $v0, $zero`
at `0x8007A320`, after `jal rs_malloc` at `0x8007A318`.
The next write is `lw $s5, 0x44($sp)` at `0x8007A840`,
which is the epilogue restore and is after the free.
`sw $s5, 0x44($sp)` at `0x8007A274` saves the incoming
register and does not assign it. No later instruction
stores `$s5`, so the malloc pointer is never written to
memory.

Removing `0x8007A320` from the control-flow graph makes
`0x8007A814` unreachable. The free's only predecessor is
`0x8007A810`. The filter loops branch among themselves;
none contains the free and none skips the assignment.

## What rs_malloc is asked for

`addu $a1, $zero, $zero` at `0x8007A2F4` sets flags 0.
No instruction before the jal writes `$a1` again. The
delay slot `addu $a0, $s0, $zero` at `0x8007A31C` runs
before `rs_malloc` and is the size the callee sees.

`$s3` is the sign-extended halfword at `0x28($a0)`
(width). `$t0` is the sign-extended halfword at
`0x2A($a0)` (height). `mult $s3, $t0` / `mflo $v0` is
the product. `sll $s0, $v0, 1` then `addu $s0, $s0, $v0`
is that product times 3. `$s2` is `lw $s2, 0($a0)`, the
caller's pixel pointer. `zmemcpy` then copies `$s0`
bytes from `$s2` into `$s5`.

Three branches sit before the malloc and do not reach
the free:

| Branch | Condition | Lands | Free? |
|---|---|---|---|
| `0x8007A2C4` | both dimensions `< 3` | epilogue `0x8007A830`, `$v0 = 0` | no |
| `0x8007A2DC` | format nibble at `0x2E($a0)` is not 3 | epilogue `0x8007A830`, `$v0 = 0` | no |
| `0x8007A2E8` | bit `0x8000` of that format halfword is set | `0x8007A824` then the epilogue, `$v0 = 1` | no |

The `0x8000` path shares the success path's half-dimension
stores at `0x8007A824`. Those stores do not write `$s5`
and do not call `rs_free`. On the success path, after the
free, `sh $fp, 0x28($t1)` and `sh $t0, 0x2A($t1)` publish
`width >> 1` and `height >> 1`. The filtered bytes were
written back through `$s2`, the original pixel pointer,
which is not this `$a0`.

## Callees while `$s5` holds the pointer

`zmemcpy` (`0x80018EF4`, size `0xA4`) is a leaf. It has
no `jal` and no `$s5` write. A zero length returns at
once; otherwise the delay slot copies `$a0` into `$t5`
and the copy uses that pointer. It does not store
`$a0`.

`sampleRgbBoxFilter2x2AtSubpixel` (`0x8007A0F0`, size
`0x170`) is a leaf. It has no `jal`, no `$s5` write, and
no store of `$a1`. Every call in this function passes
`$a1 = $s5` (the temp) and `$a0 = $sp+0x18` (a stack
sample). Its stores write sample bytes into that stack
record. The caller then stores those bytes through
`$s2`.

No function in that set contains `jal rs_free`. None
returns with the caller's `$s5` changed. `rs_malloc`
itself does not write `$s5`, and it returns before `$s5`
is assigned.

## Callers

Two direct `jal 0x8007A260` encodings (`0x0C01E898`),
both in `load_hmt_and_hob`:

| PC | Delay | `$a0` |
|---|---|---|
| `0x800566A4` | `addu $a0, $s0, $zero` | `$s0` |
| `0x800566B4` | `addu $a0, $s0, $zero` | the same `$s0` |

`$s0` is `addu $s0, $s6, $s5` at `0x800566A0`, once.
`$s5` there is 4 (`addiu $s5, $zero, 4` at `0x80056640`).
`$s6` is `addu $s6, $s3, $v0` at `0x80056624`, where
`$v0` is `lw $v0, 4($s3)` and that sum is stored back to
`4($s3)`. `$s3` is this caller's HMT `rs_malloc` return
(s3630). So both calls pass an interior image record at
`header+4`, not the temp this function frees.

Bit 1 of `$s4` (`$fp`) skips both calls. Bit 2 (`$s7`)
skips only the second. When both run, they pass the same
record. Each entry mallocs and frees its own temp. The
ROM contains no data word `0x8007A260` and no
`lui 0x8007` / `addiu` or `ori 0xA260` pair. There is no
indirect call.

`rs_free` branches away when `$a0 == 0` (`beq $s0, $zero`
at `0x80001CA4`). A NULL `rs_malloc` return is the same
unproven allocator-failure edge left open by s3604–s4482,
not a second pointer identity. `zmemcpy` uses `$a0`
before this jal, so a NULL return faults first.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static
scope: the only value in `$s5` at `0x8007A814` is the
`rs_malloc` return of `width * height * 3` bytes with
flags 0, no callee frees it, and it is not stored where
a sibling could free it. H-NextClassUnevaluable is not
selected. Runtime allocator legitimacy remains unproven.
No guard was added.

The next unaudited site in address order is
`npcShieldUpdate` at `0x8007B23C` (entry `0x8007AEF8`,
size `0xD20`, `funcs_19.c`). `$a0` is `lw $a0, 0x38($s3)`
at `0x8007B238`. The delay slot is `nop`. A first scan,
not a classification: the `$s3` writes before that jal
are `lw $s3, 4($s4)` at `0x8007AF2C` and
`addu $s3, $v0, $zero` at `0x8007AF70` after
`jal rs_malloc` at `0x8007AF68`. No `sw` with immediate
`0x38` appears in the function before the free. `j
0x8007BBF0` at `0x8007B230` skips the free. The site
after that is `heavyAttachedAudioEmitterNpcHandler` at
`0x8007BE50`.
