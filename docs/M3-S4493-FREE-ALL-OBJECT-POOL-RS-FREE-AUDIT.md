# M3 s4493 — freeAllObjectContextPoolNodes rs_free of the partial-list slab

## Work unit

Static census of the first `jal rs_free` in `freeAllObjectContextPoolNodes`
(`.ovl.mission`, entry `0x800EC514`, size `0x74`) at `0x800EC538`. ROM
bytes were used. `0x800EC538` is past the menu overlay end (`0x800CD520`)
and the cinematic overlay end (`0x800B0940`), so those overlays do not
contain this instruction. No build or runtime run was performed. The
second jal in this function, `0x800EC564`, walks `0x8010C0D4` and was
not classified. `unlinkAndFreeChildNpcNode` (closed s4492) was re-read
only to check that its free unlinks the slab before `rs_free`.

The discriminator was every original assignment of `$a0` from the
prologue through the free, every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control: `funcs_40.c` still has `jal 0x80001C98` at
closed `0x800EC404` and at this site `0x800EC538`. `funcs_33.c` still
has it at closed `0x800C1084`. `funcs_19.c` still has it at closed
`0x8007BE50`. The ROM word at all four PCs is `0x0C000726`. A scan that
missed `0x800EC404` or `0x800C1084` would have been invalid.

## What is freed

ROM and `RecompiledFuncs/funcs_40.c` agree. The function does not read
its incoming argument. The empty-list arm does not reach the jal:

```
lui  $v1, 0x8011              # 0x800EC514
lw   $v0, -0x3F30($v1)        # 0x800EC518  partial head 0x8010C0D0
beqz $v0, 0x800EC54C          # 0x800EC524
addu $s0, $v1, $zero          # 0x800EC52C  s0 = 0x80110000
lw   $a0, -0x3F30($s0)        # 0x800EC530
lw   $v0, 0xC($a0)            # 0x800EC534  next
jal  rs_free                  # 0x800EC538
sw   $v0, -0x3F30($s0)        # 0x800EC53C  delay: head = next
lw   $v0, -0x3F30($s0)        # 0x800EC540
bnez $v0, 0x800EC530          # 0x800EC544
```

Nothing between `0x800EC530` and the jal writes `$a0`. The delay writes
the next pointer through `$s0` and does not write `$a0`. There is no
jal on this path before `rs_free`. `rs_free` saves `$s0` at
`0x80001C9C`, restores it at `0x80001F7C`, and its own jals are
`0x800331D0` and `0x80033410`, not `rs_free`. The loop base stays
`0x80110000`. A zero head takes the `beqz` and does not call.

`$a0` is the word at `0x8010C0D0`. These are the stores of that word.
The base of each is `lui $reg, 0x8011`, or `$a1` after
`addiu $a1, $v0, -0x3F30` at `0x800EC3C4`. No other `addiu`/`ori` in
the main or mission image builds this address. Hits of immediate
`0xC0D0` past the mission image are in the data blob and are not this
word.

| PC | Value stored | When |
|---|---|---|
| `0x800EC148` | `rs_malloc` return, or 0 | `allocObjectPoolNode` publishes the first slab. Delay of `bnez`. Size `0x6C0`, flags `1`, jal `0x80001ACC` at `0x800EC138`. The 0 path returns before a slab exists. |
| `0x800EC314` | that slab's `+0xC` | Free count hit 0 and the slab is the partial head. The slab is moved off this list. |
| `0x800EC400` | that slab's `+0xC` | `unlinkAndFreeChildNpcNode` emptying path, and only when the slab is the partial head. The slab is then freed at `0x800EC404`. |
| `0x800EC4C0`, `0x800EC4C4` | the slab in `$a0` | Same function, non-empty path, after the slab is spliced out of the full list and pushed here. This path does not call `rs_free`. |
| `0x800EC4E8`, `0x800EC4F4` | 0 | `resetObjectContextPool`. The jal is not reached. |
| `0x800EC53C` | the node just loaded as `$a0`, its `+0xC` | This walk, in the delay slot, before `rs_free`. |

`rs_malloc` writes `$s2` only at `0x80001AE4` (`$s2 = 0`) and
`0x80001C10` (`addiu $s2, $a1, 0x10`). Nothing writes `$s2` between
that addiu and `addu $v0, $s2` at `0x80001C74`. The non-zero value
published at `0x800EC148` is the user pointer.

Slab `+0xC` is that same kind of value. The stores that create it, in
the functions that touch these heads, write 0 (`0x800EC168`,
`0x800EC28C`, `0x800EC334`, `0x800EC4C8`), a new `rs_malloc` return
(`0x800EC294`), the node's old next during a splice (`0x800EC2E8`,
`0x800EC3D8`, `0x800EC474`), or the other list's old head when the node
is pushed (`0x800EC328`, `0x800EC4B4`). A new node is not stored as its
own next.

A slab leaves its old list before it is pushed onto the other one.
Free count hitting 0 unlinks it from the partial list at
`0x800EC2D8`–`0x800EC314`, then pushes it onto `0x8010C0D4` at
`0x800EC318`–`0x800EC33C`. The reverse move unlinks it from the full
list at `0x800EC464`–`0x800EC4A0`, then pushes it here at
`0x800EC4A4`–`0x800EC4C8`. This jal walks only `0x8010C0D0`. It does
not free a node that the `0x800EC564` walk frees.

The emptying path splices the slab out before `jal rs_free` at
`0x800EC404`. Free count selects the list: zero uses `0x8010C0D4`
(`0x800EC3C0`), nonzero uses `0x8010C0D0` (`0x800EC3C4`). The
non-empty path does not call `rs_free`. A slab freed there is not
still linked, so this walk does not free it again.

One iteration loads the head, loads `+0xC`, publishes that next as the
head, then frees the old head. The following iteration loads the new
head. A zero-terminated chain is freed once per node.

## Who reaches the jal

The only `jal 0x800EC514` in the ROM is `0x800FBAD4`, inside
`endMissionCleanup` (`0x800FB9E4`). The delay is `nop`. There is no
`j` to the entry, no raw word `0x800EC514`, and no `lui`/`addiu` pair
that materializes it in the main or mission image. An indirect entry
is rejected. Menu and cinematic are exclusive overlays and are not
resident with this function.

`endMissionCleanup` reaches the jal on a straight line. Both callers
are in `mainGameLoop`, at `0x8003E2C4` and `0x8003E388`, each with
delay `nop`. The argument is not read. `resetObjectContextPool` does
not call this function. Its three callees zero `0x8010C0A0`,
`0x8010C0C0`, and byte `0x8013A980`. `resetObjectPoolListHead` writes
`0x8010C0C0`, not `0x8010C0D0`.

## Verdict

H-NextClassComplete. The value at the jal is the partial-list head.
Every non-zero store of that word is an `rs_malloc(0x6C0, 1)` user
pointer or the `+0xC` link of such a slab, which is the same kind of
pointer. The walk frees each still-linked node once. Zero does not
reach the jal. No guard was added.

H-NextClassGap is not selected. The reached value is that allocator
return, and the other free of the same slab unlinks it first.
H-NextClassUnevaluable is not selected. One caller, the entry is not
materialized as a pointer, and the head stores named above do not
publish a second identity.

The next unaudited `jal rs_free` is the second jal in this function,
at `0x800EC564`. `$a0` is the word at `0x8010C0D4`, loaded at
`0x800EC55C`. The delay is `sw $v0, -0x3F2C($s0)` at `0x800EC568`,
which writes the full-list head and does not write `$a0`. The next
`jal rs_free` after that is `0x800EED48`.
