# M3 s4496 — preloadSceneReferencedSongs rs_free of the index buffer

## Work unit

Static census of the first `jal rs_free` in `preloadSceneReferencedSongs`
(`.ovl.mission`, entry `0x800EEA54`, size `0x328`) at `0x800EED48`. ROM
bytes were used. Mission VRAM is `0x800A5130` size `0x665A0`, so this PC
is inside that overlay (`0x800EED48` < `0x8010B6D0`). The menu overlay
ends at `0x800CD520` and the cinematic overlay ends at `0x800B0940`, so
those images do not contain this instruction. No build or runtime run
was performed. The second jal at `0x800EED50` was not classified.

The discriminator was every original assignment of `$a0` and `$s2` from
the entry through this jal, every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control: `funcs_40.c` still has `jal 0x80001C98` at
closed `0x800EC564`, closed `0x800EC538`, and closed `0x800EC404`.
`funcs_33.c` still has it at closed `0x800C1084`. `funcs_19.c` still
has it at closed `0x8007BE50`. The ROM word at those PCs and at
`0x800EED48` is `0x0C000726`. A scan that missed `0x800EC564` or
`0x800EC538` would have been invalid.

## What is freed

The delay slot is the argument. It executes before `rs_free` and writes
`$a0`:

```
jal  rs_free                  # 0x800EED48
addu $a0, $s2, $zero          # 0x800EED4C
```

`$s2` has one register write before that delay. The prologue
`sw $s2, 0x18($sp)` at `0x800EEA78` saves the incoming register and
does not change it. The epilogue `lw $s2` at `0x800EED68` is after
both jals. The write that reaches the delay is:

```
jal  rs_malloc                # 0x800EEBF8
addu $a1, $zero, $zero        # 0x800EEBFC  flags = 0
addiu $t0, $zero, 0x1         # 0x800EEC00
addu $s1, $zero, $zero        # 0x800EEC04
addu $s2, $v0, $zero          # 0x800EEC08
addiu $v0, $zero, -0x1        # 0x800EEC0C
sh   $v0, 0x2($s2)            # 0x800EEC10
```

Nothing writes `$v0` between the return and `0x800EEC08`. A
control-flow walk from the entry reaches `0x800EED48` only with that
assignment already executed. `blez $a0, 0x800EED50` at `0x800EEBEC`
skips both the allocation and this jal. No other branch enters the
span between the assignment and the jal. The jal is not in a cycle:
after it, the next instruction in this function is the other free.

The call happens only when the mark count in `$a0` is greater than 0.
The delay of that `blez` sets `$s0 = $a0 + 1` (at least 2), and the
not-taken path passes `$a0 = $s0 << 3` with `$a1 = 0`. The size is
therefore at least 16. `rs_malloc` returns through one instruction,
`addu $v0, $s2` at `0x80001C74`. Its `$s2` is 0, or `addiu $s2, $a1,
0x10` at `0x80001C10` after a block fits. The size-0 exit also lands
on that move, with `$s2` still 0, but this call does not take it.
Flags bits `0x4` and `0x10` are both clear, so the search is the
ordinary two-list walk. `rs_malloc` restores the caller's `$s2`
before returning; the copy at `0x800EEC08` is what keeps the return
value.

`$s2 = 0` does not reach the jal on a completed execution. The halfword
store at `0x800EEC10` is unconditional and is the next use. A zero
base faults there. `rs_free` itself also skips a zero: `addu $s0, $a0`
at `0x80001CA0`, then `beqz $s0, 0x80001F78`, which is the epilogue.
The value that completes to this jal is the user pointer from this
call.

`$s2` is not stored after `0x800EEC08`. The only `sw $s2` in the
function is the prologue save of the incoming register. Copies into
`$v1`, `$a0`, and `$s0` are bases for halfword traffic inside the
buffer. They are not published.

`parseLoadedSndSection` (`0x80066918`) and `loadSongAssetByName`
(`0x8006657C`) run while `$s2` holds the pointer. Neither is passed
that pointer. `parseLoadedSndSection` does not mention `$s2`. It calls
`parseSndFiles` (`0x80097518`), which saves `$s2` at `0x80097548`
before any write and restores it at `0x800978D4`. The only `jr $ra`
is `0x800978E4`, and no path reaches it without that restore. No path
reaches the first `$s2` write without the save. `loadSongAssetByName`
saves `$s2` at `0x800665A0` and restores it at `0x800666C8` on the
only return join, `0x800666BC`. Its own `$s2` is a table slot, not
this buffer.

