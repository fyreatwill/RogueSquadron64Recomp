# M3 s4498 — reset_and_free_model_animations rs_free of one name-table slot

## Work unit

Static census of the only `jal rs_free` in `reset_and_free_model_animations`
(`.ovl.mission`, entry `0x800F9F6C`, size `0x64`) at `0x800F9F94`. ROM
bytes were used. Mission VRAM is `0x800A5130` size `0x665A0`, so this PC
is inside that overlay (`0x800F9F94` < `0x8010B6D0`). The menu overlay
ends at `0x800CD520` and the cinematic overlay ends at `0x800B0940`, so
those images do not contain this instruction. No build or runtime run
was performed. `0x800EED50` was not reclassified.

The discriminator was every original assignment of `$a0` from the entry
through this jal, every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control. `RecompiledFuncs/` is gitignored and not
present, so the C-file scan could not be repeated. Mission ROM words at
closed `0x800EED50`, closed `0x800EED48`, and closed `0x800EC564` are
`0x0C000726`, and so is `.text` at closed `0x8007BE50`. This jal is the
same word. A scan that missed `0x800EED50` or `0x800EC564` would have
been invalid.

## What is freed

The delay is `nop` at `0x800F9F98` (word `0`). It does not write `$a0`.
The only `$a0` write from the entry to the jal is the load that feeds
the branch:

```
lw    $a0, 0x0($s0)            # 0x800F9F88
beql  $a0, $zero, 0x800F9FA0   # 0x800F9F8C
sw    $zero, 0x0($s0)          # 0x800F9F90  delay, only if taken
jal   rs_free                  # 0x800F9F94
nop                            # 0x800F9F98
sw    $zero, 0x0($s0)          # 0x800F9F9C
```

`beql` is branch-likely. A zero word executes the delay store and skips
the jal, landing on `addiu $s1, $s1, 1` at `0x800F9FA0`. A nonzero word
nullifies that delay, so the slot is still the loaded pointer when
`rs_free` runs, and `0x800F9F9C` clears it after the return. No branch
in the function targets the jal. The loop branch at `0x800F9FA8` targets
the load at `0x800F9F88`, not the jal. The incoming `$a0` is not read.
`endMissionCleanup`'s delay at `0x800FBAC8` is `nop`.

`$s0` starts at `0x8010C4A0` (`lui $v0, 0x8011` / `addiu $s0, $v0,
-0x3B60`). `$s1` starts at 0. The loop-back delay is `addiu $s0, $s0,
0x24`, which is not likely, so it executes on the exit too. `slti $v0,
$s1, 0x10` stops after 16 loads. The words are `0x8010C4A0 + i*0x24`
for `i` in `0..15`. The last is `0x8010C6BC`. The next named symbol is
`simpleCheckHandles` at `0x8010C6E0`, so the 16 records fill the gap
and do not run into it. Each iteration loads a different slot. The
clear at `0x800F9F9C` happens before `$s0` advances, so one call does
not free the same slot twice. A second call loads zeros and takes
`beql`.

## Who writes the slot word

The address `0x8010C4A0` is `lui 0x8011` plus addiu immediate `0xC4A0`.
No raw word `0x8010C4A0` exists in the ROM. The only code-image uses of
immediate `0xC4A0` that form this address are:

- `load_model_animation` at `0x800F9E60`
- `reset_model_animations` at `0x800F9F44`
- this function at `0x800F9F80`

The `.text` hit `lb $v1, -0x3B60($zero)` at `0x8009FE90` addresses
`0xFFFFC4A0`. The menu hits at `0x800AD784` and `0x800AD78C` use
`lui $v0, 0x800D`, which is `0x800CC4A0`. Neither is this table.

`reset_model_animations` stores `$zero` at all 16 words, walking
backward from `+0x21C`. It does not jal `rs_free`. Its only caller is
`initMission` at `0x800FA2CC` (delay `nop`). A zero does not reach
this jal. A live pointer dropped by that clear is a leak, not a value
this jal frees.

`load_model_animation` is the only nonzero store: `sw $a0, 0x0($s0)`
at `0x800F9EF8`, in the delay of `jal model_animation_offset_convert`.
The delay executes before the call, so the slot receives `$a0` before
the callee runs. `$a0` is `$v0` from `jal load_asset` at `0x800F9EE0`.
Nothing writes `$v0` between that return and the copy at `0x800F9EE8`.

The store runs only after the scan finds an empty slot. `$s3` records
the last index whose word was 0. A name match reloads the existing
word and jumps to the epilogue at `0x800F9E98`; it does not store and
does not allocate. If every slot is nonzero, `$s3` stays `-1` and the
function returns 0 at `0x800F9F08` without storing. The fill path
computes `index * 0x24` (`sll` 3, add the index, `sll` 2), copies the
name to `slot + 4` with `rs_strcpy`, then calls `load_asset`.

`rs_strcpy` (`0x8000761C`, size `0x24`) writes forward from `$a0` and
does not write `$s0`, `$s1`, or `$s4`. The 17 callers of
`load_model_animation` pass ASCII literals. The longest are
`imp_stuff/atst_start` and `reb_stuff/atpt_start`, 20 bytes, so the
copy is 21 bytes including the NUL. The next slot's pointer is `0x20`
bytes past the name. The copy cannot reach it, and it cannot reach
this slot's pointer because that word is before `+4`.

`load_asset` (`0x8006488C`) has no branch. It calls `rs_malloc` at
`0x800648C0` with flags `$a1 = 0`, copies `$v0` to `$s2` at
`0x800648DC`, and returns that `$s2` at `0x80064914`. Nothing writes
`$v0` between the malloc return and the copy. `findAssetAcrossSegments`,
`setupAssetDma`, and `teardownAssetDma` contain no `jal rs_free`.
Each has one `jr`, and each restores `$s2` from its stack slot with
no branch landing on or after that restore. `load_asset` itself saves
`$s0` and `$s1` and restores them before its only `jr`, so the slot
address survives.

