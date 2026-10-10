# M3 s4492 — unlinkAndFreeChildNpcNode rs_free of the object slab

## Work unit

Static census of `unlinkAndFreeChildNpcNode` (`.ovl.mission`, entry
`0x800EC388`, size `0x150`) at its only `jal rs_free`, `0x800EC404`.
ROM bytes were used. `0x800EC404` is past the menu overlay end
(`0x800CD520`) and the cinematic overlay end (`0x800B0940`), so those
overlays do not contain this instruction. No build or runtime run was
performed. `handleHUD` (closed s4491) and the mission frees from
`0x800CABB0` through `0x800EAAE4` (s3617–s3620) were not re-audited.
s1814 renamed this function; that note is not a classification.

The discriminator was every original assignment of `$a0` from the
prologue through the free, every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control: `funcs_20.c` still has `jal 0x80001C98` at
closed `0x80083C58`. `funcs_19.c` still has it at closed `0x8007BE50`.
`funcs_33.c` still has it at closed `0x800C1084`. `funcs_40.c` has it
at `0x800EC404`. The ROM word at all four PCs is `0x0C000726`. A scan
that missed `0x800C1084` or `0x8007BE50` would have been invalid.

## What is freed

ROM and `RecompiledFuncs/funcs_40.c` agree. The prologue copies the
incoming argument to `$a2` and then replaces `$a0`:

```
addu $a2, $a0, $zero          # 0x800EC38C
lw   $a0, 0x0($a2)            # 0x800EC394  slab pointer
lbu  $a3, 0x4($a2)            # slot count recorded on the object
lbu  $a1, 0x0($a0)            # slab free-slot count
addu $v1, $a1, $a3
bne  $v1, $v0, 0x800EC414     # v0 is 4; other arm does not free
```

Nothing between `0x800EC394` and the jal writes `$a0`. That path has
no `jal` before `rs_free`. The delay at `0x800EC408` is `nop`. The
instruction before the jal, `sw $v0, 0($a1)` at `0x800EC400`, updates
a list head and does not write `$a0`. The other arm
(`free count + slot count != 4`) returns slots to the slab and does
not reach `0x800EC404`.

`$a0` at the jal is the word at offset 0 of the incoming object. The
only store of that word is `sw $a1, 0($v0)` at `0x800EC364` in
`allocObjectPoolNode` (`0x800EC110`). `$a1` there is the current slab,
and `$v0` is `slab + 0x10 + index * 0x1AC`. The same block stores the
slot count at object `+0x4` and the start index at object `+0x5`.

Each slab is one `rs_malloc(0x6C0, 1)` return. The call sites are
`0x800EC138` (empty partial list) and `0x800EC258` (no slab has a
fitting run). Both pass `$a1 = 1`. Inside `rs_malloc`, bits `0x4` and
`0x10` of the flags are the only flag tests; bit `0x1` selects neither.
The return is still `addu $v0, $s2` after `addiu $s2, $a1, 0x10`, the
user pointer. A NULL return from the first call returns 0 from
`allocObjectPoolNode` before a slab is published. Header layout of the
`0x6C0` block:

- byte 0: free-slot count, initially 4
- bytes 1..4: per-slot free flags
- `+0x8` / `+0xC`: previous / next slab
- four objects at `+0x10 + i * 0x1AC`

`0x10 + 4 * 0x1AC = 0x6C0`. The index scale at `0x800EC2D4` is
`index * 0x1AC + 0x10`. The slot count is
`ceil(size / 0x1AC)` via the multiply by `0x4C8F8D29`.

`createAndInitObject` (`0x800EC588`) is the only `jal 0x800EC110`.
It passes `a1 + 0x1AC` as the size. On success it stores the object
at `0($s1)`, and `$s1` is its incoming `$a0`. It does not store to
offset 0 of the object. Its optional callback receives the template
(`$a2`), not the object. All twenty callbacks were scanned across
their full symbol ranges: none stores through offset 0 of a non-`$sp`
base, and none contains `jal rs_free`.

Eighteen callers pass `a1 = 0`, which is one slot. `npcGroundTransportUpdate`
passes `0x80` and `npcTrainCarUpdate` passes `0xE0`; both are two
slots. The count is the byte at object `+0x4`, so the free condition
still fires only when this object owns every slot that is not already
free. That is the call that empties the slab.

## Who reaches the jal

The only `jal 0x800EC388` in the ROM is `0x800EC6A4`, inside
`clearPendingAndDestroyChildNpc` (`0x800EC684`). There is no `j` to
the entry, no raw word `0x800EC388`, and no `lui`/`addiu` pair that
materializes it. An indirect entry is rejected.

