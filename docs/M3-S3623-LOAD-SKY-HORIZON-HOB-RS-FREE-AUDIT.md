# M3 s3623 — loadSkyHorizonHob stack-scratch rs_free

## Work unit

Static census of `loadSkyHorizonHob` `jal rs_free` at
`0x8005B350` (`$a0 = 0x84($sp)`) and `0x8005B364`
(`$a0 = 0x0($s0)` walking the 16-word array at `$sp+0x10`).
Enumerated every original load/store of those two scratch
words and every `jal rs_free` that can receive them.
Classified each pointer's writer and whether a free can run
on a non-allocator or already-freed value. No build or
runtime run was performed.

The discriminator was the single complete original census of
those two `jal rs_free` sites plus every original `lw`/`sw` of
`0x84($sp)` and the `$sp+0x10` 16-word array inside
`loadSkyHorizonHob`, and every `jal rs_free` that can receive
them:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: cinematicSplineWalkerNpcHandler
nested 0xF00/0x2B44, leftover spawn `+0x6C`, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor `+0x4C`, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table, loadCharTextureSet
DMA-array, load_asset-then-free, texture-scratch `rs_free`,
text-texture `rs_free`, format-message `rs_free`, speech-file
`rs_free`, speech/cache `rs_free`, destructor skipped-NULL,
destructor unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_13.c`: 7 sites. Two are
this class (`0x8005B350`, `0x8005B364`). The other five are
`cinematicSplineWalkerNpcHandler` `0x8005C35C`/`0x8005C368`
(closed s3622), `freeEffectAssetBuffers`
`0x8005EBB4`/`0x8005EBC4` (globals `0x8013961C`/`0x80139740`),
and `loadExplosionTextures` `0x80061254`. None of those five
loads `0x84($sp)` or `0x0($s0)` of this callee frame.

`loadSkyHorizonHob` is `0x8005AB34`..`0x8005B3A4`, frame
`-0xE0`. One generated caller: `cinematicSplineWalkerNpcHandler`
`jal 0x8005AB34` at `0x8005BE28` with `$a0 = $s2` (the 0xF14
body). Single `jr $ra` at `0x8005B3A0`.

Original `0x84($sp)` word accesses in this PC range: 4. Other
`funcs_13.c` `0x84($sp)` hits are later functions' frames
(`swc1`/`sw`/`lwc1`/`sh` at `0x8005C434` and after).

Original `$sp+0x10` 16-word array accesses use `$s0`/`$fp`/
`0x9C($sp)` as the base; there is no direct `0x10($sp)`..
`0x4C($sp)` displacement in this function.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| init loop | `0x8005ABDC`/`0x8005ABE4` | `jal rs_malloc((0xC($s6)<<1), 0)`; `sw $v0, 0x0($s0)` | `$sp+0x10` slot `$s3` | only heap-pointer writer |
| fill | `0x8005ADE0`/`0x8005ADF0` | `lw` slot `$s0` (0..7) via `$fp` | same array | consumer; `sh` into the buffer |
| fill | `0x8005AE34`/`0x8005AE8C` | `lw` slot `$s0+8` via `$fp` | same array | consumer; `sh` into the buffer |
| packed malloc | `0x8005AEF4`/`0x8005AEFC` | `jal rs_malloc($s4&0xFFFF, 0)`; `sw $v0, 0x84($sp)` | `0x84($sp)` | only heap-pointer writer |
| packed memcpy | `0x8005AF00`/`0x8005AF34` | `zmemcpy(0x84, 0x8($s6), size)` | `0x84($sp)` | dest, not a store of the word |
| work loop | `0x8005B00C`/`0x8005B0E8` | `lw $t6, 0x84($sp)` | `0x84($sp)` | base + halfword offset |
| work loop | `0x8005B008`/`0x8005B0E4` | `lw` current `$sp+0x10` slot via `0x9C($sp)` | same array | consumer |
| epilogue | `0x8005B34C`/`0x8005B350` | `lw`/`jal rs_free` `0x84($sp)` | packed buffer | destructor |
| epilogue | `0x8005B35C`/`0x8005B364` | `lw`/`jal rs_free` `0x0($s0)` 16 times | `$sp+0x10` array | destructor |

## Object identity

`$s3 = 0` at `0x8005ABAC`. `$s1 = $sp+0x50` (16 halfword
counts). Delay-slot `$s0 = $sp+0x10`. Loop `L_8005ABD0` runs
16 times (`addiu $s3, 1` then `slti $s3, 0x10`): `$a1 = 0`,
`$a0 = 0xC($s6) << 1`, `rs_malloc`, `sw $v0, 0x0($s0)`,
`sh $zero, 0x0($s1)`, `$s0 += 4`, `$s1 += 2`. `$s6` is
`0x20(0x10(0x10(getHobObjectByName)))` from `0x80($sp)`.

After the alloc loop `$s0` is reused as a scalar counter.
`$fp` is reset to `$sp+0x10` at `0x8005ACE0` for the fill.
Fill loads `array[s0]` and `array[s0+8]` (`$s0 = atan2 & 7`)
and `sh`s packed offsets into those buffers. It does not
`sw` a new pointer into the array. `$s5 = $sp+0x50` holds
the matching halfword counts.

`L_8005AC9C` always runs. `0xC($s6)==0` skips the fill to
`L_8005AEEC` with `$s4 = 0`. The fill otherwise accumulates
`$s4` from `(word>>22)&0xFC`. `L_8005AEEC` always
`rs_malloc`s `$s4 & 0xFFFF` with `$a1 = 0` into `0x84($sp)`,
`zmemcpy`s `0x8($s6)` into that buffer, then the 16-iter
`L_8005AF54` work loop. `0x9C($sp)` walks `$sp+0x10` by 4
per iter as a consumer. Work-loop `sw` through `$s1` writes
packed-record contents at `0x84 + offset`, not the scratch
word.

`$s4` / `$s5` after `L_8005AEEC` are the caller 0xF14 body
(`0xE0($sp)`). Stores to `+0x1C`/`+0x20`/`+0x28`/`+0x3C`/
`+0x40`/`+0x5DC`..`+0x5E8` are that body, not the scratch
pointers. Level-config words at `0x88($sp)`/`0x8C($sp)` are
or-masked packed ints, not heap pointers.

## Matching allocators

The only original heap-pointer writer of `$sp+0x10[i]` is
the 16-iter `rs_malloc((0xC($s6)<<1), 0)` at `0x8005ABDC`.
The only original heap-pointer writer of `0x84($sp)` is
`rs_malloc($s4&0xFFFF, 0)` at `0x8005AEF4`. Both `$a1 = 0`.

No other `jal rs_free` receives either pointer. The five
sibling `funcs_13.c` frees are the closed spline-walker
pair or the `0x8014xxxx` effect-buffer globals /
`loadExplosionTextures`.

`rs_free` itself `beq $s0, $zero` at `0x80001CA4` and
returns, so a NULL `$a0` is a skip, not a Gap. The epilogue
has no local NULL skip; a failed malloc stores 0.

## Sequential double-free

The epilogue frees `0x84($sp)` once, then each of the 16
`$sp+0x10` slots once, then returns and the frame is dead.
It does not NULL the scratch words. There is no second
generated `jal rs_free` of either word. A size-0
`0xC($s6)` path still allocates 16 (zero-size) slots and a
zero-size packed buffer, then frees them; that is still the
matching destructor, not a second pointer source.

## Verdict

H-NextClassComplete. The two epilogue frees are the
destructor of the matching `loadSkyHorizonHob` stores:
`0x84($sp)` is the packed `rs_malloc($s4&0xFFFF)` copy,
`$sp+0x10[i]` is `rs_malloc((0xC($s6)<<1))`. H-NextClassGap
is refuted at static scope: no free of a non-allocator or
already-freed value. H-NextClassUnevaluable is not selected:
both words have a single original heap-pointer writer on this
callee frame. Runtime allocator/lifetime legitimacy remains
unproven. No guard.

ORIGIN: writer of `0x84($sp)` is `loadSkyHorizonHob`
`rs_malloc($s4&0xFFFF)` at `0x8005AEF4`; writer of
`$sp+0x10[i]` is `loadSkyHorizonHob`
`rs_malloc((0xC($s6)<<1))` at `0x8005ABDC`. Both values are
legitimate allocator returns. No mitigation was added.
