# M3 s4490 — audioSeqFree rs_free

## Work unit

Static census of `audioSeqFree` (`0x80083C50`, size `0x20`) in
`.text`, jal at `0x80083C58`. ROM: `addiu $sp, $sp, -0x18` /
`sw $ra, 0x10($sp)` / `jal rs_free` / `nop` / `lw $ra` /
`addiu $sp, $sp, 0x18` / `jr $ra` / `nop`. The delay is
`nop` (`0x00000000`) and does not write `$a0`. The
prologue does not write `$a0` either. No build or runtime
run was performed. `0x80082DC0`, `0x80082D98`, and
`0x80082D5C` were not re-audited.

The discriminator was every original assignment of `$a0`
from the prologue through the free, every direct or
indirect entry, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator
  value, or a pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one
  allocator return, freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity
  can reach `$a0`, or a possible indirect entry cannot be
  accepted or rejected.

Same-scan positive control: the `jal 0x80001C98` comment
scan still locates closed `0x80082430`, closed
`0x80082D5C`, closed `0x80082D98`, closed `0x80082DC0`,
and this site in `funcs_20.c`; still locates closed
`0x8007A814`, closed `0x8007B23C`, and closed `0x8007BE50`
in `funcs_19.c`; still locates `0x80072E40` in
`funcs_18.c`; and still locates `0x8006F378` in
`funcs_17.c`. The ROM word `0x0C000726` matches all of
those PCs. A whole-ROM count of that word is 204, and all
204 sit in `.entry`, `.text`, `.ovl.mission`, `.ovl.menu`,
or `.ovl.cinematic`. A scan that missed `0x80082DC0` or
`0x8007BE50` would have been invalid. ROM and the generated
listing agree on the eight instructions. The generated
tree contains the definition and no call.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_20.c`, `0x80083C58` | incoming argument | delay `nop`; prologue only saves `$ra` | no path reaches the jal |

ROM words at `0x80083C50`:

| PC | Word | Instruction |
|---|---|---|
| `0x80083C50` | `0x27BDFFE8` | `addiu $sp, $sp, -0x18` |
| `0x80083C54` | `0xAFBF0010` | `sw $ra, 0x10($sp)` |
| `0x80083C58` | `0x0C000726` | `jal rs_free` |
| `0x80083C5C` | `0x00000000` | `nop` |
| `0x80083C60` | `0x8FBF0010` | `lw $ra, 0x10($sp)` |
| `0x80083C64` | `0x27BD0018` | `addiu $sp, $sp, 0x18` |
| `0x80083C68` | `0x03E00008` | `jr $ra` |
| `0x80083C6C` | `0x00000000` | `nop` |

`$a0` is not a destination of any of those instructions.
The only jal in the function is `rs_free`. There is no
branch back to it.

## What reaches the jal

Nothing. Counted on `./rogue_squadron.z64` (16 MiB), any
alignment:

| Bytes | Meaning | Count |
|---|---|---|
| `0x0C020F14` | `jal 0x80083C50` | 0 |
| `0x08020F14` | `j 0x80083C50` | 0 |
| `0x80083C50` | absolute pointer | 0 |
| `0x0C020F0A` | `jal 0x80083C28` | 0 |
| `0x08020F0A` | `j 0x80083C28` | 0 |
| `0x80083C28` | `audioSeqMallocZero` entry | 0 |
| `0x80083C30` | skipped malloc prologue | 0 |
| `0x80083C38` | malloc body | 0 |

The same zero holds for the `j`, `jal`, and absolute-pointer
encodings of every instruction address from `0x80083C50`
through `0x80083C6C`.

Every `j`, `jal`, conditional branch, and branch-and-link
in the four CPU sections was decoded. The only transfer
into `[0x80083C28, 0x80083C70)` is `j 0x80083C38` at
`0x80083C28` (word `0x08020F0E`). That jump stays inside
`audioSeqMallocZero`. It does not enter `audioSeqFree`.
`audioSeqMallocZero` itself returns at `0x80083C48`
(`jr $ra`, delay `nop`) and does not fall through.
`parseModelAnimType2Entry` has already returned at
`0x80083C20`.

No `lui` plus `addiu`/`ori` within 80 bytes produces an
address in that range, and a straight-line constant
tracker over the four sections produces none either. The
153 `jalr` instructions have no tracked constant target
in the range. A `jalr` cannot load a pointer that is not
in the image. The symbol name is not a reference: the
generated sources call neither `audioSeqFree` nor
`audioSeqMallocZero`.

`audioSeqMallocZero` jumps over its own prologue, calls
`rs_malloc` with `$a1 = 0`, then reloads `$ra` and pops
the frame it did not allocate. That body is reachable
only from the unreferenced entry jump. It does not jal
`audioSeqFree`.

## Classification

H-NextClassComplete. No path reaches the jal, which is
the second arm of that hypothesis. H-NextClassGap is
refuted: there is no reached path that can pass a
pointer. H-NextClassUnevaluable is not selected. The
indirect entries that this image can express (direct
`j`/`jal`, PC-relative branch, stored pointer, and
`lui`/`addiu` materialization into `jalr`) were each
rejected by a search that still finds the 204 real
`jal rs_free` words. No guard was added.

The other `jal rs_free` sites still in `.text` are the
destructor and speech frees closed in s3602–s3607. The
eighteen jal PCs those docs do not spell
(`0x80091DDC` through `0x80091FAC`, except the ones they
name directly) are the instruction immediately after the
documented `lw $a0`. Each of those loads is in the s3602–
s3605 docs. They are not a new class.

The next unaudited `jal rs_free` is in `.ovl.mission`,
not in `.text`. `handleHUD` (`0x800C0084`, size
`0x1AE0`) jals at `0x800C1084`. ROM word is `0x0C000726`.
The delay at `0x800C1088` is `nop`. The instruction
before the jal is `lw $a0, 0x230($s2)` (`0x8E440230`).
That is a first scan, not a classification. The mission
ROM offset is `vram - 0x7FFFF400`. Menu and cinematic
do not use that difference.
