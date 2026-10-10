# M3 s4499 — freePlayerAuxBuffersIfActive rs_free of the slot +8 array

## Work unit

Static census of the first `jal rs_free` in `freePlayerAuxBuffersIfActive`
(`.ovl.mission`, entry `0x80100F40`, size `0x68`) at `0x80100F84`. ROM
bytes were used. Mission VRAM runs `0x800A5130` through `0x8010B6D0`,
so this PC is in that overlay. The menu overlay ends at `0x800CD520`
and the cinematic overlay ends at `0x800B0940`. No build or runtime
run was performed. `0x800F9F94` was not reclassified. The second jal
in this function, at `0x80100F90`, was not classified.

The discriminator was every original assignment of `$a0` from the entry
through this jal, every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control. `RecompiledFuncs/` is not on disk, so the
C-file scan could not be repeated. Mission ROM words at closed
`0x800F9F94`, closed `0x800EED50`, and closed `0x800EC564` are
`0x0C000726`, and so is `.text` at closed `0x8007BE50`. This jal is
the same word. A scan that missed `0x800F9F94` or `0x800EC564` would
have been invalid.

## What is freed

The delay is `nop` at `0x80100F88` (word 0). It does not write `$a0`.
From the entry, `$a0` is written twice before the jal:

```
andi  $a0, $a0, 0xFF           # 0x80100F4C  index
...
lw    $v0, 0x4($s0)            # 0x80100F68  count object
lbu   $v0, 0x0($v0)            # 0x80100F6C
beqz  $v0, 0x80100F98          # 0x80100F70  skips both frees
nop
jal   despawnCraftAnimationSlotNpcs
nop
lw    $a0, 0x8($s0)            # 0x80100F80  the value freed
jal   rs_free                  # 0x80100F84
nop                            # 0x80100F88
```

`$s0` is `0x8010CF20 + (index & 0xFF) * 0x18`
(`lui $v1, 0x8011` / `addiu $v1, $v1, -0x30E0`, then
`(index * 3) << 3`). The `andi` is overwritten by the load. No branch
in the function targets the jal. The `beqz` is not likely, and its
delay is `nop`, so a zero count skips the jal and the one at
`0x80100F90`.

Every caller passes index 0. The nine `jal 0x80100F40` sites are all
in `.ovl.mission`, and each delay is `addu $a0, $zero, $zero`:

| Caller | jal |
|---|---|
| `playerSnowSpeederUpdate` | `0x800AD184` |
| `playerXwingUpdate` | `0x800B56E0` |
| `playerAwingUpdate` | `0x800B742C` |
| `playerYwingUpdate` | `0x800B8764` |
| `playerVwingUpdate` | `0x800BA244` |
| `playerFalconUpdate` | `0x800BBAF4` |
| `playerTieInterceptorUpdate` | `0x800BCAD4` |
| `playerT16Update` | `0x800BD7F4` |
| `playerNabooStarfighterUpdate` | `0x800BEA80` |

Index 0 selects one word, `0x8010CF28`. There is no raw word
`0x80100F40`, no `j` to it, and no code-image immediate `0x0F40`.
The symbol name is not a caller.

## Who writes 0x8010CF28

The only `sw` of that word is `allocateCraftAnimationStateForSlot`
(`0x801007C0`) at `0x80100828`, `sw $v0, 0x8($s0)`, immediately after
`jal rs_malloc`. `$s0` there is the same `0x8010CF20 + index * 0x18`.
Every caller of allocate passes `$a1 = 0` (the index) and is one of
the nine craft mode-1 blocks. The nine jals are the only
`jal 0x801007C0` in `.text` and `.ovl.mission`.

`$a2` is a static count object. Its first byte is the count, and the
malloc size is that byte shifted left by 1. `$a1` of `rs_malloc` is 0.
The bytes are image constants: xwing `0x801097BC` = 8, awing
`0x8010986C` = 6, ywing `0x801098DC` = 2, vwing `0x8010996C` = 4,
t16 `0x80109A40` = 4, naboo `0x80109AAC` = 4, snow `0x8010964C` = 0,
falcon `0x80109990` = 0, tie `0x801099BC` = 0. The only store whose
immediate collides with one of those low halves is `sw $a0, -0x6644($at)`
at `0x8008F6A4`, and the `lui` before it is `0x8015`, so the address
is `0x801499BC`, not the tie object.

Allocate stores the count object at slot +4 before testing the byte.
A zero count branches to `0x80100924` and does not execute the `sw`
at `0x80100828`. Free then loads that same byte and takes `beqz`, so
snow, falcon, and tie do not reach this jal.

`rs_malloc` returns through `addu $v0, $s2, $zero` at `0x80001C74`.
`$s2` is cleared at `0x80001AE4` and set to `block + 0x10` only at
`0x80001C10`. The size-0 `beqz` at `0x80001AF0` and the failure
branches at `0x80001B34` and `0x80001B9C` target `0x80001C60`, which
is after `0x80001C10` but those branches are taken before that
write, so they return 0. `$s2` is restored at `0x80001C80` only after
`$v0` has been written. Nothing writes `$v0` between the malloc
return and the `sw` at `0x80100828`.

A zero return is stored by that same `sw`. The fill loop then does
`lw $v1, 0x8($v1)` at `0x80100894` and `sh` through it at
`0x801008A0`. A null pointer faults there. Allocate does not return,
so 0 does not survive to a later free.

