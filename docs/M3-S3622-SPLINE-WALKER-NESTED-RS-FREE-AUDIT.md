# M3 s3622 — cinematicSplineWalkerNpcHandler nested rs_free

## Work unit

Static census of `cinematicSplineWalkerNpcHandler` opcode-2
`jal rs_free` at `0x8005C35C` (`$a0 = 0x2B44(0xF00($s2))`) and
`0x8005C368` (`$a0 = 0xF00($s2)`). Enumerated every original
load/store of those two words and every `jal rs_free` that can
receive them. Classified each pointer's writer and whether a
free can run on a non-allocator or already-freed value. No
build or runtime run was performed.

The discriminator was the single complete original census of
those two `jal rs_free` sites plus every original `lw`/`sw` of
`0xF00($s2)` and `0x2B44(0xF00($s2))` and every `jal rs_free`
that can receive them:

- H-NextClassGap: a remaining free can pass a pointer that is
  not the matching allocator store, or can free it after a
  sibling already released it without a NULL.
- H-NextClassComplete: every remaining free is a destructor of
  a matching init store, and only runtime allocator legitimacy
  remains.
- H-NextClassUnevaluable: mixed object identities or unshared
  writers prevent a complete classification of a pointer source.

Closed classes were not repeated: leftover spawn `+0x6C`, NPC
allocateAndInit destructor, player-craft `+0xBC`,
playerAtStUpdate 0xA4/0xBC, actor `+0x4C`, tickMultiPartVoiceLine,
freeModelViewerMeshChain, shutdownModelViewer header-word,
lookup-table, loadCharTextureSet DMA-array, load_asset-then-free,
texture-scratch `rs_free`, text-texture `rs_free`,
format-message `rs_free`, speech-file `rs_free`, speech/cache
`rs_free`, destructor skipped-NULL, destructor unchecked-free,
`-0x6904` alias, remaining-indexer, `-0x6908` non-a0,
release/fade, `+0x5C`/`+0x64`, `+0x66..+0x74`,
`+0x18..+0x24`, `+0x28..+0x2C`, `+0x30..+0x40`, `+0x60`,
MORT publication, mix-table, pan-input, hangar-Y.

## Census size

Original `jal 0x80001C98` in `funcs_13.c`: 7 sites. Two are
this class (`0x8005C35C`, `0x8005C368`). The other five are
`loadSkyHorizonHob` `0x8005B350`/`0x8005B364` (callee-stack
scratch), `freeEffectAssetBuffers` `0x8005EBB4`/`0x8005EBC4`
(globals `0x8013961C`/`0x80139740`), and
`loadExplosionTextures` `0x80061254`. None of those five
loads `0xF00($reg)` or `0x2B44($reg)` of the 0xF14 walker
body / 0x2C90 wrapper.

Original non-stack word `lw`/`sw` of `0xF00($reg)` across all
`funcs_*.c`: 7 PCs, all in `funcs_13.c`. Immediate `0xF000`,
negative `-0xF00`, `addiu 0xF00`, `swc2`, and `scd` hits are
different encodings.

Original `0x2B44($reg)` across all `funcs_*.c`: 3 positive
word accesses, all in `funcs_13.c`. `funcs_3.c` `0x800082DC`
is `lw $a0, 0x2B44($at)` with `$at = 0x80110000 + $a3` (global
`0x80112B44` mesh-release table). `funcs_19.c` `0x80079B48`
is `lwc1 -0x2B44($at)`.

| Site | PC | Op | Object | Value |
|---|---|---|---|---|
| `loadTopCloudsAsset` | `0x8005A154`/`0x8005A174` | `jal rs_malloc(0x2C90)`; `sw $s3, 0xF00($s0)` | opcode-1 0xF14 body (`$a0`) | only `0x2C90` malloc |
| `loadTopCloudsAsset` | `0x8005A1A0` | `sw $v0, 0x2B44($s3)` | that 0x2C90 wrapper | `loadAssetAndIterateSubchunks` return |
| `loadTopCloudsAsset` | `0x8005A1EC` | `sw $zero, 0xF00($s0)` | inner `wrapper + i*0x5C`, 50 iters after `$s0=$s3` | 0; not actor `+0xF00` |
| `cinematicSplineWalkerNpcHandler` op1 | `0x8005BEAC` | `sw $zero, 0xF00($s2)` | 0xF14 body | 0, always, before the `0x80130B70` jump table |
| `cinematicSplineWalkerNpcHandler` op2 | `0x8005C34C` | `lw $v0, 0xF00($s2)` | same body | skip both frees when 0 |
| `cinematicSplineWalkerNpcHandler` op2 | `0x8005C358`/`0x8005C35C` | `lw`/`jal rs_free` `0x2B44($v0)` | wrapper | index-table malloc |
| `cinematicSplineWalkerNpcHandler` op2 | `0x8005C364`/`0x8005C368` | `lw`/`jal rs_free` `0xF00($s2)` | same body | 0x2C90 wrapper |
| `cinematicSplineWalkerNpcHandler` op4 | `0x8005C504` | `lw $v0, 0xF00($s2)` | same body | NULL-check; `$a2` of `updateWalkerParticlePositions` is the body, not this word |
| `updateWalkerParticlePositions` | `0x8005A50C` | `lw $a2, 0xF00($a2)` | only caller is opcode 4 | consumer |