Those callees do not jal `rs_free`. `parseSndFiles` calls
`factor5BucketedTableInsertEntry`, `relocateSndPointer`, and five
`factor5SortedTableInsert*` functions. None of those bodies contains
`jal rs_free`. `relocateSndPointer` has `jalr $v0` at `0x80092630`.
The target is the word at `0x801499E0`, and `$a0` is the sound pointer
just tested for a `0x80`/`0xB0` top byte. That is not this `$s2`.
`parseSndFiles` restores `$s2` after the call returns. `loadSongAssetByName`
calls `sprintf`, `get_asset_size_extra`, `rs_malloc`,
`findAssetAcrossSegments`, `setupAssetDma`, and `teardownAssetDma`.
None of those bodies contains `jal rs_free`. `rs_malloc` and
`rs_memset`, which run before this `$s2` exists, also do not.

`rs_free` does not jal itself. Its jals are `osRecvMesg`
(`0x800331D0`) and `osSendMesg` (`0x80033410`). Neither contains
`jal rs_free`.

The other free in this function passes `$s3`, not `$s2`. `$s3` is the
return of the earlier `rs_malloc` at `0x800EEAA4`, copied at
`0x800EEAAC`. No jal sits between that copy and the second allocation,
so the first block is still live when the second returns. The two
non-zero returns are different blocks. This jal frees the second one
once.

`RecompiledFuncs/funcs_40.c` agrees. `ctx->r18` is set from `ctx->r2`
at the `0x800EEC08` comment and is not assigned again until the
epilogue. The delay writes `ctx->r4` from `ctx->r18` and then calls
`rs_free`. The `blez` at `0x800EEBEC` goes to `L_800EED50`. The store
probes around the halfword writes do not write `r18`.

Earlier `$a0` writes do not survive the delay. From the entry they
are the end-marker scan copy (`0x800EEA88`), the first malloc size
(`0x800EEAA0`), the `rs_memset` destination (`0x800EEAB0`), the scene
record (`0x800EEAEC`), the name-search index (`0x800EEB98`,
`0x800EEBB0`), the mark counter (`0x800EEBC0`, `0x800EEBD8`), the
second malloc size (`0x800EEBF4`), the init-loop bound (`0x800EEC1C`),
one record address (`0x800EEC60`), the `parseLoadedSndSection`
halfword (`0x800EECF0`), and the `loadSongAssetByName` word at
`0x80138920` (`0x800EED2C`). The incoming `$a0` is not read.

## Who reaches the jal

The only `jal 0x800EEA54` in the ROM is `0x800EFB9C`, inside
`preloadSceneSongsWrapper` (`0x800EFB94`). The delay is `nop`. The
only `jal 0x800EFB94` is `0x800FA5E4`, inside `initMission`
(`0x800FA250`). That delay is `nop`, and no branch in `initMission`
targets the jal or jumps backward onto it. The symbol name is not a
caller.

There is no `j` to `0x800EEA54` and no raw word `0x800EEA54` in the
ROM. The only `addiu`/`ori` with immediate `0xEA54` is `ori $a1, $s3,
0xEA54` at ROM `0xA575F0`. Mission ROM ends at `0x10C2D0`, menu at
`0x1346C0`, and cinematic at `0x142D90`. That word is outside every
code image and is not an entry. An indirect entry is rejected.

## Verdict

H-NextClassComplete. Every completed path that reaches the jal passes
the user pointer from the `rs_malloc` at `0x800EEBF8` (size
`(marks + 1) << 3`, flags 0), and this jal frees it once. A zero
return faults at `0x800EEC10` and does not arrive. The mark-count
`blez` skips the jal instead of freeing another value. No guard was
added.

H-NextClassGap is not selected. The reached value is that allocator
return, and no reached writer publishes a non-allocator or
already-freed pointer. H-NextClassUnevaluable is not selected. One
register identity reaches the delay, the entry is not materialized as
a pointer, and the `jalr` in `relocateSndPointer` does not receive
this buffer.

The next unaudited `jal rs_free` is the second one in this function,
at `0x800EED50`. Its delay is `addu $a0, $s3, $zero` at `0x800EED54`,
which writes `$a0`. The `$s3` write observed while classifying this
site is `addu $s3, $v0` at `0x800EEAAC`, after `jal rs_malloc` at
`0x800EEAA4`. The `blez` at `0x800EEBEC` also targets `0x800EED50`.
That is not a classification of the second jal.
