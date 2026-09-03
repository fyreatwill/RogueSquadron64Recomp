# M3 s3630 — load_hmt_and_hob rs_free of $s3 / 0x6C($sp) / 0x74($sp)

## Work unit

Static census of `load_hmt_and_hob` `jal rs_free` at
`0x80056798` (`$a0` = `$s3`), `0x80056D60` (`$a0` =
`0x6C($sp)`, gated by `lbu 0x8F($sp)`), and `0x80056D6C`
(`$a0` = `0x74($sp)`). Enumerated every original load/store
of `$s3` / `0x6C($sp)` / `0x74($sp)` (including the
`get_asset_size_extra` `rs_malloc` at `0x80056580` flags-4 /
`0x80056598` flags-0 retry into `$s3`, and every later stack
malloc that can land in `0x6C`/`0x74`) and every `jal rs_free`
that can receive those pointers. No build or runtime run was
performed.

The discriminator was the single complete original census of
those three `jal rs_free` sites plus every original `lw`/`sw`
of `$s3`, `0x6C($sp)`, and `0x74($sp)` in `load_hmt_and_hob`
and every `jal rs_free` that can receive those pointers:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: freeSubtitleOverlay
`*0x80139010`, freeTxtFile globals, loadSpriteSheetTextureFrames
inlined-malloc, loadAndRelocateAsset load_asset,
loadExplosionTextures load_asset, freeEffectAssetBuffers
globals, loadSkyHorizonHob stack scratch,
cinematicSplineWalkerNpcHandler nested 0xF00/0x2B44,
spawnCutsceneObjectsFromList 0x6C, NPC allocateAndInit
destructor, player-craft `+0xBC`, playerAtStUpdate 0xA4/0xBC,
actor `+0x4C`, tickMultiPartVoiceLine, freeModelViewerMeshChain,
shutdownModelViewer header-word, lookup-table,
loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`,
speech/cache `rs_free`, destructor skipped-NULL, destructor
unchecked-free, `-0x6904` alias, remaining-indexer,
`-0x6908` non-a0, release/fade, `+0x5C`/`+0x64`,
`+0x66..+0x74`, `+0x18..+0x24`, `+0x28..+0x2C`,
`+0x30..+0x40`, `+0x60`, MORT publication, mix-table,
pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_12.c`: 10 sites. Three
are this class (`0x80056798`, `0x80056D60`, `0x80056D6C`).
The other seven are `loadSpriteSheetTextureFrames`
`0x80055450` (closed s3627), `loadAndRelocateAsset`
`0x800555C4` (closed s3626), `freeTxtFile`
`0x800558F8`/`0x80055910` (closed s3628),
`freeSubtitleOverlay` `0x800562CC` (closed s3629),
`releaseMeshAsset` `0x8005794C`, and `freeAllHobFiles`
`0x80059244`. None of those seven loads `$s3` as this
function's HMT buffer, `0x6C($sp)`, or `0x74($sp)`.

`load_hmt_and_hob` is `0x8005645C`..`0x80056DA0`, frame
`-0xC0`. Forty-three generated callers. Single `jr $ra` at
`0x80056D9C`. `sprintf` names are `%s_HMT` then `%s_HOB`.
`$a2` bit 0 is saved as `0x8F($sp)` and selects the HOB
packed-copy path.

