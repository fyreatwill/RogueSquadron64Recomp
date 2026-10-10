# M3 s4497 — preloadSceneReferencedSongs rs_free of the mark array

## Work unit

Static census of the second `jal rs_free` in `preloadSceneReferencedSongs`
(`.ovl.mission`, entry `0x800EEA54`, size `0x328`) at `0x800EED50`. ROM
bytes were used. Mission VRAM is `0x800A5130` size `0x665A0`, so this PC
is inside that overlay (`0x800EED50` < `0x8010B6D0`). The menu overlay
ends at `0x800CD520` and the cinematic overlay ends at `0x800B0940`, so
those images do not contain this instruction. No build or runtime run
was performed. The first jal at `0x800EED48` was not reclassified.

The discriminator was every original assignment of `$a0` and `$s3` from
the entry through this jal, every caller, and every callee `jal rs_free`:

- H-NextClassGap: a reached path passes a non-allocator value, or a
  pointer already freed, with the writer named.
- H-NextClassComplete: every reached path passes one allocator return,
  freed once, or no path reaches the jal.
- H-NextClassUnevaluable: more than one pointer identity can reach
  `$a0`, or a possible indirect entry cannot be accepted or rejected.

Same-scan positive control. `RecompiledFuncs/` is gitignored and not
present, so the C-file scan could not be repeated. The ROM word was
read from the image that contains each closed site. Mission bytes at
`0x800EED48`, `0x800EED50`, `0x800EC564`, `0x800EC538`, `0x800EC404`,
and `0x800C1084` are `0x0C000726`, and so is `.text` at `0x8007BE50`.
The menu image at VRAM `0x800C1084` is `addiu $a0, $zero, 0x8` and is
not the closed `handleHUD` site. A scan that missed `0x800EED48` or
`0x800EC564` would have been invalid.

## What is freed

The delay slot is the argument. It executes before `rs_free` and writes
`$a0`:

```
jal  rs_free                  # 0x800EED50
addu $a0, $s3, $zero          # 0x800EED54
```

`$s3` has one register write before that delay. The prologue
`sw $s3, 0x1C($sp)` at `0x800EEA74` saves the incoming register and
does not change it. The epilogue `lw $s3` at `0x800EED64` is after
this jal. The write that reaches the delay is:

```
addu $a0, $s4, $zero          # 0x800EEAA0  size = record count
jal  rs_malloc                # 0x800EEAA4
addu $a1, $zero, $zero        # 0x800EEAA8  flags = 0
addu $s3, $v0, $zero          # 0x800EEAAC
```

Nothing writes `$v0` between the return and `0x800EEAAC`. Removing
`0x800EEAAC` from the control-flow graph makes `0x800EED50`
unreachable from the entry. No other instruction in the function
writes `$s3`. The jal is not in a cycle: the epilogue's only exit is
`jr $ra` at `0x800EED74`.

`$s4` is the number of 6-byte records at `0x8010B1C0` before a
`0xFFFF` halfword. It starts at 0. If the first halfword is already
`0xFFFF`, `beq` at `0x800EEA80` skips the scan and the size stays 0.
Otherwise the scan starts at the next record, steps by 6, and counts
the terminator step, which equals the number of records before it.
Both exits fall through to this `rs_malloc`.

`rs_malloc` returns through `addu $v0, $s2` at `0x80001C74`. `$s2` is
set to 0 at `0x80001AE4`, or to `block + 0x10` at `0x80001C10` when a
block fits. `beqz $s0, 0x80001C74` at `0x80001AF0` is the size-0 exit:
the branch is before any later `$s2` write, so a zero size returns 0.
Flags bits `0x4` and `0x10` are both clear, so the search is the
ordinary list walk and `ensureHeapInitialized` is not called. The
caller `$s3` is saved at `0x80001AE8` and restored at `0x80001C7C`
before the only `jr`. The copy at `0x800EEAAC` is what keeps the
return value.

A zero return does not reach this jal. The next call is
`rs_memset($s3, 0, $s4)` at `0x800EEAB8`, and there is no branch
between the copy and that jal. `rs_memset` is 0x28 bytes, has no
`$s3` write and no jal. `beqz $a2, 0x80007900` at `0x800078E0`
returns immediately when the size is 0. A nonzero size stores through
`$a0`, so a null pointer faults at `0x800078EC` and does not return.
The size-0 null still does not arrive later: every path from the
entry to this jal passes `sb $v0, 0x0($v1)` at `0x800EEBBC`, where
`$v1` is `$s3 + $a0` from `0x800EEBB4`. No branch from before that
store lands after it. The equal-halfword path sets `$a0` to 0 in the
delay of `0x800EEB94` and stores to `$s3`. The search path stores at
`$s3` plus a count that starts at 0. A zero base faults. The store is
a use of the buffer, not a publish: after `0x800EEAAC` the only
memory operation on `$s3` itself is the epilogue reload.

`blez $a0, 0x800EED50` at `0x800EEBEC` reaches this jal without the
second `rs_malloc`. Its delay writes `$s0`, not `$s3` or `$a0`. That
path still passed the mark-byte store, so `$s3` is the nonzero return
from the first call. The fall-through path allocates the index buffer
into `$s2` at `0x800EEC08` and frees that pointer at `0x800EED48`
before this jal. `sh` at `0x800EEC10` is unconditional, so a zero
second return faults there and does not arrive. The taken block is
marked with halfword 2 at `0x80001C18`, and the free-list search
requires bit 0 (`0x80001BC8`), so a still-live first block is not
returned again. The two nonzero returns are different blocks.