`rs_malloc` returns through `addu $v0, $s2, $zero` at `0x80001C74`.
`$s2` is cleared at `0x80001AE4` and set to `block + 0x10` only at
`0x80001C10`. The size-0 `beqz` at `0x80001AF0` targets `0x80001C74`
with `$s2` still 0. The failure branches at `0x80001B34` and
`0x80001B9C` target `0x80001C60`, which is after `0x80001C10`, so they
also return 0. `osSendMesg` (`0x80033410`) writes `$s2` at `0x8003352C`
and reloads the saved value at `0x80033550`, immediately before its
only `jr` at `0x80033554`. The branch to `0x80033544` still passes
that reload. The user pointer therefore survives back to `load_asset`.

A zero return is stored by the same delay, then
`model_animation_offset_convert` executes `lw $v0, 0x4($a0)` at
`0x80082BD0` before any branch. A null `$a0` faults there and does
not return. The slot remains 0. This jal's `beql` would skip it if a
later call ran. `model_animation_offset_convert` contains no jal. It
adds the asset base to offsets inside the block. It does not receive
the slot address, and the slot word is already the malloc return.

## The pointer is not freed earlier

`load_model_animation`'s return is discarded by `load_dat_file_assets`
(eight calls, then `j 0x80064FC8`, and that function contains no
`jal rs_free`). The other nine calls save it into an NPC field:

| Caller | Return saved at | `jal rs_free` in that function |
|---|---|---|
| `npcAtAtUpdate` | `+0x70`, `+0x74` | `0x800CDE8C` loads `+0x4C` |
| `npcAtStUpdate` | `+0x80`, `+0x84`, `+0x88` | `0x800D0480` and `0x800D0DC0` load `+0x4C` |
| `playerAtStUpdate` | `+0x74` | `0x800D25A0` loads `+0xA4`; `0x800D25D4` loads `0xBC($s4)` |
| `npcAtPtUpdate` | `+0x88`, `+0x8C`, `+0x90` | `0x800EAAE4` loads `+0x4C` |

`npcAtPtUpdate` also stores 0 at `+0x88` in the delay of
`clearModelAnimChannelEntry` and does not free that word.
`playerAtStUpdate`'s `+0xA4` is a different pointer, stored at
`0x800D22B8` before the animation load. None of these frees pass the
saved asset.

`flattenAnimTreeAndAllocateSlot` (`0x80082B00`) receives the asset in
`$a1`, keeps it in `$s2`, and contains no `jal rs_free`. It mallocs a
separate block. `appendAnimHandleAndDescendantsToBuffer` and
`allocateModelAnimSlot` contain no `jal rs_free`. The value returned
to the NPC is that helper's result, saved at a different field
(`+0x8C` or `+0x94`), and `releaseModelAnimSlot` is called with that
field. `releaseModelAnimSlot` does not form `0x8010C4A0`. Its three
frees are the already-closed tree class, not this slot word.

A name match returns the existing slot word instead of allocating a
second one, so two slots are not given the same pointer. A new store
goes into a slot whose word was 0. `rs_malloc` cannot return an
address that another slot still holds unless that block was already
freed, and the only `jal rs_free` of a load from this table is the
one under study. It zeros the slot before the next iteration.

`rs_free` contains no nested `jal rs_free` and no `0xC4A0` immediate.
Its argument is the asset, not the slot address. The following clear
is this function's `sw $zero`.

## Who reaches the jal

The only `jal 0x800F9F6C` in `.text`, `.ovl.mission`, `.ovl.menu`,
and `.ovl.cinematic` is `0x800FBAC4`, inside `endMissionCleanup`
(`0x800FB9E4`). The delay is `nop`. No branch in that function
targets the jal. The calls before it are a straight line from the
join at `0x800FBA34`. The symbol name is not a caller. The two
callers of `endMissionCleanup` are `mainGameLoop` at `0x8003E2C4`
and `0x8003E388`. They do not supply `$a0` for this free.

There is no `j` to `0x800F9F6C` in those images and no raw word
`0x800F9F6C` anywhere in the ROM. No `addiu`, `ori`, `andi`, or
`xori` in those images has immediate `0x9F6C`. The only three such
immediates in the ROM are at `0x9C4814`, `0xEF69CC`, and `0xF9BA68`.
Code images end at ROM `0x142D90`. All three are outside every code
image and are not an entry. An indirect entry is rejected.

## Verdict

H-NextClassComplete. Every completed path that reaches the jal passes
the user pointer from one `load_asset` → `rs_malloc(..., 0)` return,
stored at one empty slot of `0x8010C4A0`, and this jal frees that
slot once. A zero word takes `beql` and does not arrive. No guard
was added.

H-NextClassGap is not selected. The reached value is that allocator
return. The zeroing writer in `reset_model_animations` does not reach
the jal, and no reached writer publishes a non-allocator or
already-freed pointer. H-NextClassUnevaluable is not selected. One
memory identity reaches `$a0`, the entry is not materialized as a
pointer, and the name copy cannot spill into the next pointer.

The next unaudited `jal rs_free` in `.ovl.mission` is
`freePlayerAuxBuffersIfActive` (`0x80100F40`, size `0x68`) at
`0x80100F84`. Its delay is `nop` at `0x80100F88`, which does not
write `$a0`. The `lw $a0, 0x8($s0)` at `0x80100F80` was seen while
naming that site. That is not a classification of that jal. The same
function has a second jal at `0x80100F90`.
