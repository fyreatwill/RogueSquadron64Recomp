# M3 s4481 — walkDatTreeAndCollectSubtypes rs_free of the 0x2A0 child array

## Work unit

Static census of the one original `jal rs_free` in
`walkDatTreeAndCollectSubtypes` (`0x80072AF8`, size `0xE8`), at
`0x80072B8C`. The instruction before the jal is `lw $a0, 8($s0)`
at `0x80072B88`. The delay slot is `nop`. No build or runtime run
was performed. `saveServiceWorker` (s4480) was not re-audited.

The discriminator was the writer of the word at `8($s0)` on every
path that reaches `0x80072B8C`, every callee `jal rs_free`, and
every caller argument:

- H-NextClassGap: that word can be a non-allocator value, or a
  pointer a sibling already freed, with the writer named.
- H-NextClassComplete: the word is the matching allocator return,
  and each such pointer is freed once.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`.

Same-scan positive control: the `jal 0x80001C98` comment scan
still locates closed `0x8006DA28` and `0x8006F378` in `funcs_17.c`,
and still locates `0x8006C8C4` (also `0x8006B814`, `0x8006C4A8`,
`0x8006C650`) in `funcs_16.c`. The ROM word `0x0C000726` matches
`0x8006B814`, `0x8006C8C4`, `0x80005268`, `0x8006DA28`,
`0x8006F378`, and `0x80072B8C`. A scan that missed `0x8006F378`
would have been invalid. ROM and the generated listing agree on
the free sequence.

## Census

| Site | `$a0` | Setup | Classification |
|---|---|---|---|
| `funcs_18.c`, `0x80072B8C` | word at `8($s0)` | `lw $a0, 8($s0)`; `$s0` is the incoming node | sole free; the `rs_malloc(0x2A0)` child array |

`$s0` is assigned once before the free: `addu $s0, $a0, $zero` at
`0x80072B00`. The epilogue reload at `0x80072BD4` is after the
free. The function stores the node byte at `0($s0)` after the
free and does not store the word at `8($s0)`. Its only `jal` is
`rs_free`. No callee frees the pointer.

The free is reached only when byte 0 is not `255` and bit `0x80`
of byte 0 is set. Both the count-zero branch (`0x80072B24`) and
the loop fall-through execute the `lw` before the jal. The bit
clear path at `0x80072BA0` collects byte 6 and does not free.
After the free, `sb` of `255` at `0($s0)` is the delay slot of
`j 0x80072BD0`, so a second entry sees `255` and skips.

## Who writes the word

The only store to offset 8 in `walkDatTreeAndAllocSubtypeBuffers`
(`0x80071064`) is `sw $v0, 8($s0)` at `0x800710FC`. `$v0` is the
return of `jal rs_malloc` at `0x800710F4`. The arguments are size
`0x2A0` and flags `0`, set at `0x800710E4` and `0x800710E8`. The
delay slot `sb $zero, 4($s0)` does not write `$v0`. `0x2A0` is
`12 * 0x38`, the same cap as `sltiu` of the count byte against
`0xC`.

That store is in the same straight-line block as `sb` of `0x80`
at `0x800710F0`, and only when the incoming 5th argument is
negative and byte 0 is `255`. The recursive call at `0x8007116C`
passes a nonnegative index as that 5th argument and clears bit
`0x80` of `$a3` (`and $a3, $s5, $s2` with `$s2 = -0x81`), so it
cannot take the malloc block. `dispatchDatSubtypeByRandomIndex`
is the only other caller. Every one of its 24 calls passes the
same node in `$s4` and `-1` as the 5th argument, after storing
`255` at byte 0.

No other instruction in the allocator sets bit `0x80` on the
parent node. `sb $s5, 0($s0)` at `0x800711B8` runs only when that
bit is already clear, and the leaf path that reaches it with the
parent still in `$s0` has bit `0x80` of `$s5` clear. The same
store at `0x800711EC` writes the parent only on that leaf path;
once `$s0` has moved to a child slot the store is inside the
`0x2A0` array, not the parent word. `sb` of `255` at `0x800712D4`
clears the bit and does not reach this free. Collect and
dispatch otherwise write `255`, not `0x80`.

A whole-function store scan of each collect caller found no store
of the parent pointer word. Two immediates collided with stack
saves (`sw $zero, 0x50($sp)`, `sw $fp, 0x108($sp)`,
`sw $s6, 0x100($sp)`) and are not the node.

## Callers

Twelve direct `jal 0x80072AF8`. No `addiu`/`ori` materializes
that address, so there is no indirect call site in the scanned
image. Every delay slot is `addiu` of an object register. The
freed word is `8` bytes into that embedded node. The matching
`dispatchDatSubtypeByRandomIndex` call in the same function
passes that same address (`npcGroundTransportUpdate` reloads
`*(*(object+0x38)+0x1A8)` into `$s2` for dispatch and `$s0` for
collect; those are different action blocks, joined by `j`, and
the address expression matches).

| Call | Node |
|---|---|
| `parseDatItemSubtypes1To5` `0x800479BC` | `$s0+0x40` |
| `updateDestructionDebrisNpc` `0x8006CEB0`, `0x8006D744` | `$s1+0x48` |
| `npcPowerGeneratorUpdate` `0x800780A0` | `$s2+0x1DC` |
| `npcWordDevastatorUpdate` `0x8007F428` | `$s3+0x2BC` |
| `runModelViewerSoundDemo` `0x800CAF70` | `$s1+0xE4` |
| `npcShuttleUpdate` `0x800D3E60` | `$s1+0xC8` |
| `npcDebrisFieldUpdate` `0x800D5668` | `$s1+0xCC` |
| `npcRadarDishUpdate` `0x800DCA18` | `$s1+0xB4` |
| `npcGroundTransportUpdate` `0x800DEE38` | `$s0+0x48` |
| `handleRayShieldedNpcDestroy` `0x800E428C` | `$s1+0x40` |
| `npcWaterCraftUpdate` `0x800E67CC` | `$s3+0x100` |

Dispatch at `0x8012AA90` and `0x801399EC` does not jal this
function. Those nodes do not reach `0x80072B8C`.

`rs_free` branches away when `$a0 == 0` (`beq` at `0x80001CA4`).
A NULL `rs_malloc` return is the same unproven allocator-failure
edge left open by s3604–s4480, not a second pointer identity.
A later dispatch that stores `255` and then mallocs again
replaces the word with a new return; the pointer this jal frees
is that return. An early name-lookup miss can abandon a previous
array without freeing it. That path sets byte 0 to `255` and
does not reach this jal.

## Classification

H-NextClassComplete. H-NextClassGap is refuted at static scope:
the only parent word that reaches the free is the
`rs_malloc(0x2A0)` return stored at `0x800710FC`, and the `255`
mark after the free makes a second entry skip. H-NextClassUnevaluable
is not selected. Runtime allocator and freelist legitimacy remain
unproven. No guard was added.

The symbol comment's "4 children" and `0x8010A898` list address
are stale. The ROM count is the byte at node+4, the stride is
`0x38`, and the list is the byte at `0x8013A898` plus the pointer
at `0x8013A89C`. The comment also omits this free.

The next unaudited `jal rs_free` in address order is
`initWaterSprayParticles` at `0x80072E40` (entry `0x80072CF0`,
size `0x1D4`, `funcs_18.c`). `$a0` is `$s3` (`addu $a0, $s3` at
`0x80072E3C`). The delay slot `addu $s0, $v0` writes `$s0`, not
`$a0`. The one `$s3` assignment in that function is
`addu $s3, $v0` at `0x80072DD4`, after `jal load_asset`.
