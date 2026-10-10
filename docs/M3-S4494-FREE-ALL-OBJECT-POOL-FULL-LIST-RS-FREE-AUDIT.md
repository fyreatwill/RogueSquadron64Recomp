# M3 s4494 — freeAllObjectContextPoolNodes rs_free of the full-list slab

## Work unit

Static census of the second `jal rs_free` in `freeAllObjectContextPoolNodes`
(`.ovl.mission`, entry `0x800EC514`, size `0x74`) at `0x800EC564`. ROM
bytes were used. Mission VRAM is `0x800A5130` size `0x665A0`, so this PC
is inside that overlay. The menu overlay ends at `0x800CD520` and the
cinematic overlay ends at `0x800B0940`, so those overlays do not contain
this instruction. No build or runtime run was performed. The partial-list
jal at `0x800EC538` (closed s4493) was not re-classified. Its splice was
re-disassembled only to test whether this walk frees a node that walk
already freed.

The discriminator was every original assignment of `$a0` from the second
loop's entry through the free, every caller, and every callee
`jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control: `funcs_40.c` still has `jal 0x80001C98` at
closed `0x800EC538`, closed `0x800EC404`, and this site `0x800EC564`.
`funcs_33.c` still has it at closed `0x800C1084`. `funcs_19.c` still has
it at closed `0x8007BE50`. The ROM word at all five PCs is `0x0C000726`.
A scan that missed `0x800EC538` or `0x800EC404` would have been invalid.

## What is freed

ROM and `RecompiledFuncs/funcs_40.c` agree. The second loop does not
read the incoming argument. The empty-list arm does not reach the jal:

```
lui  $v1, 0x8011              # 0x800EC54C
lw   $v0, -0x3F2C($v1)        # 0x800EC550  full head 0x8010C0D4
beqz $v0, 0x800EC578          # 0x800EC554
addu $s0, $v1, $zero          # 0x800EC558  s0 = 0x80110000
lw   $a0, -0x3F2C($s0)        # 0x800EC55C
lw   $v0, 0xC($a0)            # 0x800EC560  next
jal  rs_free                  # 0x800EC564
sw   $v0, -0x3F2C($s0)        # 0x800EC568  delay: head = next
lw   $v0, -0x3F2C($s0)        # 0x800EC56C
bnez $v0, 0x800EC55C          # 0x800EC570
```

Nothing between `0x800EC55C` and the jal writes `$a0`. The delay writes
the next pointer through `$s0` and does not write `$a0`. The generated
body does the same: `r4` is the load, the store writes
`MEM_W(-0x3F2C, r16)` from `r2`, then `rs_free`. There is no jal on
this path before `rs_free`. The partial-list loop has already returned.

`rs_free` saves `$s0` at `0x80001C9C` and restores it at `0x80001F7C`.
The loop base stays `0x80110000`. Its jals are `osRecvMesg`
(`0x800331D0`) and `osSendMesg` (`0x80033410`). Neither contains
`jal rs_free`. A zero argument takes `beqz` at `0x80001CA4` and does
not free. The second loop also reloads `$s0` from the fresh `lui`
before the first iteration, so it does not depend on the first loop's
`$s0`.

`$a0` is the word at `0x8010C0D4`. These are the stores of that word.
The base of each direct store is `lui $reg, 0x8011`. The only
`addiu`/`ori` in the scanned image that builds the address is
`addiu $a1, $v0, -0x3F2C` at `0x800EC3C0`, and the store through that
pointer is `0x800EC400`. One `sb` with immediate `0xC0D4` decodes at
flat VRAM `0x801E73D4` (ROM `0x1E7FD4`). That offset is past `.text`
and past the mission, menu, and cinematic images. It is not a writer.

| PC | Value stored | When |
|---|---|---|
| `0x800EC33C` | `$a1`, the slab | `allocObjectPoolNode`, after the slab's free count hits 0. The slab has just been unlinked from `0x8010C0D0`. |
| `0x800EC400` | that slab's `+0xC` | `unlinkAndFreeChildNpcNode` emptying path, and only when the free count was 0 and the slab is the full head. The slab is then freed at `0x800EC404`. |
| `0x800EC4A0` | that slab's `+0xC` | Same function, non-empty path, and only when the old free count was 0 and the slab is the full head. The slab is then pushed onto `0x8010C0D0`. This path does not call `rs_free`. |
| `0x800EC4EC` | 0 | `resetObjectContextPool`. The jal is not reached. |
| `0x800EC568` | the node just loaded as `$a0`, its `+0xC` | This walk, in the delay slot, before `rs_free`. |

`$a1` at `0x800EC33C` is the slab whose free count just became 0. No
branch in `allocObjectPoolNode` enters `0x800EC2D8`–`0x800EC33C` from
above; the unlink and the push are the fall-through of `bnez` at
`0x800EC2D0`. That `$a1` was loaded from the partial head at
`0x800EC1A4` and then followed through `+0xC` at `0x800EC248`, or it
is the `rs_malloc` return copied at `0x800EC260` when that walk ends.
The second malloc is appended (`0x800EC28C`–`0x800EC294`) before the
free-count test, so a slab that immediately becomes full is linked and
then unlinked before the push. The `beqz` at `0x800EC1B0` also targets
the second malloc, but its head is non-zero on both entries: an empty
list has already published the first `rs_malloc` return or returned,
and the other entry branched because the head was non-zero.

Both `rs_malloc` calls (`0x800EC138`, `0x800EC258`) pass size `0x6C0`
and flags `1`. The flag tests inside `rs_malloc` are bits `0x4` and
`0x10` of `$s1`. Bit `0x1` selects neither. The return is `addu $v0,
$s2` at `0x80001C74` after `addiu $s2, $a1, 0x10` at `0x80001C10`.
Nothing writes `$s2` between those two instructions. A NULL block
takes `beqz` at `0x80001AF0` to that same return with `$s2` still 0.
The first caller returns 0 before a slab exists. The second caller
writes through the pointer before this push, so a NULL return does not
reach `0x800EC33C`.

Slab `+0xC`, which is what the head becomes on an unlink or on this
walk's delay, is written in these functions as 0 (`0x800EC168`,
`0x800EC28C`, `0x800EC334`, `0x800EC4C8`), a new `rs_malloc` return
(`0x800EC294`), the node's old next during a splice (`0x800EC2E8`,
`0x800EC3D8`, `0x800EC474`), or the other list's old head when the node
is pushed (`0x800EC328`, `0x800EC4B4`). None of those stores writes a
node as its own next.

A slab leaves its old list before it is pushed onto the other one.
Free count hitting 0 unlinks it from `0x8010C0D0` at
`0x800EC2D8`–`0x800EC314`, then this push stores it at `0x8010C0D4`.
The reverse move unlinks it from `0x8010C0D4` at `0x800EC464`–`0x800EC4A0`,
then pushes it onto `0x8010C0D0`. The partial-list jal walks only
`0x8010C0D0`, and it runs to completion before this loop loads
`0x8010C0D4`. The two walks do not free the same node.

The emptying path splices the slab out before `jal rs_free` at
`0x800EC404`. Free count 0 selects `0x8010C0D4` (`0x800EC3C0`). The
head store there writes the successor, not the slab, and only when the
slab is the head. A slab freed there is not still linked, so this walk
does not free it again.

One iteration loads the head, loads `+0xC`, publishes that next as the
head, then frees the old head. The following iteration loads the new
head. A zero-terminated chain is freed once per node.

## Who reaches the jal

The only `jal 0x800EC514` in the scanned image is `0x800FBAD4`, inside
`endMissionCleanup` (`0x800FB9E4`). The delay is `nop`. There is no
`j` to the entry, no raw word `0x800EC514` anywhere in the ROM, and no
`addiu`/`ori` with immediate `0xC514`. An indirect entry is rejected.
Menu and cinematic are exclusive overlays and are not resident with
this function.

`endMissionCleanup` reaches the jal on a straight line. Both callers
are in `mainGameLoop` (`0x8003DFA0`), at `0x8003E2C4` and `0x8003E388`,
each with delay `nop`. The argument is not read.

## Verdict

H-NextClassComplete. The value at the jal is the full-list head. Every
non-zero store of that word is an `rs_malloc(0x6C0, 1)` user pointer or
the `+0xC` link of such a slab, which is the same kind of pointer. The
walk frees each still-linked node once. Zero does not reach the jal.
The partial-list walk frees a disjoint set, and the other free of the
same slab unlinks it first. No guard was added.

H-NextClassGap is not selected. The reached value is that allocator
return, and no reached writer publishes a non-allocator or
already-freed pointer. H-NextClassUnevaluable is not selected. One
caller, the entry is not materialized as a pointer, and the head stores
named above do not publish a second identity.

The next unaudited `jal rs_free` is `preloadSceneReferencedSongs`
(`0x800EEA54`, size `0x328`) at `0x800EED48`. The delay is
`addu $a0, $s2, $zero` at `0x800EED4C`, which writes `$a0`. The only
`$s2` write before that jal in this function is `addu $s2, $v0` at
`0x800EEC08`, after `jal rs_malloc` at `0x800EEBF8`. The jal at
`0x800EED50` is a separate site. Its delay is `addu $a0, $s3, $zero`.