Original `$s3` / `0x6C($sp)` / `0x74($sp)` accesses:

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| HMT malloc | `0x80056580`/`0x80056588` | `jal rs_malloc($s2, 4)`; `addu $s3, $v0` | `$s3` | flags-4 writer |
| HMT retry | `0x80056598`/`0x800565A0` | `jal rs_malloc($s2, 0)` if `$s3==0`; `addu $s3, $v0` | `$s3` | flags-0 retry; only other `$s3` heap writer |
| DMA dest | `0x800565DC` | `sw $s3, 0x14($sp)` | `$s3` | `setupAssetDma` dest, not a second pointer |
| relocate | `0x80056618`..`0x80056688` | `lw`/`addu $s3` into `+0x4`/`+0x24`/`+0x28` | HMT body | interior offsets; die with the buffer |
| tex count | `0x800566E0` | `lhu 0x0($s3)`; `beq 0 -> L_80056D74` | `$s3` | skip remaining work and all three frees |
| tex-id malloc | `0x800566F0`/`0x800566FC` | `jal rs_malloc(count<<1, 4)`; `sw $v0, 0x74($sp)` | `0x74($sp)` | flags-4 writer |
| tex-id retry | `0x80056708`/`0x80056710` | `jal rs_malloc(count<<1, 0)`; `sw $v0, 0x74($sp)` | `0x74($sp)` | flags-0 retry; only other `0x74` writer |
| tex fill | `0x80056720`..`0x80056774` | `lw $s2, 0x74($sp)`; `sh $v0, 0x0($s2)` | `0x74($sp)` | consumer; texture-id halfwords from `registerHmtTextureInTable` |
| HMT free | `0x80056798`/`0x8005679C` | `jal rs_free`; `addu $a0, $s3` | `$s3` | destructor; no NULL skip; no post-free NULL |
| `$s3` reuse | `0x800567DC` | `lbu $s3, 0x8F($sp)` | flag | not a heap pointer |
| HOB malloc | `0x800567EC`/`0x80056800` | `jal rs_malloc($s2, 4 or 0x10)`; `sw $v0, 0x68($sp)` | `0x68($sp)` | kept HOB; not this class |
| `0x6C` copy | `0x80056870` | `lw 0x68`; `sw $t0, 0x6C($sp)` if flag | `0x6C($sp)` | only `0x6C` writer; original DMA HOB |
| packed copy | `0x8005687C`/`0x80056888` | `jal rs_malloc(0x4(hob)+4, 0x10)`; `sw $v0, 0x68($sp)` | `0x68($sp)` | overwrites `0x68`; `zmemcpy` from `0x6C` |
| tex consumers | `0x80056A24`/`0x80056AAC` | `lw $a3, 0x74($sp)` | `0x74($sp)` | `meshdef1_offset_convert` / `meshdef0_offset_convert`; neither `jal rs_free` |
| `$s3` interior | `0x800569D4`/`0x80056BCC` | `addu $s3` from HOB `+0x20` | HOB body | later `$s3` is an interior `0x68` pointer, not the freed HMT |
| `0x6C` free | `0x80056D50`..`0x80056D60` | `lbu 0x8F`; skip if 0; `lw $a0, 0x6C`; `jal rs_free` | `0x6C($sp)` | destructor of the DMA HOB; no post-free NULL |
| `0x74` free | `0x80056D68`/`0x80056D6C` | `lw $a0, 0x74`; `jal rs_free` | `0x74($sp)` | destructor; no NULL skip; no post-free NULL |

`$s3` is callee-saved at `0xA4($sp)` and restored at
`0x80056D8C`. That is not a heap-pointer store.

## Object identity

### `$s3` — packed HMT DMA buffer

Sequence:

1. `sprintf` `%s_HMT` into `$sp+0x18`.
2. `get_asset_size_extra` into `$s2`.
3. `rs_malloc($s2, 4)` then retry `rs_malloc($s2, 0)` into
   `$s3`.
4. `findAssetAcrossSegments` / `setupAssetDma` dest `$s3` /
   `teardownAssetDma`.
5. Name `pl_crafts/koelsch` runs `decrypt_ns_hmt($s3, $s2)`
   (no `rs_free`).
6. Relocate interior file offsets by adding `$s3`; optional
   `downscaleImageHalfResBoxFilter` of those interiors.
7. `lhu 0x0($s3)==0` jumps to `L_80056D74` and leaks `$s3`.
   That is a leak of the matching allocator return, not a
   second pointer source.
8. Otherwise allocate `0x74`, copy texture ids, then
   `rs_free($s3)`.

`$s3` is never stored to a global. After the free it is
overwritten with the `0x8F` flag byte, then later with
interior HOB pointers at `hob+0x20`. Those later values are
not passed to `rs_free`. `rs_free` itself `beq $s0, $zero`
and returns, so a failed malloc (`$s3==0`) that reached the
free would skip, not Gap. There is no original non-allocator
store into `$s3` before the free.

