# s5775 — what makes stepObjectOrientationTowardTarget return 2

Static trace of retail `build/rogue_squadron.z64`. Mission overlay ROM `0xA5D30`,
VRAM `0x800A5130`. Function `stepObjectOrientationTowardTarget` is `0x800FEF10`,
size `0xEF0`. Disassembled with `mips64-elf-objdump -m mips:4000`. No run.

## The return

There is one `jr ra`, at `0x800FFDF8`. The value is `addu v0, t3, zero` at
`0x800FFDF4`. `t3` was loaded by `lbu t3, 1175(sp)` at `0x800FFDB4`.
`1175 = 0x497`. Nothing else writes `v0` between that load and the jump.

`0x800FFCF8` is not the return. It is `addiu v0, zero, 2` and the next
instruction compares `t2` to it. `t2` is the same stack byte, loaded at
`0x800FFCE8`.

Three instructions store that byte. Nothing else does: no halfword or word
covers offset 1175, and no `addiu` takes its address.

| PC | Store | Effect |
|---|---|---|
| `0x800FEF70` | `sb zero` | Delay slot of `bc1t 0x800FFDB4` when argument `a1` is 0. Returns 0. |
| `0x800FF6F0` | `sb t3` | The only store of 2. |
| `0x800FFA40` | `sb` of 1 | The return-1 path. The store-2 path jumps to `0x800FFC30` and skips it. |

Both entries to `0x800FF6F0` set `t3` with `addiu t3, zero, 2` (`0x800FF6B8`
on the byte0==1 branch, `0x800FF6DC` on the byte0==0 fall-through). `t3` is
not written again before the store.

The caller in `updatePlayerCraftPhysics` (`0x800B2910` jal, then `andi` of
`v0`) branches on the low byte: 1 goes to `0x800B2938`, 2 goes to `0x800B2D2C`.
`0x800B2D2C` is the arm that reaches jal `0x800B2EC4`
(`spawnSceneDebrisAndEffectCluster`). Anything else jumps to `0x800B2F1C`.

## The compare

A jump table at `0x800A9450` is indexed by the selected record's byte at +1:

| Index | Target | Stores 2? |
|---|---|---|
| 0 | `0x800FF610` | yes, this block |
| 1 | `0x800FF520` | no |
| 2 | `0x800FF598` | no |
| 3 | `0x800FF47C` | no |
| 4 | `0x800FF4C8` | no |
| 5 | `0x800FF610` | yes, same block as 0 |

`0x800FF610` picks the record at `sp+0x198 + bestIndex*44` and reads the vec3
at record+0x10:

- `f22 = asin(dot(object+0x1C, that vec3)) * 57.295776`
- `f26 = acos(dot(object+0x10, that vec3)) * 57.295776`

The shipped names are `sinfApprox` (`0x8001C400`) and `constMinusSinfApprox`
(`0x8001C5CC`). The constants say otherwise. `sinfApprox` clamps the input to
about ±1 and returns ±pi/2 at the ends (`0x80000810` = 0.999999,
`0x80000814` = pi/2), and its polynomial starts with 1/6
(`0x80000838`). That is asin. `constMinusSinfApprox` is `pi/2 - asin`
(`0x80000850` = pi/2), which is acos. The scale at `0x800A9480` is 180/pi,
so both results are degrees.

Then:

- `abs(f22) < 15` (`0x800A9484`). False goes to `0x800FF748` and does not store 2.
- `f26 < 90` (`0x800A9488`). False goes to `0x800FF738` and does not store 2.
- record byte0 == 1: store 2.
- record byte0 == 0: store 2 only when the float at record+0x24 is not < 0.7
  (`0x800A948C`). If it is < 0.7, go to `0x800FF748`.
- any other byte0: go to `0x800FF738`.

The store-2 path also copies record+4/+8/+12 onto object+4/+8/+12 and writes
zero to object+0x28, +0x2C, +0x30, and +0xE8, then joins the shared tail.

## Where the record bytes come from

Up to six 44-byte records are packed at `sp+0x198`. The one with the smallest
float at +0x1C wins (index kept at `sp+0x488`). Two fills share that array.

Fill A (`0x800FF1BC`, index `s4` = 0..5) walks the halfword list at
`0x8011B4EC` through `findActiveNpcInSlotChain`, `getNpcContextByIndex`, and
`findSegmentObjectSphereHit`. A hit commits byte0 = 0 and byte1 = `s4`.

Fill B (`0x800FF398`, its own `s4` = 0..5) calls `sampleTerrainAtNpcPosition`
(`0x80068D5C`) with `a2 = 0x80138058`. A nonzero return commits byte0 = 1 and
byte1 = `s4`, packed after fill A's records.

So byte0 == 1 is a terrain sample and byte0 == 0 is an NPC sphere hit. Either
can carry byte1 0 or 5, and both then take the angle test above. Slots 1..4
do not store 2.

object+0x04 is the position vec3. The caller reads +4 and +12 as the x/z
arguments of `isTerrainCellBlockedAtWorldXz` (`0x800698F4`) with that same
`0x80138058` pointer, and the store-2 path overwrites +4/+8/+12 from the
record. object+0x10 and object+0x1C are the next two vec3s. This trace does
not name them forward or up.

## Runtime (s5776)

One level-select death run, `scratch/agent/m6/s5775_ret2/run.log` (hold 422 s,
0 crashes, 0 stalls). Controls: `[livesctl] mission`, lives 3->2, and
`[orient-ret] kind=ret1` n=1..8 about 33 s before the first death. The
return-1 store did not reach n=500.

The store at `0x800FF6F0` fired three times, all on the player object, and
each was the immediately preceding line of a `site=0x800B2EC4` debris call
(same millisecond):

| ord | byte0 | byte1 | v | idx | f24 | object |
|---|---|---|---|---|---|---|
| 14 | 1 | 5 | 2 | 0 | 0 | 0x80137DBC |
| 20 | 1 | 5 | 2 | 0 | ~-3.09e-39 | 0x80137DBC |
| 26 | 1 | 5 | 2 | 0 | ~-3.09e-39 | 0x80137DBC |

byte0=1 is the terrain fill. byte1=5 is a jump-table slot that stores 2.
idx=0 is the packed winner at sp+0x488, not the probe slot. f24 is unused on
this arm (the 0.7 test is byte0=0 only). No byte0=0 hit occurred, and the
other-object cap (16) never tripped, so the log is the full set of stores.
A later player debris call at `0x800B0D9C` (ord 33) had no ret2 in front of
it. That spline caller stays untraced. No mitigation was added.

## Not claimed

Whether the terrain normal is a real impact or a degenerate sample is not
measured. The angles `f22`/`f26` are still live at the store on the byte0=1
path (`0x800FF65C` / `0x800FF670`, no jal before `0x800FF6F0`) and were not
logged.