`rs_malloc(0x2C90)` has one generated site. `loadTopCloudsAsset`
has one generated caller: jump-table case 10 (`0x80130B70 ==
0xA`) at `0x8005BECC`.

## Object identity

`$s0` at handler entry is `$a0` (NPC wrapper). `$s2` is
`0x4($s0)` except opcode 1, which `rs_malloc(0xF14)` at
`0x8005BD3C` and stores that at `0x4($s0)` (`0x8005BD54`).
`0xF00` sits near the end of that 0xF14 body.

Opcode 1 always zeros `0xF00($s2)` at `0x8005BEAC` (delay slot
of the `0x80130B70 < 0x11` branch, both arms). The jump table
at `0x8003AEE8` then:

- case 10: `loadTopCloudsAsset($s2)` stores the 0x2C90 malloc
  into that just-zeroed word
- cases 0, 1, 5: `load_hmt_and_hob` / `walkMeshdef0List` into
  `+0xED4`/`+0xED8`; they do not write `+0xF00`
- other cases / `>= 0x11`: leave `+0xF00` zero

Opcode 2 (`$a1==2` at `0x8005BD00`) jumps to `L_8005C310`,
skips the zero-store, `releaseMeshAsset`s `+0xED4` count and
`+0x18`, then the two `rs_free`s if `+0xF00` is nonzero. It
does not NULL `+0xF00` and does not free the 0xF14 body.

Opcode 4 is a consumer. `updateWalkerParticlePositions` is
only called from that path.

## Matching allocators

`loadTopCloudsAsset` (`0x8005A120`) is the only writer of the
freed `+0xF00` word as a heap pointer: `$s0=$a0` (the 0xF14
body), `rs_malloc(0x2C90)` at `0x8005A154`, `sw $s3, 0xF00($s0)`
at `0x8005A174`. It then `$s0=$s3` and the 50-iter
`sw $zero, 0xF00($s0)` at `0x8005A1EC` writes
`wrapper + i*0x5C + 0xF00`, a different word.

The 0x2B44 field of that wrapper is stored at `0x8005A1A0`
from `loadAssetAndIterateSubchunks` (`0x80054EF0`). That
callee `rs_malloc`s the DMA image into `$s6`, later
`rs_free`s `$s6` at `0x8005519C`, and returns `$s4`. When
`$a2==0` it `rs_malloc((chunk_count+1)<<1)` at `0x80055014`
into `$s4`. `loadTopCloudsAsset` passes `$a1=$a2=$a3=0` and
stack arg 0, so 0x2B44 is that halfword-table malloc. The
same function later `lhu`s through it at `0x8005A308`. The
`$a2!=0` caller-buffer path is not used for this store.

`rs_free` itself `beq $s0, $zero` at `0x80001CA4` and returns,
so a NULL `$a0` is a skip, not a Gap. Opcode 2 has no local
NULL skip on 0x2B44; a failed table malloc stores 0.

No other `jal rs_free` receives either pointer. The five
sibling `funcs_13.c` frees are stack scratch or the
`0x8014xxxx` effect-buffer globals.

## Sequential double-free

Opcode 2 does not NULL `+0xF00` after the wrapper free.
`destroyNpcSlotByIndex` (`0x8003ED74`) `jalr`s the handler
with `$a1=2` once (`0x8003EDE0`) then
`reinsertNpcIntoSortedFreeList`. That is a dangling word on
a detached wrapper, not a second pointer source, matching
s3617/s3620.

A second opcode-1 on a live wrapper would leak the previous
0xF14/0x2C90 pair (opcode 1 overwrites `0x4($s0)` without
freeing it). That is a leak, not a non-allocator or
already-freed free.

## Verdict

H-NextClassComplete. The two opcode-2 frees are the
destructor of the matching `loadTopCloudsAsset` stores: 0x2B44
is the `(chunk_count+1)*2` index table, 0xF00 is the 0x2C90
wrapper. H-NextClassGap is refuted at static scope: no free
of a non-allocator or already-freed value. H-NextClassUnevaluable
is not selected: both words have a single original heap-pointer
writer and a single object identity (0xF14 body / 0x2C90
wrapper). Runtime allocator/lifetime legitimacy remains
unproven. No guard.

ORIGIN: writer of `+0xF00` is `loadTopCloudsAsset`
`rs_malloc(0x2C90)` at `0x8005A154`; writer of wrapper
`+0x2B44` is `loadAssetAndIterateSubchunks`
`rs_malloc((chunk_count+1)<<1)` at `0x80055014` with `$a2=0`.
Both values are legitimate allocator returns. No mitigation
was added.