### `0x74($sp)` — texture-id halfword table

Size is `lhu 0x0($s3) << 1`. Only writers are the flags-4
malloc and the flags-0 retry. The fill loop stores returned
texture-id halfwords. `meshdef1_offset_convert` indexes
`$a3 + (halfword<<1)` and writes the looked-up id into mesh
data; it does not store `$a3`. `meshdef0_offset_convert`
saves `$a3` in `$s4` on its own frame and restores it; it
does not store the table pointer. No other generated
`jal 0x80001C98` can receive this stack word.

The `0x800566E0` zero-count path jumps to `L_80056D74` and
skips the `0x74` malloc and its free, so the epilogue free
is not reached with an uninitialized word.

### `0x6C($sp)` — original HOB DMA buffer on the packed-copy path

After the HMT free, `sprintf` `%s_HOB`, `get_asset_size_extra`
into `$s2`, then `rs_malloc($s2, flags)` into `0x68($sp)`
(flags 4 when `0x8F!=0`, else `0x10`; retry always `0x10`).
DMA lands in `0x68`.

When `0x8F==0`, `0x6C` is never stored and its free is
skipped. `0x68` is the kept HOB, published at
`0x80139020 + index*12 + 0x8` for object index 0
(`0x80056D20`). That published word is `freeAllHobFiles`
`0x80059244`, not this class.

When `0x8F!=0`:

1. `sw 0x68, 0x6C($sp)` — only `0x6C` writer.
2. `rs_malloc(0x4(hob)+4, 0x10)` overwrites `0x68`.
3. `zmemcpy(new, 0x6C, size)` copies the DMA bytes.
4. Relocate uses `0x80($sp)` = the new packed copy.
5. Epilogue `rs_free(0x6C)` then keeps `0x68`.

`0x6C` is used as the memcpy source and is not stored to a
global. The flag that writes it is the same flag that frees
it. The zero-count HMT skip never reaches this path.

`0x68`/`0x80`/`0x84` are the kept-or-copy HOB bases. They
are not `$s3` / `0x6C` / `0x74` and are not freed here.

## Pairing

Forty-three generated callers across twenty-two functions
(menu/hangar/cinematic/mission asset loads). Each call is
one stack frame: allocate HMT, free HMT, allocate tex-id
table, optionally allocate a second HOB DMA and free it,
free the tex-id table, return. Sequential double-free of
these three stack words would require the epilogue to run
twice on the same frame; there is one `jr $ra`.

A zero HMT texture count leaks `$s3` and skips HOB load.
Failed mallocs store NULL and `rs_free` skips. Runtime
allocator legitimacy and whether callers pair this load with
`freeAllHobFiles` / `releaseMeshAsset` remain unproven.

## Classification

The only `jal rs_free` sites that can receive these pointers
are `0x80056798`, `0x80056D60`, and `0x80056D6C`. `$s3` is
the matching `get_asset_size_extra` `rs_malloc`. `0x74($sp)`
is the matching `count<<1` `rs_malloc`. `0x6C($sp)` is the
matching HOB DMA `rs_malloc` copied off `0x68` before that
slot is overwritten, and only while `0x8F!=0`. Consumers
load the words as buffer bases or a texture-id table and do
not free them. No original non-allocator writer exists.
This selects `H-NextClassComplete`. `H-NextClassGap` is
refuted at static scope. `H-NextClassUnevaluable` is not
selected: each of the three words has one original
heap-pointer writer.

No guard was added. Runtime allocator state, the
zero-count HMT leak, and pairing of the kept `0x68` HOB
with `freeAllHobFiles` remain unproven.

## Next remaining `jal rs_free`

`releaseMeshAsset` in `funcs_12.c`: `0x8005794C`
(`$a0` = `$s5` = incoming `$a0`). Then `freeAllHobFiles`
`0x80059244` (`$a0` = `0x8($s0)` of the 12-byte slot table
at `0x80139020`, the kept `0x68` HOB).