The other functions that form `0x8010CF20` do not store offset 8.
`despawnCraftAnimationSlotNpcs` and
`despawnCraftAnimationSlotNpcsAndMarkStopping` write a halfword
through the pointer and a byte at slot +0x10. `tickCraftAnimationSlot`
writes bytes at +0x10..+0x14 and halfwords through the pointer.
`resetCraftAnimationStateForSlot` clears +0x10..+0x13.
`setCraftAnimationSlotParams` writes +0x12 and +0x14. Free and the
two getters do not store the slot. The `.text` immediate `0xCF20` at
`0x80072DC8` is `addiu` after `lui $s1, 0x8004`, which is
`0x8003CF20`, not this table.

The `swc1` pair at `0x8010091C` / `0x80100920` uses base `0x8010CF38`
and offsets `0xF4` / `0xF8`, which are slot 11's +4 and +8. Index 0
does not alias them.

## The pointer is not freed earlier

`despawnCraftAnimationSlotNpcs` (`0x80100594`) runs after the count
check and before this jal. It reloads slot +8, treats it as an array
of halfword NPC indices, and `jal destroyNpcSlotByIndex` on each
index that is not `0xFFFF`. It then stores `0xFFFF` into that
halfword. It contains no `jal rs_free` and no `sw` of slot +8.

That destroy cannot re-enter this jal on the craft that is already
inside mode 2. `destroyNpcSlotByIndex` increments byte +0x1A before
its `jalr` and decrements it on the way out. A nested destroy sees
+0x1A nonzero and returns without calling the handler. The halfwords
are other NPCs' directory indices. Those handlers are not the nine
callers of this function.

The `jal rs_free` of `0xBC($s1)` inside the craft teardown blocks
loads a different pointer. It is not this word.

## Who reaches the jal

Mode 2 is the only `jalr` whose `$a1` is the immediate 2:
`destroyNpcSlotByIndex` at `0x8003EDE0`, delay `addu $a2, $zero, $zero`,
with `addiu $a1, $zero, 2` at `0x8003EDDC`. `slotDispatcherIter`
forwards its own `$a1`. Of its 127 direct callers in `.text` and
`.ovl.mission`, none pass 2. The one backward walk that stopped on a
`j` is `dealDamagetoDatItem` at `0x800C7450`. The branch into that
block is a non-likely `beqz` at `0x800C7414` whose delay is
`addiu $a1, $zero, 0xB`, so that call is mode `0xB`.

Each of xwing, awing, ywing, vwing, t16, and naboo has a 12-word
mode table indexed by `mode - 1`. Table index 1 is the only entry
within `0x90` bytes before this function's jal, and the instruction
before that block is `j` to the epilogue with delay
`addiu $v0, $zero, 1`, so the previous mode does not fall through.
Snow, falcon, and tie call the function too, but their count byte is
0, so `beqz` skips the jal.

`choosePlayerCraftAssets` (`0x800FB6C0`) is called once, from
`initMission` at `0x800FA5B4`. Its loop counter `$s1` is set to 0 and
incremented to 1 before `blez`, so the body runs once and spawns one
handler from the craft table at `0x8010B3C4`. The other
`spawnNpcOfType` calls in that function pass `0x800D2208` and
`0x800C68A0`, which are not these nine handlers. `spawnNpcOfType`
then calls `slotDispatcherIter` with `$a1 = 1`, which is the alloc
mode, not mode 2.

`mainGameLoop` calls `initMission` at `0x8003E2B4` and `0x8003E378`,
on opposite sides of the `beqz` at `0x8003E25C`. Each arm then calls
`endMissionCleanup`. That function does not jal this free and does
not jal `destroyNpcSlotByIndex`. It does jal `destroyNpcContextArrays`,
which calls `destroyTransientNpcSlots` while the free-stack count is
below `0xBF`. That walker loads the halfword at directory +0xE and
returns immediately when it is `0xFFFF`. `initNpcSlotList` writes
`0xFFFF` there at `0x8003E5DC`, after a store of 0 to the same
halfword. No later `sh` of offset `0xE` in `.text` or `.ovl.mission`
is in the window after a load of the directory pointer at
`0x80130BB0`. The refill loop does not destroy a craft.

`destroyNpcSlotByIndex` does not store 0 through the directory slot.
A second destroy of the same index would `jalr` mode 2 again, and
this function would load the same word, because nothing clears slot
+8 or the count byte. No caller found by this census issues that
second destroy. The two readers of the saved craft index at
`0x80137DB8 + 0x292` (`spawnTexturedExplosionBurst`,
`applyNpcPositionDrift`) pass it to `getNpcContextByIndex`, not to
destroy.

## Verdict

H-NextClassComplete. A zero count does not reach the jal. A nonzero
count reaches it with the user pointer from one
`rs_malloc(count << 1, 0)` return, stored at `0x8010CF28`, and that
call frees it once. No guard was added.

H-NextClassGap is not selected. The reached value is that allocator
return. The uncleared directory slot would matter only if a second
destroy of the same craft index were in the call graph. The
mission-end walker does not destroy one, and each mode-2 block calls
this function once. H-NextClassUnevaluable is not selected. One
memory identity reaches `$a0`, and the entry is not materialized as
a pointer.

The next unaudited `jal rs_free` is the other one in this function,
at `0x80100F90`. Its delay is `nop` at `0x80100F94`. The
`lw $a0, 0xC($s0)` at `0x80100F8C` was seen while reading this
function. That is not a classification of that jal. A scan from
`0x80100F94` to the end of `.ovl.mission` found no later
`jal rs_free`.