`clearPendingAndDestroyChildNpc` reloads `0($s0)` after
`clearPendingChildNpc` and passes that word to this function. The
reload is `lw $a0, 0($s0)` at `0x800EC6A0`. Its delay is `nop`.
`clearPendingChildNpc` (`0x800F2A24`) adds `0x114` to its argument,
has no `jal rs_free`, and has no store through offset 0.

Every one of the twenty `jal 0x800EC684` sites sets `$a0` in the
delay slot to the same `addiu $a0, $sN, imm` that the paired
`jal createAndInitObject` in that function used. The saved register
is not written between the two calls. The pairs are:

| Function | Create | Clear | Slot |
|---|---|---|---|
| `npcPowerGeneratorUpdate` | `0x80077F74` | `0x80078094` | `$s2+0x6C` |
| `npcWordDevastatorUpdate` | `0x8007F1F0` | `0x8007F41C` | `$s3+0x38` |
| `attachedAudioVisualEmitterNpcHandler` | `0x80080304` | `0x800803CC` | `$s2+0x38` |
| `npcShieldGeneratorUpdate` | `0x800814B0` | `0x800815E0` | `$s2+0x34` |
| `npcTurretUpdate` | `0x800C9374` | `0x800C93CC` | `$s1+0x38` |
| `runModelViewerSoundDemo` | `0x800CADF4` | `0x800CAF78` | `$s1+0x38` |
| `npcAtAtUpdate` | `0x800CDBC4` | `0x800CDEE4` | `$s1+0x38` |
| `npcAtStUpdate` | `0x800D02BC` | `0x800D0504` | `$s2+0x38` |
| `npcShuttleUpdate` | `0x800D3C30` | `0x800D3E54` | `$s1+0x38` |
| `npcDebrisFieldUpdate` | `0x800D54BC` | `0x800D565C` | `$s1+0x38` |
| `npcTankDroidUpdate` | `0x800D6C30` | `0x800D6D54` | `$s1+0x38` |
| `npcWingmanUpdate` | `0x800D95DC` | `0x800D987C` | `$s0+0x38` |
| `npcTieVariantUpdate` | `0x800DB438` | `0x800DB768` | `$s1+0x38` |
| `npcRadarDishUpdate` | `0x800DC9A8` | `0x800DCA0C` | `$s1+0x38` |
| `npcGroundTransportUpdate` | `0x800DEBAC` | `0x800DEE80` | `$s1+0x38` |
| `npcTrainCarUpdate` | `0x800E2BFC` | `0x800E2E70` | `$s2+0x38` |
| `npcWaterCraftUpdate` | `0x800E6548` | `0x800E67C0` | `$s3+0x38` |
| `npcGroundTroopUpdate` | `0x800E7C78` | `0x800E802C` | `$s1+0x38` |
| `tickCraftWithPhasedDestruction` | `0x800E911C` | `0x800E9434` | `$s1+0x38` |
| `npcAtPtUpdate` | `0x800EA958` | `0x800EAB18` | `$s1+0x38` |

Between each pair, loads of that slot are passed to
`initActorRenderDescriptorIfUninit`, `initActorAsType1`,
`initActorAsType2`, `initActorAsType3`, `initActorAsType4`,
`setType1ActorField40`, `setType1ActorVelocity`,
`setType2ActorVelocity`, `setType3ActorParams`,
`updateObjectFlags110`, `resetType1FxFields`,
`updateType1AnimRamp`, `getNpcCurrentHealth`, and
`clearPendingChildNpc`. None of those contains `jal rs_free`.
The offset-0 stores inside them are counters at object `+0x19C` /
`+0x1A0`, or loads of a different argument, not stores to the
object's own word 0.

On the emptying path the slab is unlinked from `0x8010C0D0` (partial,
free count nonzero) or `0x8010C0D4` (full, free count zero) before
`rs_free`. `freeAllObjectContextPoolNodes` walks those same heads and
frees slabs that are still linked. A slab removed here is not still
linked, so that walk does not free it again. The partial arm does not
call `rs_free` at all. This function has one jal and no loop around it.

## Verdict

H-NextClassComplete. The value at the jal is the slab base stored at
object `+0` by `allocObjectPoolNode`, which is one
`rs_malloc(0x6C0, 1)` user pointer, freed once when this object
empties the slab. No guard was added.

H-NextClassGap is not selected: the reached value is that allocator
return, and this path unlinks the slab before freeing it.
H-NextClassUnevaluable is not selected. The only direct caller is
`clearPendingAndDestroyChildNpc`, the entry is not materialized as a
pointer, and object `+0` is not rewritten by `createAndInitObject`,
its twenty callbacks, or the callees that receive the object before
the clear.

The next unaudited `jal rs_free` is `freeAllObjectContextPoolNodes`
at `0x800EC538` (entry `0x800EC514`). The delay is
`sw $v0, -0x3F30($s0)`, which does not write `$a0`. The jal at
`0x800EC564` is a separate site in the same function.
