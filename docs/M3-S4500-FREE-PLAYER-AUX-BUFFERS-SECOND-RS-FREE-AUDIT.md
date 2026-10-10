# M3 s4500 — freePlayerAuxBuffersIfActive second rs_free (slot +0xC array)

## Work unit

Static census of the second `jal rs_free` in `freePlayerAuxBuffersIfActive`
(`.ovl.mission`, entry `0x80100F40`, size `0x68`) at `0x80100F90`. ROM bytes
only; no build or runtime run. `0x80100F84` was not reclassified (closed
s4499). Helper scripts: `scratch/agent/s4500_dis.py` (mini MIPS decoder, system
python3), `s4500_scan*.py`.

Same-scan positive control (ROM `./rogue_squadron.z64`, offset
`vram - 0x7FFFF400`): `0x0C000726` is present at closed `0x800F9F94`,
`0x800EED50`, `0x800EC564`, `.text` `0x8007BE50`, and at `0x80100F84` and
`0x80100F90`. The delay at `0x80100F94` is `0`. The control passed.

Hypotheses: H-NextClassComplete (one allocator return freed once, or no path),
H-NextClassGap (named non-allocator / already-freed writer on a reached path),
H-NextClassUnevaluable.

## What is freed

```
0x80100F8C  lw  $a0, 0xC($s0)     # the value freed
0x80100F90  jal rs_free
0x80100F94  nop                   # does not write $a0
```

`$s0 = 0x8010CF20 + (index & 0xFF) * 0x18`; the `beqz` at `0x80100F70` on the
count byte skips both frees, and no branch targets `0x80100F90`. All nine
callers (`jal 0x80100F40` at `0x800AD184, 0x800B56E0, 0x800B742C, 0x800B8764,
0x800BA244, 0x800BBAF4, 0x800BCAD4, 0x800BD7F4, 0x800BEA80`; re-counted this
session, no `j` form) have delay `addu $a0, $zero, $zero`, so index 0 and the
word is `0x8010CF2C`.

## Who writes 0x8010CF2C

Exactly one store of slot offset `+0xC` exists in the table code
(`0x800FFE00..0x80101100`): `sw $v0, 0xC($t1)` at `0x80100854` inside
`allocateCraftAnimationStateForSlot` (`0x801007C0`), with `$t1 = $s0` = the
same slot base. `$v0` there is the return of the second
`jal rs_malloc` at `0x80100834` (`$a0 = count << 1` in the delay `sll`,
`$a1 = 0`): the instructions between (`0x8010083C..0x80100850`) write only
`$a3,$t2,$t4,$t1,$t5,$t3`. The only other `sw ...,12(...)` hit in the wider
region, `0x800FFEE8`, stores through `$a3` (an object pointer, not the slot).
Stores with offset `-12`/`-4` from a `0x8010CF38`-derived base: none.
The `0x8010CF38` table (written at `0x800FFE64..0x800FFEA4`) starts after slot
0 (`0x8010CF20..0x8010CF37`) and is a different table; index 0 does not alias
it. The nine `jal 0x801007C0` sites are the only allocators (re-counted).

The fill loop (`0x80100858..0x801008CC`) runs a second pass (`$a3 = 1`) that
does `lw $v1, 8(slot + 4*$a3)` = slot `+0xC`, then `sh 0xFFFF` through it
at `0x801008A0`, so a null `+0xC` pointer faults and allocate does not return.
The two mallocs are independent allocations (the first is not freed between).

## Freed once

Nothing clears `+0xC` and no `jal rs_free` other than the two in this function
exists in `0x800FFE00..0x80101100`. `despawnCraftAnimationSlotNpcs`
(`0x80100594`) loads `+8` only and has no `sw` to `+0xC`. The reach analysis
(only mode-2 `destroyNpcSlotByIndex` reaches the function; one call per
craft block; no second destroy of the same index) is s4499's and applies
identically because the `beqz` gate and caller set are shared. Zero-count crafts
(snow, falcon, tie) skip the jal.

## Verdict

H-NextClassComplete. Zero count: no path. Nonzero: one `rs_malloc(count << 1, 0)`
return from `0x80100834`, stored at `0x80100854`, freed once. No guard added.
H-NextClassGap is not selected (no non-allocator writer; the uncleared slot is
not a Gap without a second destroy). H-NextClassUnevaluable is not selected.
ORIGIN: `allocateCraftAnimationStateForSlot` writes slot +0xC from the second
`rs_malloc` at `0x80100834`; the value is the legitimate user pointer.

Mission-image exhaustion: a scan of `0x80100F98..0x8010B6D0` for word
`0x0C000726` found no later `jal rs_free` (second, independent run of s4499's
claim; this one has a passing control). `freePlayerAuxBuffersIfActive` was the
last mission-overlay site by address.
