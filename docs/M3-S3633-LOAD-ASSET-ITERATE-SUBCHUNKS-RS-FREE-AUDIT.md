# M3 s3633 — loadAssetAndIterateSubchunks rs_free of $s6

## Work unit

Static census of `loadAssetAndIterateSubchunks` `jal rs_free`
at `0x8005519C` (`$a0` = `$s6` = matching
`get_asset_size_extra` `rs_malloc` at `0x80054F48` flags-4 /
`0x80054F60` flags-0 retry). Enumerated every original
load/store of `$s6` (including the DMA dest, the `$s2` walk
alias, the `$a2`/`0x70($sp)` keep-buffer gate, and every
later store that can become this `$a0`) and every
`jal rs_free` that can receive that pointer. No build or
runtime run was performed.

The discriminator was the single complete original census of
that `jal rs_free` site plus every original `lw`/`sw`/`addu`
of `$s6` in `loadAssetAndIterateSubchunks` and every
caller-side store that can become this `$a0`, and every
`jal rs_free` that can receive that pointer:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeAllHobFiles slot `+0x8`,
releaseMeshAsset `$s5`, load_hmt_and_hob `$s3`/`0x6C`/`0x74`,
freeSubtitleOverlay `*0x80139010`, freeTxtFile globals,
loadSpriteSheetTextureFrames inlined-malloc,
loadAndRelocateAsset load_asset, loadExplosionTextures
load_asset, freeEffectAssetBuffers globals,
loadSkyHorizonHob stack scratch,
cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
spawnCutsceneObjectsFromList 0x6C, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor +0x4C, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch rs_free, text-texture rs_free, format-message
rs_free, speech-file rs_free, speech/cache rs_free, destructor
skipped-NULL, destructor unchecked-free, `-0x6904` alias,
remaining-indexer, `-0x6908` non-a0, release/fade,
`+0x5C`/`+0x64`, `+0x66..+0x74`, `+0x18..+0x24`,
`+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`, MORT publication,
mix-table, pan-input, or hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_11.c`: 7 sites. One is
this class (`0x8005519C`). The other six are
`attachedMeshOverlayNpcHandler` `0x80054344` (`0x1C($s0)`),
`load_full_header_image` `0x800544D8` (`$s1`),
`freeListEntryPointers` `0x80054620` (`0x1C($s0)`),
`loadAssetIntoNewSlot` `0x800549E4` (that function's `$s6`),
and `freeAnimationPhasePool` `0x80054AC8`/`0x80054AEC`
(`0x0(slot)` / `0x80137C84`). None of those six loads this
function's `$s6`. `loadAssetIntoNewSlot`'s `$s6` is a
different callee-saved register in a different frame.

`loadAssetAndIterateSubchunks` is `0x80054EF0`..`0x800551D4`,
frame `-0x68`. Eight generated callers; zero
`LOOKUP_FUNC(0x80054EF0)`. Single `jr $ra` at `0x800551D0`.

Original `$s6` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| prologue | `0x80054F1C` | `sw $s6, 0x58($sp)` | callee-save | not a heap store |
| DMA malloc | `0x80054F48`/`0x80054F50` | `jal rs_malloc($s4, 4)`; `addu $s6, $v0` | `$s6` | flags-4 writer |
| DMA retry | `0x80054F60`/`0x80054F68` | `jal rs_malloc($s4, 0)` if `$s6==0`; `addu $s6, $v0` | `$s6` | flags-0 retry; only other `$s6` heap writer |
| walk alias | `0x80054F70`/`0x80055008`/`0x80055020` | `addu $s2, $s6` | `$s2` | same pointer; never stored |
| DMA dest | `0x80054FC0` | `sw $s6, 0x14($sp)` | stack | `setupAssetDma` dest, not a second pointer |
| chunk walk | `0x80054FFC`/`0x80055180` | `addu $s2, $s6, $s3` | `$s2` | interior of `$s6`; dies with the buffer |
| keep-table | `0x80055000`/`0x80055184` | `lw 0x70($sp)` | `$a2` | gates index-table malloc and `0xFFFF` terminator, not this free |
| table malloc | `0x80055014`/`0x8005501C` | `jal rs_malloc((count+1)<<1, 0)`; `addu $s4, $v0` | `$s4` | returned table; not `$s6` |
| relocate | `0x80055070`..`0x800550AC` | 8-iter `+0x4` plus `+0x20`/`+0x24($s2)` | `$s6` body | interior offsets; die with the buffer |
| name/id | `0x80055120`/`0x80055148` | `sw $s7, 0x28($s2)`; `sh $v0, 0x0($s1)` | `$s6` body / table | stack name or texture-id halfword |
| DMA free | `0x8005519C`/`0x800551A0` | `jal rs_free`; `addu $a0, $s6` | `$s6` | destructor; both `$a2` arms; no NULL skip; no post-free NULL |
| epilogue | `0x800551B4` | `lw $s6, 0x58($sp)` | callee-save | restores caller `$s6` |

`$s6` is never stored to a global. `$v0` is `$s4`, not `$s6`.

## Object identity

### `$s6` — packed DMA buffer

Sequence:

1. `get_asset_size_extra($a0=name)` into `$s4`.
2. `rs_malloc($s4, 4)` then retry `rs_malloc($s4, 0)` into
   `$s6`.
3. `findAssetAcrossSegments` / `setupAssetDma` dest `$s6` /
   `teardownAssetDma`.
4. Count chunks by walking `$s2 = $s6 + $s3` while
   `$s3 < size-0x10`; `$s5` is the count.
5. `0x70($sp)` (`$a2`): if 0, malloc `(count+1)<<1` into
   `$s4` as the return table; if nonzero, `$s4` is the
   caller-provided table.
6. Per-chunk: relocate interior file offsets by adding
   `$s2+4`; `registerHmtTextureInTable($s2+4)` copies pixels
   and returns a texture-id halfword stored at `$s1`.
7. If `$a2==0`, write `0xFFFF` terminator at `$s4+$s0*2`.
8. `rs_free($s6)` on both `$a2` arms. Return `$s4`.

`$s2` is only a walk alias of `$s6`. Interior stores at
`$s2+4` / `+0x20` / `+0x24` / `+0x28` / `+0x32` die with
the buffer. `0x70($sp)` is the keep-table gate, not a
keep-`$s6` gate: both arms still free `$s6`. `blez $s5`
skips the chunk loop and still reaches the free. Failed
malloc (`$s6==0`) still reaches `rs_free`, which
`beq $s0, $zero` and returns. Zero chunk count with
`$a2==0` mallocs a 2-byte table, writes the terminator,
and frees `$s6`; that is not a second pointer source.

### Caller-side stores of the return (`$s4`), not `$s6`

Eight generated callers; none receive `$s6`:

| Caller | `$a2` / `0x70($sp)` | Return store | Frees `$s6`? |
|---|---|---|---|
| `loadTopCloudsAsset` | 0 (allocates table) | `0x2B44($s3)` | no; closed s3622 as the table |
| `loadExplosionTextures` ×5 | BSS `0x80139870` / `0x80139898` / `0x80139900` / `0x80139910` / `0x8013990C` | ignored | no |
| `initHudStruct` | `$s2` = that function's `rs_malloc(0xF80)` at hud `+0x4` | ignored (`$v0` is `$s2`) | no |
| `allocAndInitParticlePool` | 0 (allocates table) | `0x80130C08` | no |

`freeNpcBurstSpawnerTables` `0x80041B68` frees `0x80130C08`.
That is the returned index table, not this `$s6`.
`loadExplosionTextures`' own `load_asset` `rs_free` was
closed s3625 and does not load `$s6`.

## Pairing

One generated destructor. Both `$a2` arms reach it. There
is no second `jal rs_free` of this `$s6`. Sequential
double-free would require a caller to hold `$s6`; no
caller-side store exists. Runtime allocator legitimacy and
whether every call's malloc succeeds remain unproven.

## Classification

The only `jal rs_free` site that can receive this pointer
is `0x8005519C`. The only original heap-pointer writers of
`$s6` are the flags-4 malloc at `0x80054F50` and the
flags-0 retry at `0x80054F68`. The `$s2` walk alias, the
DMA dest slot, and the `$a2` keep-table path are not a
second pointer source. This selects `H-NextClassComplete`.
`H-NextClassGap` is refuted at static scope.
`H-NextClassUnevaluable` is not selected: one DMA-buffer
identity and two mutually exclusive allocator stores of
that same register.

No guard was added. Runtime allocator state remains
unproven.

## Next remaining `jal rs_free`

Remaining in `funcs_11.c`: `freeAnimationPhasePool`
`0x80054AC8` (`$a0` = `0x0(0x80137C84 + index*16)`, gated
by `lhu +0x6 & 0x8000`) and `0x80054AEC` (`$a0` =
`0x80137C84`).