`$s3` is preserved across every callee that runs while it is live:

- `rs_memset` does not write `$s3`.
- The second `rs_malloc` saves `$s3` at `0x80001AE8` and restores it
  at `0x80001C7C`. It does not jal `rs_free`.
- `parseLoadedSndSection` (`0x80066918`) does not write `$s3`. Its
  `$a0` is the halfword at `0x4($s0)` from the index buffer, not this
  pointer. It calls `parseSndFiles` (`0x80097518`), which saves `$s3`
  at `0x8009752C` before any write and restores it at `0x800978D0`
  before its only `jr` at `0x800978E4`. No path reaches that `jr`
  without the restore. `parseSndFiles` does not jal `rs_free`. Its
  `jalr` is inside `relocateSndPointer` at `0x80092630`; `$a0` there
  is the sound pointer just tested for a `0x80`/`0xB0` top byte, and
  `$s3` is restored after the call returns.
- `loadSongAssetByName` (`0x8006657C`) saves `$s3` at `0x80066580`
  and restores it at `0x800666C4` on the only return join,
  `0x800666BC`. Its own `$s3` is the word at `0x80138920`, the name
  pointer passed in `$a0`, not this buffer. None of its direct
  callees (`sprintf`, `get_asset_size_extra`, `rs_malloc`,
  `findAssetAcrossSegments`, `setupAssetDma`, `teardownAssetDma`)
  contains `jal rs_free`.
- `rs_free` of `$s2` does not write `$s3`. A zero argument returns
  from `beqz $s0, 0x80001F78` at `0x80001CA4`, which is not this
  path. Its jals are `osRecvMesg` (`0x800331D0`) and `osSendMesg`
  (`0x80033410`). Neither writes `$s3` and neither contains
  `jal rs_free`. A blocking receive can yield: `__osEnqueueAndYield`
  saves `$s3` with `sd $s3, 0xB0($a1)` at `0x8002BC40`, and
  `__osDispatchThread` reloads it with `ld $s3, 0xB0($k0)` at
  `0x8002BE18` before `eret`.

Earlier `$a0` writes do not survive the delay. From the entry they
are the terminator-scan copy (`0x800EEA88`), the first malloc size
(`0x800EEAA0`), the `rs_memset` destination (`0x800EEAB0`), one scene
record (`0x800EEAEC`), the name-search index (`0x800EEB98`,
`0x800EEBB0`), the cleared mark counter (`0x800EEBC0`) and its
increment (`0x800EEBD8`), the second malloc size (`0x800EEBF4`), the
init-loop bound (`0x800EEC1C`), one index slot (`0x800EEC60`), the
`parseLoadedSndSection` halfword (`0x800EECF0`), the
`loadSongAssetByName` word (`0x800EED2C`), and the other free's
`$s2` (`0x800EED4C`). The incoming `$a0` is not read.

## Who reaches the jal

The only `jal 0x800EEA54` in `.text`, `.ovl.mission`, `.ovl.menu`,
and `.ovl.cinematic` is `0x800EFB9C`, inside `preloadSceneSongsWrapper`
(`0x800EFB94`). The delay is `nop`. The only `jal 0x800EFB94` is
`0x800FA5E4`, inside `initMission` (`0x800FA250`). That delay is
`nop`. No branch in `initMission` targets the jal, and no branch
from after it targets the jal or an earlier instruction. The symbol
name is not a caller.

There is no `j` to `0x800EEA54` in those images and no raw word
`0x800EEA54` anywhere in the ROM. No `addiu`, `ori`, `andi`, or
`xori` in those images has immediate `0xEA54`. The only two such
immediates in the ROM are `xori $v1, $t5, 0xEA54` at `0x675DB8` and
`ori $a1, $s3, 0xEA54` at `0xA575F0`. Cinematic ROM ends at
`0x142D90`. Both words are outside every code image and are not an
entry. An indirect entry is rejected.

## Verdict

H-NextClassComplete. Every completed path that reaches the jal passes
the user pointer from the `rs_malloc` at `0x800EEAA4` (size = the
record count, flags 0), and this jal frees it once. A zero return
faults in `rs_memset` when the count is nonzero, or at the mark-byte
store at `0x800EEBBC` when the count is zero, and does not arrive.
The mark-count `blez` and the fall-through path free that same
pointer. The fall-through path's other free passes the distinct
index buffer. No guard was added.

H-NextClassGap is not selected. The reached value is that allocator
return, and no reached writer publishes a non-allocator or
already-freed pointer. H-NextClassUnevaluable is not selected. One
register identity reaches the delay, the entry is not materialized as
a pointer, and the `jalr` in `relocateSndPointer` does not receive
this buffer.

The next unaudited `jal rs_free` in `.ovl.mission` is
`reset_and_free_model_animations` (`0x800F9F6C`, size `0x64`) at
`0x800F9F94`. Its delay is `nop` at `0x800F9F98`, which does not
write `$a0`. That is not a classification of that jal.
