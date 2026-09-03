# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3648 (2026-09-03).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-image/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The Factor 5 image task is the
qualified real-audio arm; `ROGUESQ_AUDIO_UCODE=0`/`Broke` is the silent control.
Audio is not production-complete.

The active M5 Step 3 boundary is the image-task source range
`0x1797B0..0x179930`. The port's target handoff sees a deliberate zero-fill
from `0x800078EC` (`rs_memset`, with tuples such as
`dst=0x801797B0, fill=0, len=0x298`) followed by zero source-DMA payloads.
Retail independently reaches the target phase, writes the watched source
span, and repeatedly calls `0x800078E0` with `a2=0x80` and changing structure
pointers from `0x800C825C`, unlike the port tuple. The target-phase retail
source writer is `0x800078EC` and runs before the first observed target VI. A
new oracle capture observed nonzero words and joined the
`0x800052C4 -> 0x800078E0 -> 0x800078EC` path with changing buffer/length
tuples. Session 3584 watched the qualified source buffer itself: all controls
and the target phase fired, but its phase histogram was mixed and exposed no
stable earlier constructor or distinct DMA/copy PC. The earlier-constructor
boundary is therefore unavailable to this oracle, not disproven; exact DMA
ordering remains open. This still selects a retail-versus-port stored-value
divergence at the writer boundary and qualifies the immediate producer
context. See
[M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md).

Do not force the cinematic flag at `0x800B0934`, bypass the state machine, or
rewrite task, audio, PCM, selector, or output state. The default route's null
stage-advancer input is a known route/configuration issue; the validated
real-audio route is the comparison arm.

## Next steps

The backlog is one monotonic sequence. Work only the first applicable item.

1. M5 Step 3: the source-buffer oracle boundary is now closed as unavailable;
   do not repeat that watch or the saturated field table. Exact DMA ordering
   remains open, but no DMA identifier is exposed by the current capture. Do
   not implement a writeback or zero-fill mitigation without a new independent
   writer/order discriminator.
2. Keep the s3554 slot-dispatch failure parked as route-specific absence.
   Revisit only with a new route discriminator; do not add a slot guard.
3. Keep the silent-arm `fillSampleStreamRange` crash separate from the
   real-audio target path, and do not infer target behavior from it.
4. M5's exact DMA ordering remains unresolved and unavailable to the current
   oracle. While it is parked, perform only systematic M3 idiom-class audits.
   Sessions 3586–3593 structurally closed packed-handle, allocator-stride,
   record-field, hangar-Y, MORT publication, mix-table, and pan-input classes
   with no concrete invalid writer. Sessions 3594–3599 selected structural
   unevaluability for mixed-layout families `+0x60`, `+0x30..+0x40`,
   `+0x28..+0x2C`, `+0x18..+0x24`, `+0x66..+0x74`, and envelope companion
   `+0x5C`/`+0x64`. Sessions 3600–3620 closed unmasked release/fade,
   remaining `0x88`-stride indexers, remaining `-0x6908` non-a0,
   `-0x6904` alias, destructor unchecked-free, skipped-NULL
   destructor-free, remaining speech/cache `rs_free`, remaining
   speech-file `rs_free`, remaining format-message `rs_free`,
   remaining text-texture `rs_free`, remaining texture-scratch
   `rs_free`, remaining load_asset-then-free clones, remaining
   `loadCharTextureSet` DMA-array `rs_free`, remaining
   lookup-table `rs_free`, remaining `shutdownModelViewer`
   header-word `rs_free`, remaining model-viewer mesh-chain
   `rs_free`, remaining `tickMultiPartVoiceLine` `$s0`
   `rs_free`, remaining actor `+0x4C` `rs_free`, remaining
   `playerAtStUpdate` `0xA4`/`0xBC` `rs_free`, remaining
   player-craft table `+0xBC` `rs_free`, remaining NPC
   `allocateAndInitCraftNpcContext` destructor `rs_free`, and
   leftover `spawnCutsceneObjectsFromList` `0x6C` store,
   `cinematicSplineWalkerNpcHandler` nested `rs_free`,
   `loadSkyHorizonHob` stack-scratch `rs_free`,
   `freeEffectAssetBuffers` globals `rs_free`,
   `loadExplosionTextures` `load_asset` `rs_free`,
   `loadAndRelocateAsset` `load_asset` `rs_free`,
   `loadSpriteSheetTextureFrames` inlined-malloc `rs_free`,
   `freeTxtFile` globals `rs_free`,
   `freeSubtitleOverlay` `*0x80139010` `rs_free`, and
   `load_hmt_and_hob` `$s3`/`0x6C($sp)`/`0x74($sp)`
   `rs_free`, `releaseMeshAsset` `$s5` `rs_free`,
   `freeAllHobFiles` slot `+0x8` `rs_free`,
   `loadAssetAndIterateSubchunks` `$s6` `rs_free`, and
   `freeAnimationPhasePool` slot `+0x0` / `0x80137C84`
   `rs_free`, `loadAssetIntoNewSlot` `$s6` DMA
   scratch `rs_free`, `load_full_header_image`
   `$s1` `rs_free`, and `freeLevelDatBuffers`
   `*0x801375D0` / `*0x801375D8` / `*0x801375F4`
   `rs_free` as complete.
   Session 3636 selected Gap for
   `attachedMeshOverlayNpcHandler` `0x80054344`: the
   two-iter `rs_malloc(0x80, 0)` at `0x80053DBC` is the
   only heap-pointer writer of `0x1C`/`0x20` on the
   pool-carved `0x4($wrapper)` body, but opcode 2 still
   frees those words when `dispatchOverlaySetupByParentAssetName`
   stores type `-1` or when parent mesh `+0xC` is NULL.
   Neither skip stores NULL first. No guard was added. See
   [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md).
   Session 3638 selected Complete for
   `freeLevelDatBuffers`: matching `load_asset` store of
   D8, flags-0 grid malloc of F4, and flags-0
   count-sized malloc of D0 (or NULL when count is 0).
   One destructor; skip-path `$v0` is `$s2` xor the D8
   store. No guard was added. See
   [M3-S3638-FREE-LEVEL-DAT-BUFFERS-RS-FREE-AUDIT.md](M3-S3638-FREE-LEVEL-DAT-BUFFERS-RS-FREE-AUDIT.md).
   Session 3639 selected Complete for
   `loadLevelTextureCache` `$s0`: matching flags-0
   `rs_malloc(0x136C, 0)` rebound at `0x80048248`.
   Incoming `$a0` is a reserved-size constant
   (`0x1000` / `0x5DC0`). The `0x80137614` count
   table is a different identity. One destructor; no
   caller holds the buffer. No guard was added. See
   [M3-S3639-LOAD-LEVEL-TEXTURE-CACHE-RS-FREE-AUDIT.md](M3-S3639-LOAD-LEVEL-TEXTURE-CACHE-RS-FREE-AUDIT.md).
   Session 3640 selected Complete for
   `freeGridCellBuffers`: matching flags-0
   `rs_malloc(n*0xB8, 0)` of `0x80137A5C`,
   `rs_malloc(12*(10n+1), 0)` of `0x80137A54`,
   `rs_malloc(n*4, 0)` of `0x80137A4C`, and
   `rs_malloc(200*(n/10), 0)` of `0x80137A68`
   (interior split at `0x80137A6C` is not
   independently freed). One destructor via
   `teardownAnimatedMapGridLayer`; type-`0xA`
   skip is paired. No guard was added. See
   [M3-S3640-FREE-GRID-CELL-BUFFERS-RS-FREE-AUDIT.md](M3-S3640-FREE-GRID-CELL-BUFFERS-RS-FREE-AUDIT.md).
   Session 3641 selected Complete for
   `teardownGridLayerWorker`: matching flags-0
   `rs_malloc(count*12, 0)` of `0x80137614`.
   Consumers load it as a table base and do not
   `jal rs_free`. One destructor via
   `teardownAnimatedMapGridLayer`; type-`0xA`
   skip is paired. No guard was added.
   `funcs_10.c` `jal rs_free` is exhausted. See
   [M3-S3641-TEARDOWN-GRID-LAYER-WORKER-RS-FREE-AUDIT.md](M3-S3641-TEARDOWN-GRID-LAYER-WORKER-RS-FREE-AUDIT.md).
   Session 3642 selected Complete for
   `teardownAnimatedMapGridLayer` remaining
   `rs_free`: matching flags-0 HMP
   `rs_malloc` of `0x80136FC4`, W*H grid of
   `0x80136DC8`, second asset of `0x80136DCC`,
   `n*12` node pool of `0x80136FCC`, and
   `n*24` of `0x80136E1C`. One destructor;
   `0x80136FC4` is NULLed after its free.
   Type-`0xA` skips the `n*24` publish and
   the `0x6FCC`/`0x6E1C` frees. No guard was
   added. See
   [M3-S3642-TEARDOWN-ANIMATED-MAP-GRID-LAYER-RS-FREE-AUDIT.md](M3-S3642-TEARDOWN-ANIMATED-MAP-GRID-LAYER-RS-FREE-AUDIT.md).
   Session 3643 selected Complete for
   `computeGridTileEdgeAdjacencyMasks` `$s1`:
   matching flags-0 `rs_malloc(lhu 0x18(*0x80136FC4), 0)`
   at `0x80044C00`. Never stored. One destructor
   at `0x800453AC`; skipped walks still reach it.
   `static_3_80045024` is an unreferenced tail
   clone of the same PCs, not a second destructor.
   No guard was added. See
   [M3-S3643-COMPUTE-GRID-TILE-EDGE-ADJACENCY-MASKS-RS-FREE-AUDIT.md](M3-S3643-COMPUTE-GRID-TILE-EDGE-ADJACENCY-MASKS-RS-FREE-AUDIT.md).
   Session 3644 selected Complete for
   `freeNpcBurstSpawnerTables`: matching flags-0
   `rs_malloc(0x3600, 0)` of `0x80130BD0`,
   `loadAssetAndIterateSubchunks` `$a2=0` index
   table of `0x80130C08`, and `load_asset` of
   `0x80130C04`. One destructor via
   `endMissionCleanup`; no NULL skip or post-free
   NULL. Consumers load the three words as table
   bases and do not `jal rs_free`. No guard was
   added. See
   [M3-S3644-FREE-NPC-BURST-SPAWNER-TABLES-RS-FREE-AUDIT.md](M3-S3644-FREE-NPC-BURST-SPAWNER-TABLES-RS-FREE-AUDIT.md).
   Session 3645 selected Complete for
   `destroyNpcContextArrays` `*0x80130BC0` /
   `*0x80130BC4` / `*0x80130BBC` / `*0x80130BB8`.
   Session 3646 selected Complete for
   `freeNpcSlotArray`: matching flags-0
   `rs_malloc(0x4000, 0)` of `0x80130BB0`
   (0x800 × 8-byte slot table). One
   destructor via `endMissionCleanup`; no NULL
   skip; NULL after. Consumers load the word
   as a table base and do not `jal rs_free`.
   `0x80130BB4` is a free-list head halfword,
   not a pointer. `funcs_9.c` `jal rs_free`
   is exhausted. No guard was added. See
   [M3-S3646-FREE-NPC-SLOT-ARRAY-RS-FREE-AUDIT.md](M3-S3646-FREE-NPC-SLOT-ARRAY-RS-FREE-AUDIT.md).
   Session 3647 selected Complete for
   `reinsertNpcIntoSortedFreeList`
   `0x4($npc)`. Session 3648 selected
   Complete for `loadDebugAssets` `$s0`:
   matching `get_asset_size_extra`
   `rs_malloc($s2, 8)` rebound at
   `0x80024768`. Never stored. One
   destructor; `-1` skip is paired.
   `funcs_7.c` `jal rs_free` is exhausted.
   No guard was added. See
   [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md).
   Retail-entry and SP-yield threads remain parked. The next
   M3 unit is `destroyTextureLUTs`
   `*0x80128F08` / `*0x80128EFC`
   `rs_free` at `0x8001E344` /
   `0x8001E354`. Do
   not add a pointer guard without a concrete
   invalid writer.
5. Generated-symbol renaming remains last priority. Resume only when M5 is
   closed and M3 is parked with no new discriminator.

## Active hypothesis table

| Hypothesis | Discriminating result |
|---|---|
| H-RetailWriterSame | Selected for target-phase identity/order: `0x800078EC` writes at 47.4 s before target VI at 48.5 s. |
| H-RetailWriterOther | Refuted for the target-phase write; earlier setup writers are separate activity. |
| H-RetailOrdering | Exact DMA ordering remains unmeasured. |
| H-RetailValue | Nonzero target-phase words selected; parity against the port remains open. |
| H-RetailProducer | `0x800052C4` is repeatedly the immediate caller of `0x800078E0`; no earlier constructor was exposed by the repeated field table. |
| H-RetailDmaOrder | No separate DMA event identifier was exposed; ordering remains open. |
| H-CaptureInvalid | Refuted for this run: whole-RDRAM, source-span, writer-PC, and target-phase controls all fired. |
| H-MortComplete | Selected structurally: the `0x8009D7D0..0x8009DD7C` path has complete bounded stages and publication edges. |
| H-MortGap | No concrete missing/invalid writer, consumer, base, or bound was found. |
| H-MortMisread | Not supported: the range is a coherent CPU voice-filter/mix/compand path. |
| H-NextClassComplete | Selected for `loadDebugAssets` `$s0`: matching flags-8 `get_asset_size_extra` `rs_malloc`; one destructor. |
| H-NextClassGap | Refuted for this register. Remains selected for overlay `0x1C`/`0x20` (s3636). |
| H-NextClassUnevaluable | Not selected: one scratch-buffer identity and one allocator store. |

The current work-unit slug is `m3-next-audio-idiom-audit`.

## Recent evidence ledger

Only the latest boundary transitions are repeated here; the append-only ledger
and evidence notes retain the full history.

- **3648 — loadDebugAssets rs_free of $s0:** `$s0`
  is the matching `get_asset_size_extra`
  `rs_malloc($s2, 8)` at `0x80024768`. Never
  stored to a global. Incoming `$s3` is
  `*0x8010E008`. The ROM string at
  `0x80000A48` is overwritten before the free.
  DMA slot `+0x24` is dest only;
  `teardownAssetDma` does not `jal rs_free`.
  `registerHmtTextureInTable` copies pixels and
  keeps a texture-id halfword at `0x80128F22`.
  One destructor; `-1` skip is paired. Two
  generated callers; zero overlay lookup. One
  `jr $ra`. `funcs_7.c` `jal rs_free` is
  exhausted. This selects `H-NextClassComplete`.
  See
  [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md).
- **3577 — remaining retail zero-fill edge:** retail controls fired and
  `0x800C825C` repeatedly reached `0x800078E0` with `a2=0x80` and changing
  structure pointers, unlike the port's `0x801797B0/0/0x298` tuple. Input
  divergence is selected; writer identity and ordering remain open.
- **3579 — retail source writer:** controls and target phase fired. The
  target-phase source span was written by `0x800078EC` at 47.4 s before the
  first 512-wide target VI at 48.5 s. Writer identity and pre-target order
  selected; ordinary watch rows did not report stored values, so value parity
  remains open. See [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md).
- **3581 — retail source producer/value:** controls fired; the target
  transition joined `0x800052C4 -> 0x800078E0 -> 0x800078EC` with buffer/
  length tuples and nonzero post-store words. No independent DMA event was
  exposed, so producer construction and exact DMA order remain open. See
  [M5-S3581-RETAIL-SOURCE-PRODUCER.md](M5-S3581-RETAIL-SOURCE-PRODUCER.md).
- **3582 — retail source-writer table:** controls fired; target phase VI 2803
  at 47.4 s recorded 384 `0x800078EC` source-span writes and nonzero
  post-store words, while field rows joined `0x800052C4 -> 0x800078E0 ->
  0x800078EC` with `0x8065E0A0/0x1C`. No DMA event identifier was exposed;
  earlier construction and exact ordering remain open. See
  [M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md](M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md).
- **3583 — retail producer discriminator repeat:** controls fired; target
  phase reached VI 2813 at 48.5 s and the writer histogram again recorded 384
  `0x800078EC` writes. The joined tuple included `0x8065FA30/0x1C` and
  `0x59050000`; post-value rows again contained nonzero words. No earlier
  constructor or DMA event identifier was exposed, so those boundaries stay
  open. See [M5-S3583-RETAIL-PRODUCER-REPEAT.md](M5-S3583-RETAIL-PRODUCER-REPEAT.md).
- **3584 — retail source-buffer writer:** all three watches and the target phase
  fired; source-buffer writes were mixed, with 176 phase hits at `0x800078EC`
  and no stable distinct constructor/DMA PC. The earlier-constructor boundary
  is unavailable to this oracle; exact DMA ordering remains open. See
  [M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md).
- **3586 — `voice_record+0x64` writer/lifecycle audit:** every generated field
  writer was enumerated. `startNoteOnVoice` writes a packed handle whose low
  byte is the allocator-returned slot; cleanup and reset paths write `-1`.
  This corrects the prior semantic label of the field as a standalone slot
  index. No concrete invalid low-byte writer was found, but runtime allocator
  state and record lifetime remain unproven. See
  [M3-S3586-VOICE-INDEX-WRITERS.md](M3-S3586-VOICE-INDEX-WRITERS.md).
- **3587 — `allocateSynthVoice` stride-scan audit:** the complete allocator
  scan class uses 0x17C-stride indices bounded by the slot-count byte; each
  selected candidate is checked against `-1` and its per-slot limit before
  returning. No concrete invalid writer/value or unchecked index was found,
  so no guard was added. See [M3-S3587-ALLOCATOR-STRIDE-AUDIT.md](M3-S3587-ALLOCATOR-STRIDE-AUDIT.md).
- **3588 — packed voice-handle table writer audit:** all three stores to the
  per-slot `-0x271C` field were enumerated. Cleanup/reset write `-1`, while
  `startNoteOnVoice` writes the composite handle after allocator selection.
  Low-byte consumers were classified; runtime allocator/lifetime legitimacy
  remains unproven, so no guard was added. See
  [M3-S3588-VOICE-HANDLE-TABLE-WRITERS.md](M3-S3588-VOICE-HANDLE-TABLE-WRITERS.md).
- **3589 — audio record field/table-address audit:** all 29 distinct generated
  writer PCs and 13 `-0x7C30` consumer PCs were enumerated. The relevant audio
  writers are `musyxKeyOnVoice` (`+0x64` to field `0x4E`) and
  `tickAudioChannel` (`+0x58/+0x59` to fields `0x4E/0x4F`); no concrete
  invalid value was found. The source-field ranges remain unclassified and
  no guard was added. See
  [M3-S3589-AUDIO-RECORD-FIELDS.md](M3-S3589-AUDIO-RECORD-FIELDS.md).
- **3592 — CPU MORT publication idiom audit:** the complete requested range
  has bounded filter, delay, lattice, mix, compand, and voice-state
  publication edges. No concrete invalid writer/value, alternate base, or
  unchecked count was found; runtime legitimacy remains unproven. See
  [M3-S3592-MORT-PUBLICATION-IDIOM-AUDIT.md](M3-S3592-MORT-PUBLICATION-IDIOM-AUDIT.md).
- **3593 — pan-coefficient input/selector provenance audit:** all three direct
  callers and the 16-byte source-vector paths were enumerated. The selector is
  a bounded two-bank toggle at `voice+0x188`; no concrete invalid writer,
  source pointer, object base, or unchecked count was found. Runtime source
  contents, allocator state, and DMA timing remain unproven. See
  [M3-S3593-AUDIO-PAN-INPUT-PROVENANCE-AUDIT.md](M3-S3593-AUDIO-PAN-INPUT-PROVENANCE-AUDIT.md).
- **3594 — MusyX voice `+0x60` field audit:** generated accesses split across
  channel, envelope, render-voice, and source-descriptor layouts; reset values
  are legitimate transitions, but no complete object identity, caller-proven
  slot bound, or lifetime chain is exposed. This selects
  `H-NextClassUnevaluable`, not a concrete invalid writer. See
  [M3-S3594-VOICE-60-FIELD-AUDIT.md](../scratch/agent/M3-S3594-VOICE-60-FIELD-AUDIT.md).
- **3595 — MusyX voice `+0x30..+0x40` field audit:** the complete generated
  access census split across global voice slots, sample/command descriptors,
  and stack frames. Mixed widths and layouts prevent a complete object-level
  classification; no concrete invalid writer/value was found and no guard was
  added. See [M3-S3595-VOICE-30-40-FIELD-AUDIT.md](../scratch/agent/M3-S3595-VOICE-30-40-FIELD-AUDIT.md).
- **3596 — MusyX voice `+0x28..+0x2C` field audit:** generated accesses split
  across stack temporaries, source/command descriptors, and global voice
  slots. Initialization/copy writers have identified sources, but the
  64-slot bound and secondary unmasked-index contract are not proven; no
  concrete invalid writer/value was found. This selects
  `H-NextClassUnevaluable`. See
  [M3-S3596-VOICE-28-2C-FIELD-AUDIT.md](../scratch/agent/M3-S3596-VOICE-28-2C-FIELD-AUDIT.md).
- **3597 — MusyX voice `+0x18..+0x24` field audit:** 81 stores and 81 loads
  were enumerated. Stack spills aside, the offsets belong to the `0x88`
  voice-table volume halfwords, the command-list ping-pong `+0x22` flag,
  the `0xA10`/`0x50` key-on dest slope/pitch fields, and a separate
  descriptor/param block. No concrete invalid writer/value was found.
  This selects `H-NextClassUnevaluable`. See
  [M3-S3597-VOICE-18-24-FIELD-AUDIT.md](M3-S3597-VOICE-18-24-FIELD-AUDIT.md).
- **3647 — reinsertNpcIntoSortedFreeList
  rs_free of 0x4($npc):** Bit `0x4` of
  NPC `+0x14` is spawn-time only. Owned
  arm: spawn zeros `+0x4`;
  `slotDispatcherInner` skips; opcode 1
  stores flags-0 `rs_malloc` at `+0x4`;
  this site is the only `jal rs_free` of
  that pointer (NULL skip). Opcode 2
  frees interiors of the body
  (`0x38`/`0x230`/`0xF00`), not `+0x4`.
  Bit-clear arm reconstructs the 0x204C
  chunk and does not free `+0x4`. One
  generated caller; zero overlay lookup;
  one `jr $ra`. `funcs_8.c` `jal rs_free`
  is exhausted. Sibling `freeNpcSlotArray`
  `*0x80130BB0` is a different destructor.
  This selects `H-NextClassComplete`. See
  [M3-S3647-REINSERT-NPC-SORTED-FREE-LIST-RS-FREE-AUDIT.md](M3-S3647-REINSERT-NPC-SORTED-FREE-LIST-RS-FREE-AUDIT.md).
- **3646 — freeNpcSlotArray rs_free of
  *0x80130BB0:** Matching flags-0
  `rs_malloc(0x4000, 0)` of `0x80130BB0`
  (0x800 × 8-byte slot table). One original
  heap-pointer store in `initNpcSlotList`.
  Post-free NULL; no NULL skip. Fifty-seven
  consumer loads use the word as a table
  base (`+0x0` NPC / `+0x4` next / `+0x6`
  prev); none `jal rs_free`.
  `unregisterAndFreeNpcSlot` relinks a slot
  index onto `0xBB4` and does not heap-free
  the table. One destructor via two mutually
  exclusive `mainGameLoop` arms. Three inits
  overwrite without freeing; menu
  `initInteractiveSceneContext` without this
  destructor leaks. Zero overlay lookup. One
  `jr $ra`. `funcs_9.c` `jal rs_free` is
  exhausted. Sibling
  `reinsertNpcIntoSortedFreeList` `0x4($npc)`
  is a different destructor. This selects
  `H-NextClassComplete`. See
  [M3-S3646-FREE-NPC-SLOT-ARRAY-RS-FREE-AUDIT.md](M3-S3646-FREE-NPC-SLOT-ARRAY-RS-FREE-AUDIT.md).
- **3645 — destroyNpcContextArrays rs_free of
  *0x80130BC0 / *0x80130BC4 / *0x80130BBC /
  *0x80130BB8:** Matching flags-0
  `rs_malloc(0x2D00, 0)` of `0x80130BB8`
  (192×0x3C pool), `rs_malloc(0x300, 0)` of
  `0x80130BBC` (pointer table into that pool),
  and `slotDispatcherInner` `rs_malloc(0x204C, 0)`
  list heads at `0x80130BC0`/`0x80130BC4`
  (bit `0x1` selects which; init zeros both).
  `0x48` relinks and `reinsertNpcIntoSortedFreeList`
  republish those same mallocs. Five spawn
  consumers load `0xBBC` as a table base; none
  `jal rs_free`. `0x8003EC34` frees `0x4($npc)`,
  not these words. One destructor via two
  mutually exclusive `mainGameLoop` arms.
  Three inits overwrite without freeing; menu
  `initInteractiveSceneContext` without this
  destructor leaks. Zero overlay lookup. One
  `jr $ra`. `0xBC0`/`0xBC4` NULL-skip; `0xBBC`/
  `0xBB8` NULL after. Sibling `freeNpcSlotArray`
  `*0x80130BB0` is a different destructor. This
  selects `H-NextClassComplete`. See
  [M3-S3645-DESTROY-NPC-CONTEXT-ARRAYS-RS-FREE-AUDIT.md](M3-S3645-DESTROY-NPC-CONTEXT-ARRAYS-RS-FREE-AUDIT.md).
- **3644 — freeNpcBurstSpawnerTables rs_free of
  *0x80130BD0 / *0x80130C08 / *0x80130C04:**
  Matching flags-0 `rs_malloc(0x3600, 0)` of
  `0x80130BD0` (128×0x6C pool),
  `loadAssetAndIterateSubchunks` `$a2=0`
  `(count+1)<<1` table of `0x80130C08` (DMA
  `$s6` is freed inside that callee, s3633),
  and `load_asset` of `0x80130C04`. One
  original store each. `0x80130BD4` is a
  free-list head halfword, not a pointer.
  Consumers load the three words as table
  bases; stack extra-arg copies do not
  `jal rs_free`. One destructor via two
  mutually exclusive `mainGameLoop` arms.
  Three inits overwrite without freeing;
  menu `initInteractiveSceneContext` without
  this destructor leaks. Zero overlay lookup.
  One `jr $ra`. No NULL skip or post-free
  NULL. This selects `H-NextClassComplete`.
  See
  [M3-S3644-FREE-NPC-BURST-SPAWNER-TABLES-RS-FREE-AUDIT.md](M3-S3644-FREE-NPC-BURST-SPAWNER-TABLES-RS-FREE-AUDIT.md).
- **3643 — computeGridTileEdgeAdjacencyMasks
  rs_free of $s1:** `$s1` is the matching
  flags-0 `rs_malloc(lhu 0x18(*0x80136FC4), 0)`
  at `0x80044C00`. Never stored to a global.
  `rs_memset` fills it `0xFF`; tile `sb` and
  second-loop `lbu` use it as a byte table.
  Second-loop `MEM_B` stores go into
  `*0x80136DC4+0x10` records, not `$s1`.
  One destructor; H==0 and count==0 skips
  still reach it. One generated caller
  (`loadLevelAssets`); skipped when
  `*0x80130B39 != 0` or type `0x11`.
  `static_3_80045024` is an unreferenced
  same-PC tail clone (`__OSGlobalIntMask`
  jal is float-as-code). Zero overlay
  lookup. One `jr $ra`. This selects
  `H-NextClassComplete`. See
  [M3-S3643-COMPUTE-GRID-TILE-EDGE-ADJACENCY-MASKS-RS-FREE-AUDIT.md](M3-S3643-COMPUTE-GRID-TILE-EDGE-ADJACENCY-MASKS-RS-FREE-AUDIT.md).
- **3642 — teardownAnimatedMapGridLayer remaining
  rs_free of *0x80136DC8 / *0x80136DCC /
  *0x80136FC4 / *0x80136FCC / *0x80136E1C:**
  Matching flags-0 `rs_malloc` stores in
  `load_level_hmp` (HMP / W*H grid / second
  asset), `allocAndInitDoublyLinkedNodePool12`
  (`n*12`), and `loadLevelAssets` (`n*24`).
  Descriptor `0x80136DC0` `+0x0`/`+0x4` are
  interior HMP pointers. Adjacency `$s1` is a
  different scratch. Consumers load the five
  words as table bases and do not `jal rs_free`.
  `0x80136FC4` NULL-skips and NULLs after.
  Type `0xA` paired-skips `0x80136E1C` and
  leaks `0x80136FCC`. One destructor via two
  route wrappers. Zero overlay lookup. One
  `jr $ra`. This selects
  `H-NextClassComplete`. See
  [M3-S3642-TEARDOWN-ANIMATED-MAP-GRID-LAYER-RS-FREE-AUDIT.md](M3-S3642-TEARDOWN-ANIMATED-MAP-GRID-LAYER-RS-FREE-AUDIT.md).
- **3641 — teardownGridLayerWorker rs_free of
  *0x80137614:** Matching flags-0
  `rs_malloc(count*12, 0)` store at
  `0x80048180`. Interior halfwords, the 0x136C
  scratch `$s0`, worker/DMA handles, and BSS
  `0x80137620` are different identities.
  Consumers load the word as a table base and do
  not `jal rs_free`. Type `0xA` skip is paired.
  One destructor via two route wrappers (mission
  `mainGameLoop` arms and cinematic shutdown).
  Zero overlay lookup. One `jr $ra`. No NULL skip
  or post-free NULL. This selects
  `H-NextClassComplete`. See
  [M3-S3641-TEARDOWN-GRID-LAYER-WORKER-RS-FREE-AUDIT.md](M3-S3641-TEARDOWN-GRID-LAYER-WORKER-RS-FREE-AUDIT.md).
- **3640 — freeGridCellBuffers rs_free of *0x80137A5C /
  *0x80137A54 / *0x80137A4C / *0x80137A68:**
  Four matching flags-0 `rs_malloc` stores in
  `allocAndInitGridCellArray`. `0x80137A6C` is an
  interior split of the `0x80137A68` buffer, loaded
  as a table base, never independently freed.
  Consumers load the four words as table bases and
  do not `jal rs_free`. Incoming `$a0` is cell
  count (`getLevelExpansionMemoryBudget` or a
  cutscene halfword). Type `0xA` skip is paired.
  One destructor via two route wrappers (mission
  `mainGameLoop` arms and cinematic shutdown).
  Zero overlay lookup. One `jr $ra`. This selects
  `H-NextClassComplete`. See
  [M3-S3640-FREE-GRID-CELL-BUFFERS-RS-FREE-AUDIT.md](M3-S3640-FREE-GRID-CELL-BUFFERS-RS-FREE-AUDIT.md).
- **3639 — loadLevelTextureCache rs_free of $s0:**
  `$s0` is the matching flags-0 `rs_malloc(0x136C, 0)`
  at `0x80048248`. Incoming `$a0` is `0x1000`
  (`initMission`) or `0x5DC0` (`load_cutscene`),
  overwritten by `lui 0x8013` then the malloc.
  Never stored to a global. Interior `+0x0/+0x20/+0x24`
  die with the buffer. `registerHmtTextureInTable`
  copies pixels and keeps texture-id halfwords in the
  `0x80137614` table (a different malloc). One
  destructor; both the register loop and the count<=5
  skip reach it. Two generated callers; zero overlay
  lookup. One `jr $ra`. This selects
  `H-NextClassComplete`. See
  [M3-S3639-LOAD-LEVEL-TEXTURE-CACHE-RS-FREE-AUDIT.md](M3-S3639-LOAD-LEVEL-TEXTURE-CACHE-RS-FREE-AUDIT.md).
- **3638 — freeLevelDatBuffers rs_free of *0x801375D0 /
  *0x801375D8 / *0x801375F4:** D8 is the matching
  `load_asset` `$s2` stored only when `0x80130B3A != 1`.
  F4 is the matching `rs_malloc((W*H)<<1, 0)` at global
  `+0x1C`. D0 is the matching `rs_malloc(count<<2, 0)`
  or NULL when count is 0. Interior `0x1C($s2)` is an
  in-buffer convert, not F4. Skip-path `$v0` is `$s2`
  xor the D8 store; `shutdownModelViewer` of
  `0x800D03CC` is that skip return (s3614 polarity
  corrected). One generated destructor via two mutually
  exclusive `mainGameLoop` arms. This selects
  `H-NextClassComplete`. See
  [M3-S3638-FREE-LEVEL-DAT-BUFFERS-RS-FREE-AUDIT.md](M3-S3638-FREE-LEVEL-DAT-BUFFERS-RS-FREE-AUDIT.md).
- **3637 — load_full_header_image rs_free of $s1:**
  `$s1` is the matching `get_asset_size_extra`
  `rs_malloc` (flags-0). Never stored to a global.
  `$s0` is the `+4` convert/register alias; interior
  relocate stores die with the buffer. Delay-slot
  `0x80137C70` is a texture-id halfword consumed by
  `dispatchOverlaySetupByParentAssetName` and is not
  this pointer. Five generated callers; one `jr $ra`;
  straight-line body. `funcs_11.c` `jal rs_free` is
  exhausted. This selects `H-NextClassComplete`. See
  [M3-S3637-LOAD-FULL-HEADER-IMAGE-RS-FREE-AUDIT.md](M3-S3637-LOAD-FULL-HEADER-IMAGE-RS-FREE-AUDIT.md).
- **3636 — attachedMeshOverlayNpcHandler rs_free of 0x1C($s0):**
  `$s0` is `$s2=0x4($s1)` on opcode 2. The only
  heap-pointer writer of `0x1C`/`0x20` is
  `dispatchOverlaySetupByParentAssetName`
  `rs_malloc(0x80, 0)` at `0x80053DBC` (two-iter
  `+0x4` walk). Unmatched parent name stores type `-1`
  and skips that loop; NULL parent mesh skips setup.
  Opcode 2 still frees both words with no NULL store.
  Sibling `freeListEntryPointers` is unreferenced.
  Nine player-craft `spawnNpcOfType` sites. This selects
  `H-NextClassGap`. See
  [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md).
- **3635 — loadAssetIntoNewSlot rs_free of $s6:**
  `$s6` is the matching `get_asset_size_extra`
  `rs_malloc` (flags-0). Never stored to a global.
  `$s3` is the walk alias; interior relocate stores die
  with the buffer. Slot `+0x0` is a different converted-
  buffer malloc (closed s3634). Return is `$s5`, not
  `$s6`. Twelve generated callers; zero overlay lookup.
  One `jr $ra`. This selects `H-NextClassComplete`. See
  [M3-S3635-LOAD-ASSET-INTO-NEW-SLOT-RS-FREE-AUDIT.md](M3-S3635-LOAD-ASSET-INTO-NEW-SLOT-RS-FREE-AUDIT.md).
- **3634 — freeAnimationPhasePool rs_free of slot +0x0 /
  0x80137C84:** `0x80137C84` is the matching
  `allocAnimationPhasePool` `rs_malloc(count*28, 0)`.
  Slot `+0x0` is the matching `loadAssetIntoNewSlot`
  converted-buffer `rs_malloc`. `+0x6 & 0x8000` is set by
  that claim and overlaid with `0xC000` by
  `setPoolEntryPhaseAndMarkActive`; the overlay does not
  write `+0x0`. One generated destructor via two mutually
  exclusive `mainGameLoop` arms. Zero overlay lookup.
  One `jr $ra`. This selects `H-NextClassComplete`. See
  [M3-S3634-FREE-ANIMATION-PHASE-POOL-RS-FREE-AUDIT.md](M3-S3634-FREE-ANIMATION-PHASE-POOL-RS-FREE-AUDIT.md).
- **3633 — loadAssetAndIterateSubchunks rs_free of $s6:**
  `$s6` is the matching `get_asset_size_extra`
  `rs_malloc` (flags-4 then flags-0 retry). Never stored
  to a global. `$s2` is the walk alias; interior relocate
  stores die with the buffer. `$a2`/`0x70($sp)` selects
  the returned index table (caller-provided or
  `(count+1)<<1` malloc) and the `0xFFFF` terminator;
  both arms still `rs_free($s6)`. Return is `$s4`, not
  `$s6`. Eight generated callers; zero overlay lookup.
  One `jr $ra`. This selects `H-NextClassComplete`. See
  [M3-S3633-LOAD-ASSET-ITERATE-SUBCHUNKS-RS-FREE-AUDIT.md](M3-S3633-LOAD-ASSET-ITERATE-SUBCHUNKS-RS-FREE-AUDIT.md).
- **3632 — freeAllHobFiles rs_free of slot +0x8:**
  `0x8($s0)` is `0x80139020+index*12+0x8`. The only
  heap-pointer writer is `load_hmt_and_hob` `0x80056D20`
  storing kept `0x68($sp)` (`rs_malloc` then optional
  packed-copy malloc). Non-first objects store 0.
  `beq $a0, $zero` skips; the walk collapses buckets to
  `0xFFFF` so a second call does not re-free. Hash-table
  consumers load `+0x4` and do not free `+0x8`. One
  generated destructor; two mutually exclusive
  `mainGameLoop` teardown arms. Zero HOB count leaks
  unpublished `0x68`; that is not a second pointer source.
  `funcs_12.c` `jal rs_free` is exhausted. This selects
  `H-NextClassComplete`. See
  [M3-S3632-FREE-ALL-HOB-FILES-RS-FREE-AUDIT.md](M3-S3632-FREE-ALL-HOB-FILES-RS-FREE-AUDIT.md).
- **3631 — releaseMeshAsset rs_free of $s5:**
  `$s5` is incoming `$a0`. `walkMeshdef0List` is the
  pool (`sh 4`) or heap (`sh 0`) constructor;
  `instantiateNamedMeshInstance` mallocs with `sh 0x1001`;
  `createMeshInstanceFromSource` mallocs `0xB4` with
  `sh 1` (skip `rs_free`). Sixty-three callers pass those
  returns. `0x8005794C` is the only `jal rs_free` of the
  instance. One `jr $ra`. This selects
  `H-NextClassComplete`. See
  [M3-S3631-RELEASE-MESH-ASSET-RS-FREE-AUDIT.md](M3-S3631-RELEASE-MESH-ASSET-RS-FREE-AUDIT.md).
- **3630 — load_hmt_and_hob rs_free of $s3 / 0x6C($sp) / 0x74($sp):**
  `$s3` is the matching `get_asset_size_extra`
  `rs_malloc` (flags-4 then flags-0). `0x74($sp)` is the
  matching `count<<1` `rs_malloc` texture-id table.
  `0x6C($sp)` is the matching HOB DMA `rs_malloc` copied
  off `0x68` when `$a2` bit 0 is set, then freed; `0x68`
  is the kept HOB published at slot `+0x8`. Zero HMT
  count leaks `$s3` and skips the other two frees; that
  is not a second pointer source. One `jr $ra`. This
  selects `H-NextClassComplete`. See
  [M3-S3630-LOAD-HMT-AND-HOB-RS-FREE-AUDIT.md](M3-S3630-LOAD-HMT-AND-HOB-RS-FREE-AUDIT.md).
- **3629 — freeSubtitleOverlay rs_free of *0x80139010:**
  `0x80139010` is the matching `initVoiceSubtitleSystem`
  `rs_malloc(0x20, 0)`. One original store; 30 loads as
  overlay fields; one `jal rs_free` with no NULL skip or
  post-free NULL. Sibling `0x80139014` is a slot index
  (`0xA`/`0x4`/`0xB`) reset by
  `resetPlayerSlotChannelTransform`, which zeros transform
  words and does not `rs_free`. Two init callers; one
  destructor via two mutually exclusive `mainGameLoop`
  arms. Cinematic init without this destructor leaks the
  first malloc; that is not a second pointer source. This
  selects `H-NextClassComplete`. See
  [M3-S3629-FREE-SUBTITLE-OVERLAY-RS-FREE-AUDIT.md](M3-S3629-FREE-SUBTITLE-OVERLAY-RS-FREE-AUDIT.md).
- **3628 — freeTxtFile globals rs_free:**
  `0x8009ECA0` is the matching `loadTxtFile` `$a1==0`
  `rs_malloc`; `0x8009ECA8` is the matching `$a1!=0`
  `rs_malloc`. Each free NULL-skips and both words NULL
  after. `0x8009ECA4` is the `findAssetAcrossSegments`
  handle, torn down when not `-1`. `getGameOrFrontText` /
  `getVoiceText` load the words as table bases and do not
  free them. Four destructor callers; reload paths free
  first. This selects `H-NextClassComplete`. See
  [M3-S3628-FREE-TXT-FILE-RS-FREE-AUDIT.md](M3-S3628-FREE-TXT-FILE-RS-FREE-AUDIT.md).
- **3627 — loadSpriteSheetTextureFrames inlined-malloc rs_free:**
  `$s2` is the matching inlined `load_asset` `rs_malloc`.
  Never stored. The 8-iter walk plus `0x20`/`0x24($s2+4)`
  stores relocate interior words into the buffer; the frame
  loop `sprintf`/`rs_strcpy`/`registerHmtTextureInTable`
  copies pixels and keeps texture-id halfwords. One
  generated caller; one `jr $ra` after the free. Format
  jump table and `blez $s4` still reach the free. This
  selects `H-NextClassComplete`. See
  [M3-S3627-LOAD-SPRITE-SHEET-TEXTURE-FRAMES-RS-FREE-AUDIT.md](M3-S3627-LOAD-SPRITE-SHEET-TEXTURE-FRAMES-RS-FREE-AUDIT.md).
- **3626 — loadAndRelocateAsset load_asset rs_free:**
  `$s1` is the matching `load_asset` `rs_malloc`. Never
  stored. The 8-iter walk plus `0x20`/`0x24($s1+4)` stores
  relocate interior words into the buffer;
  `registerHmtTextureInTable` copies pixels and keeps a
  texture id. Ten generated callers; one `jr $ra` after
  the free. This selects `H-NextClassComplete`. See
  [M3-S3626-LOAD-AND-RELOCATE-ASSET-RS-FREE-AUDIT.md](M3-S3626-LOAD-AND-RELOCATE-ASSET-RS-FREE-AUDIT.md).
- **3625 — loadExplosionTextures load_asset rs_free:**
  `$a0` is the matching `load_asset("smkexp_PAL")`
  `rs_malloc`. Never stored. The 16-iter walk copies RGB
  into `0x801398C0`/`0x80139920`; spawn consumers pass
  those table addresses and do not free the heap pointer.
  One generated caller; one `jr $ra` after the free.
  `funcs_13.c` `jal rs_free` is exhausted. This selects
  `H-NextClassComplete`. See
  [M3-S3625-LOAD-EXPLOSION-TEXTURES-RS-FREE-AUDIT.md](M3-S3625-LOAD-EXPLOSION-TEXTURES-RS-FREE-AUDIT.md).
- **3624 — freeEffectAssetBuffers globals rs_free:**
  `0x8013961C` is the matching `load_asset` `rs_malloc`
  store; `0x80139740` is the matching `rs_malloc(0x400)`.
  Cue-table and spawn consumers load those words and do
  not free them. One generated destructor; no NULL skip
  or post-free NULL. Two mutually exclusive
  `mainGameLoop` teardown arms. This selects
  `H-NextClassComplete`. See
  [M3-S3624-FREE-EFFECT-ASSET-BUFFERS-RS-FREE-AUDIT.md](M3-S3624-FREE-EFFECT-ASSET-BUFFERS-RS-FREE-AUDIT.md).
- **3623 — loadSkyHorizonHob stack-scratch rs_free:**
  `0x84($sp)` is the matching `rs_malloc($s4&0xFFFF)` packed
  copy; `$sp+0x10[i]` is the matching 16-iter
  `rs_malloc((0xC($s6)<<1))`. Fill/work loops load those
  pointers as buffer bases and do not store a second pointer.
  The epilogue frees the packed buffer then the 16 slots.
  One generated caller; one `jr $ra`. This selects
  `H-NextClassComplete`. See
  [M3-S3623-LOAD-SKY-HORIZON-HOB-RS-FREE-AUDIT.md](M3-S3623-LOAD-SKY-HORIZON-HOB-RS-FREE-AUDIT.md).
- **3622 — cinematicSplineWalkerNpcHandler nested rs_free:**
  `0xF00($s2)` is `loadTopCloudsAsset` `rs_malloc(0x2C90)`
  on the opcode-1 0xF14 body. Wrapper `+0x2B44` is
  `loadAssetAndIterateSubchunks` `rs_malloc((chunk_count+1)<<1)`
  with `$a2=0`; the DMA `$s6` is freed inside that callee.
  Opcode 2 frees the table then the wrapper. Inner
  `wrapper+i*0x5C+0xF00` zeros and `0x80112B44` are different
  words. This selects `H-NextClassComplete`. See
  [M3-S3622-SPLINE-WALKER-NESTED-RS-FREE-AUDIT.md](M3-S3622-SPLINE-WALKER-NESTED-RS-FREE-AUDIT.md).
- **3621 — leftover spawnCutsceneObjectsFromList 0x6C store:**
  `*0x800B1900 + index*0x13C + 0x6C` is the matching
  `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)`.
  Dispatch loads it for `advanceNpcOnCurvedPath` behind the
  same bit-`0x4` gate. No `jal rs_free` receives it.
  `cutsceneActorNpcHandler` `+0x6C` is a 0x118-byte actor
  terrain-grid field. This selects `H-NextClassComplete`. See
  [M3-S3621-SPAWN-CUTSCENE-6C-RS-FREE-AUDIT.md](M3-S3621-SPAWN-CUTSCENE-6C-RS-FREE-AUDIT.md).
- **3620 — remaining NPC allocateAndInit destructor rs_free:**
  eleven remaining NPC updates each store opcode-1
  `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` on
  actor `+0xC`/`+0x3C`/`+0x7C`/`+0xA4`/`+0x8C`/`+0x54`/
  `+0x4C` and free that word on opcode 2. Probe hop-state and
  wingman steer-toward sibling `+0x3C` frees NULL after
  release. This selects `H-NextClassComplete`. See
  [M3-S3620-NPC-ALLOCATE-INIT-DESTRUCTOR-RS-FREE-AUDIT.md](M3-S3620-NPC-ALLOCATE-INIT-DESTRUCTOR-RS-FREE-AUDIT.md).
- **3619 — remaining player-craft table +0xBC rs_free:**
  nine sibling updates each store opcode-1
  `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` at
  `0xBC($s1)` and free it on opcode 2 with no NULL skip or
  post-free NULL. `$s1 = 0x80137DBC+0x2A0*index` from
  `0x0(actor)`. Index 0 aliases AT-ST slot 0 as the same
  per-player word. This selects `H-NextClassComplete`. See
  [M3-S3619-PLAYER-CRAFT-BC-RS-FREE-AUDIT.md](M3-S3619-PLAYER-CRAFT-BC-RS-FREE-AUDIT.md).
- **3618 — remaining playerAtStUpdate 0xA4/0xBC rs_free:**
  `0xA4($s2)` is the matching opcode-1 `rs_malloc(0x168)`
  template backup; `0xBC($s4)` is the matching
  `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` at
  `0x80137DBC`. Opcode 2 frees both without a NULL skip or
  post-free NULL. `npcAtStUpdate` `0xA4($s2)` is packed NPC
  fields, not this pointer. Sibling player-craft `0xBC($s1)`
  frees are now closed by s3619. This selects
  `H-NextClassComplete`. See
  [M3-S3618-PLAYER-ATST-A4-BC-RS-FREE-AUDIT.md](M3-S3618-PLAYER-ATST-A4-BC-RS-FREE-AUDIT.md).
- **3617 — remaining actor +0x4C rs_free:**
  `0x4C($s1)` / `0x4C($s2)` are the matching
  `allocateAndInitCraftNpcContext` `rs_malloc(0x1E4)` stores
  from opcode 1. AT-ST lethal opcode 5 NULLs after its free;
  teardown NULL-skips. `destroyNpcSlotByIndex` sends opcode 2
  once then free-lists the wrapper. AT-AT teardown does not
  NULL; that is a dangling word on a detached actor, not a
  second pointer source. This selects `H-NextClassComplete`.
  See
  [M3-S3617-ACTOR-4C-RS-FREE-AUDIT.md](M3-S3617-ACTOR-4C-RS-FREE-AUDIT.md).
- **3616 — remaining tickMultiPartVoiceLine rs_free of $s0:**
  `$s0` is `$a0` of the tick. The only allocator is
  `mallocVoiceLineStruct` `rs_malloc(0x24)`, stored at
  `0x800CDA18`, `0x800CDFB0`, or `0x800CF154`. All four tick
  callers NULL the slot on return 1. Menu malloc1 and the
  three screen-init zeros can leak a live line; the
  fade-complete path can return 1 without freeing. Neither
  is a second pointer source. This selects
  `H-NextClassComplete`. See
  [M3-S3616-TICK-VOICE-LINE-RS-FREE-AUDIT.md](M3-S3616-TICK-VOICE-LINE-RS-FREE-AUDIT.md).
- **3615 — remaining model-viewer mesh-chain rs_free:**
  `0x5C(node)` is the matching `rs_malloc($s4)` (aliased at
  `0x24`, wrap-retry `rs_free` then NULL); `$s1` is the
  matching `rs_malloc(0x60)` linked at `0x10($sp+0x40)`;
  `0x800D0110` is the matching `rs_malloc(count*56)`.
  `runModelViewerLoop` pairs one `buildModelViewerTextPage`
  with one `freeModelViewerMeshChain`. This selects
  `H-NextClassComplete`. See
  [M3-S3615-MODEL-VIEWER-MESH-CHAIN-RS-FREE-AUDIT.md](M3-S3615-MODEL-VIEWER-MESH-CHAIN-RS-FREE-AUDIT.md).
- **3614 — remaining shutdownModelViewer header-word rs_free:**
  `0x800D0360`/`0x800D0364` are the two `allocateSlotTable(8)`
  headers; `0x800D03CC` is `loadDatFile`'s `load_asset` return
  or NULL. `runModelViewerLoop` pairs one init with one shutdown.
  Header frees skip `destroyLookupTable` and leak `0x0(header)`.
  This selects `H-NextClassComplete`. See
  [M3-S3614-MODEL-VIEWER-HEADER-RS-FREE-AUDIT.md](M3-S3614-MODEL-VIEWER-HEADER-RS-FREE-AUDIT.md).
- **3613 — remaining lookup-table rs_free:** rebuild scratch is
  `rs_malloc(0x400)` in `$a0`, freed at `0x800645AC`; `0x0($a0)`
  is the returned list head. `destroyLookupTable` frees
  `0x0(header)` then the header from `allocateSlotTable` and has
  no generated caller. `shutdownModelViewer`'s header-word frees
  were the next class and are now closed. This selects
  `H-NextClassComplete`. See
  [M3-S3613-LOOKUP-TABLE-RS-FREE-AUDIT.md](M3-S3613-LOOKUP-TABLE-RS-FREE-AUDIT.md).
- **3612 — remaining loadCharTextureSet DMA-array rs_free:** the
  8-slot stack array at `$sp+0xB8` is zero-init, then each live
  slot is `rs_malloc` of `get_asset_size_extra` for `fonts/%s%s`
  (`_mm%ld` suffix on slots 1..n). `0x80061910` frees nonzero
  slots and NULLs them. Helpers do not `jal rs_free`. This selects
  `H-NextClassComplete`. See
  [M3-S3612-LOADCHAR-DMA-ARRAY-RS-FREE-AUDIT.md](M3-S3612-LOADCHAR-DMA-ARRAY-RS-FREE-AUDIT.md).
- **3611 — remaining load_asset-then-free clones:** hangar `$s4`
  and font `$s0` are matching `load_asset` returns. Neither is
  stored to a global; callers read texture-id halfwords. Sequential
  double-free is blocked by rebuild-before-next-free. This selects
  `H-NextClassComplete`. See
  [M3-S3611-LOAD-ASSET-THEN-FREE-AUDIT.md](M3-S3611-LOAD-ASSET-THEN-FREE-AUDIT.md).
- **3610 — remaining texture-scratch rs_free class:** backdrop
  scratch `0x60($sp)` and cinematic/craft scratch `0x38($sp)` are
  matching `rs_malloc` stores on the callee stack. Backdrop
  `+0x10` is a matching `load_asset` malloc; `+0x10` is NULLed
  after its free. Callers read `+0xC`/`+0x14`. This selects
  `H-NextClassComplete`. See
  [M3-S3610-TEXTURE-SCRATCH-RS-FREE-AUDIT.md](M3-S3610-TEXTURE-SCRATCH-RS-FREE-AUDIT.md).
- **3609 — remaining text-texture rs_free class:** named scratch
  `0x60($sp)` and text-target scratch `0x38($sp)` are matching
  `rs_malloc` stores on the callee stack. Named `+0x10` and
  blueprint `$s1` are matching `load_asset` mallocs; `+0x10` is
  NULLed after its free. Callers read `+0xC`/`+0x14`. This selects
  `H-NextClassComplete`. See
  [M3-S3609-TEXT-TEXTURE-RS-FREE-AUDIT.md](M3-S3609-TEXT-TEXTURE-RS-FREE-AUDIT.md).
- **3608 — remaining format-message rs_free class:** glyph `+0x38`
  is always `rs_malloc` after a 0x34-byte memset; `+0x3C` is that
  malloc only when `0x1C&6`, otherwise memset-zero and both frees
  skip. `$s3` is `enqueueFormatMessage`'s `rs_malloc(0x60)`; the
  only generated send to the worker is that enqueue. Tick never
  calls dispose; dispose's callers never enqueue. This selects
  `H-NextClassComplete`. See
  [M3-S3608-FORMAT-MESSAGE-RS-FREE-AUDIT.md](M3-S3608-FORMAT-MESSAGE-RS-FREE-AUDIT.md).
- **3607 — remaining speech-file rs_free class:** `$s0` is
  `rs_malloc(4, 8)` then `rs_free($s0)` after copying the count to
  `0x80154670`. `0x80154674` is the `initMusyXVoiceTable` malloc
  store; shutdown frees it unchecked. `0x8015467C` is either the
  DMA `rs_malloc(count<<2)` or KSEG0 `a0+4`; both frees skip when
  `0x800A5120 == 0`, and that flag is set only after the DMA store.
  Sequential double-free is blocked by generated init/finalize
  pairing. This selects `H-NextClassComplete`. See
  [M3-S3607-SPEECH-FILE-RS-FREE-AUDIT.md](M3-S3607-SPEECH-FILE-RS-FREE-AUDIT.md).
- **3606 — remaining speech/cache rs_free class:** `-0x64AC`/
  `-0x64B0`/`-0x64B4` are `loadSndFiles` stores of
  `load_asset_with_malloc_flags` `rs_malloc`; cinematic wait is
  skipped by `0x80130B39`, and the other waits pair a matching
  load. Cache `+0x4` is the `loadSongAssetByName` malloc store;
  free-all marks the key `-1`. `-0x648C` is init-zero on every
  generated `initSpeechSubsystem`. This selects
  `H-NextClassComplete`. See
  [M3-S3606-SPEECH-CACHE-RS-FREE-AUDIT.md](M3-S3606-SPEECH-CACHE-RS-FREE-AUDIT.md).
- **3605 — skipped-NULL destructor-free class:** `-0x6898` is the
  matching `rs_malloc(0x48)` from `buildSongTempoSchedule`; every
  destructor and `freeAudioScratchBuffer` NULLs the slot then
  `rs_free` delay-slot zero. `-0x6890` is the matching
  `initN64RspMixer` malloc store, freed after a NULL skip with no
  post-free NULL; sequential double-free is blocked by B40.
  Wrapper `-0x50EC` has no original writer. This selects
  `H-NextClassComplete`. See
  [M3-S3605-SKIPPED-NULL-DESTRUCTOR-FREE-AUDIT.md](M3-S3605-SKIPPED-NULL-DESTRUCTOR-FREE-AUDIT.md).
- **3604 — destructor unchecked-free class:** ten remaining
  `lw a0; jal rs_free` sites with no zero-skip and no post-free NULL.
  Each pointer has a single original `0x8015` writer that stores the
  matching `rs_malloc` result (`allocateSongChannelArray`,
  `setupSongRenderBuffers`, `buildSongDecodeBufferRing`,
  `initSampleStreamBlockCache`, `runAiAudioStreamPlaybackLoop` word 0
  of the `-0x6950` slice table, `initAudioSubsystem`). Sequential
  double-free of the six shared words is blocked by B40. This selects
  `H-NextClassComplete`. See
  [M3-S3604-DESTRUCTOR-UNCHECKED-FREE-AUDIT.md](M3-S3604-DESTRUCTOR-UNCHECKED-FREE-AUDIT.md).
- **3603 — `-0x6904` pointer alias:** six original `lw`/`sw` sites. The
  only writer is `allocateSongChannelArray` storing the `rs_malloc`
  result; the init walk is count-bounded versus `-0x6900`; both
  destructors `rs_free` that same word without NULLing either alias.
  Sequential double-free is blocked by an unreferenced shutdown wrapper
  and B40 zeroing after `musyxNoopStub`. This selects
  `H-NextClassComplete`. See
  [M3-S3603-6904-POINTER-ALIAS-AUDIT.md](M3-S3603-6904-POINTER-ALIAS-AUDIT.md).
- **3602 — remaining `-0x6908` table-base users:** original loads are
  mix (count-bounded `s0` walk), synth (count-bounded `+0x88` pointer
  walk), and allocate (malloc-size store). Render, key-on, and shutdown
  have no original `-0x6908` load. This selects `H-NextClassComplete`.
  See
  [M3-S3602-REMAINING-6908-TABLE-BASE-AUDIT.md](M3-S3602-REMAINING-6908-TABLE-BASE-AUDIT.md).
- **3601 — remaining 0x88-stride voice-table indexers:** ten remaining
  consumers, including unreferenced `deactivateVoice`. Callers resolve
  to count-bounded loops versus `0x80141AD0`, `+0x67` loads behind the
  s3600 `+0x0` skip, or `allocateSynthVoice` / streamed-voice returns
  after `-1`. The speech-slot word at `0x8015462C` is that same
  allocator return, not a packed handle. This selects
  `H-NextClassComplete`. See
  [M3-S3601-REMAINING-88-STRIDE-INDEXER-AUDIT.md](M3-S3601-REMAINING-88-STRIDE-INDEXER-AUDIT.md).
- **3600 — unmasked release/fade voice-table index:** four generated
  call sites. `tickAudioChannel` opcode 17 and unreferenced
  `soundMacroOpKeyOff` load record `+0x67`; `tickAllAudioChannels` skips
  `+0x0==0`, and every `-1` handle writer also zeros `+0x0`.
  `stopAllSynthVoices` is count-bounded; `stopVoicesByHandle` fades the
  matched live slot after rejecting full-word `-1`. Consumers still lack
  a local count check. This selects `H-NextClassComplete`. See
  [M3-S3600-RELEASE-FADE-INDEX-AUDIT.md](M3-S3600-RELEASE-FADE-INDEX-AUDIT.md).
- **3599 — MusyX voice `+0x5C`/`+0x64` envelope companion audit:** 36
  generated accesses in `funcs_23.c`/`funcs_24.c` split across voice-table
  envelope floats, command-list sample halfword/word fields, and the
  `0x17C` packed handle. The envelope writer/consumer chain including
  `advanceVolumeFadeEnvelope` is now identified; mix's `+0x0` gate covers
  init's missing envelope stores. No concrete invalid writer/value was
  found. This selects `H-NextClassUnevaluable`. See
  [M3-S3599-VOICE-5C-64-ENVELOPE-AUDIT.md](M3-S3599-VOICE-5C-64-ENVELOPE-AUDIT.md).
- **3598 — MusyX voice `+0x66..+0x74` publication audit:** 15 stores, 12
  loads, and 3 `+0x6D` byte reads were enumerated. Command-list halfwords
  are render copies of voice-table volumes consumed by key-on; voice-table
  `+0x6D`/`+0x6C`/`+0x68` are decode-mode and envelope fields. No concrete
  invalid writer/value was found. This selects `H-NextClassUnevaluable`.
  See
  [M3-S3598-VOICE-66-74-PUBLICATION-AUDIT.md](M3-S3598-VOICE-66-74-PUBLICATION-AUDIT.md).
- **3571–3576 — source/input boundary:** port zero-fill from
  `0x800078EC` preceded a zero first target DMA; retail independently
  reached `0x800078E0` with varied lengths, not the port tuple.
  Sessions 3573–3575 were unevaluable for parity/order (caller watch
  not retained). Full notes remain in the evidence index.
- **3563–3570 — source/output chain:** target image-stage and source-range
  DMAs completed, but payloads were zero; the immediate observed writer was a
  legitimate zero-valued DMA/writeback. No missing dispatch or completion was
  established.
- **3532–3535 — AI-frequency contract:** retail and port shared input
  `0x5622`; retail's correct NTSC rounding returned/stored `0x561F`, and the
  host path was corrected and validated. This boundary is closed.

New soak verdicts read at maintenance time added no post-3577 result; the
tail contained older queued outcomes only.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. The image task is the real-audio
arm; the silent arm returns `RspExitReason::Broke`. Do not infer audio behavior
from a route that fails to reach the target phase.

Every instrument needs an independent ground-truth request, a same-run
positive control, a phase-scoped budget, and two evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build and run. A counter is not a control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

The runtime facts that remain operationally important are: Factor 5 custom
opcodes are documented in `docs/factor5-gbi.md`; MusyX task data cannot be sent
to stock `aspMain`; DP messages use the external-message drain; C++ exceptions
must propagate to the outer recovery boundary; and RT64's interpreter safety
limit prevents a missing DL terminator from becoming an access violation.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm; completion-aware default behavior returns from the attract viewer. The
old interpretation of the cinematic pool as an audio-slot pool was superseded
by the MusyX voice-table measurement.

The claim that `0x8002BEEC` is the retail JAL dispatch to `0x800078EC` is
route-dependent and unreconciled. Later adjacent-PC captures found zero at
both addresses while `0x800078EC` was live; do not treat it as a writer without
a new independent discriminator.

Sessions 3512 and 3516 selected non-observable predecessor watches. Their
positive stores/controls remain useful, but the absent predecessor rows are
capture-invalid and do not establish parity, divergence, or mutation.

The s3585 description of `voice_record+0x64` as a standalone slot index is
superseded by s3586's writer audit: the field is a packed handle; only its low
byte indexes the voice table. The writer list still found no concrete invalid
low byte, so the runtime allocator/lifetime boundary remains open.

## Evidence index

Latest boundary notes:

- [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md)
- [M3-S3647-REINSERT-NPC-SORTED-FREE-LIST-RS-FREE-AUDIT.md](M3-S3647-REINSERT-NPC-SORTED-FREE-LIST-RS-FREE-AUDIT.md)
- [M3-S3646-FREE-NPC-SLOT-ARRAY-RS-FREE-AUDIT.md](M3-S3646-FREE-NPC-SLOT-ARRAY-RS-FREE-AUDIT.md)
- [M3-S3645-DESTROY-NPC-CONTEXT-ARRAYS-RS-FREE-AUDIT.md](M3-S3645-DESTROY-NPC-CONTEXT-ARRAYS-RS-FREE-AUDIT.md)
- [M3-S3644-FREE-NPC-BURST-SPAWNER-TABLES-RS-FREE-AUDIT.md](M3-S3644-FREE-NPC-BURST-SPAWNER-TABLES-RS-FREE-AUDIT.md)
- [M3-S3643-COMPUTE-GRID-TILE-EDGE-ADJACENCY-MASKS-RS-FREE-AUDIT.md](M3-S3643-COMPUTE-GRID-TILE-EDGE-ADJACENCY-MASKS-RS-FREE-AUDIT.md)
- [M3-S3642-TEARDOWN-ANIMATED-MAP-GRID-LAYER-RS-FREE-AUDIT.md](M3-S3642-TEARDOWN-ANIMATED-MAP-GRID-LAYER-RS-FREE-AUDIT.md)
- [M3-S3641-TEARDOWN-GRID-LAYER-WORKER-RS-FREE-AUDIT.md](M3-S3641-TEARDOWN-GRID-LAYER-WORKER-RS-FREE-AUDIT.md)
- [M3-S3640-FREE-GRID-CELL-BUFFERS-RS-FREE-AUDIT.md](M3-S3640-FREE-GRID-CELL-BUFFERS-RS-FREE-AUDIT.md)
- [M3-S3639-LOAD-LEVEL-TEXTURE-CACHE-RS-FREE-AUDIT.md](M3-S3639-LOAD-LEVEL-TEXTURE-CACHE-RS-FREE-AUDIT.md)
- [M3-S3638-FREE-LEVEL-DAT-BUFFERS-RS-FREE-AUDIT.md](M3-S3638-FREE-LEVEL-DAT-BUFFERS-RS-FREE-AUDIT.md)
- [M3-S3637-LOAD-FULL-HEADER-IMAGE-RS-FREE-AUDIT.md](M3-S3637-LOAD-FULL-HEADER-IMAGE-RS-FREE-AUDIT.md)
- [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md)
- [M3-S3635-LOAD-ASSET-INTO-NEW-SLOT-RS-FREE-AUDIT.md](M3-S3635-LOAD-ASSET-INTO-NEW-SLOT-RS-FREE-AUDIT.md)
- [M3-S3634-FREE-ANIMATION-PHASE-POOL-RS-FREE-AUDIT.md](M3-S3634-FREE-ANIMATION-PHASE-POOL-RS-FREE-AUDIT.md)
- [M3-S3633-LOAD-ASSET-ITERATE-SUBCHUNKS-RS-FREE-AUDIT.md](M3-S3633-LOAD-ASSET-ITERATE-SUBCHUNKS-RS-FREE-AUDIT.md)
- [M3-S3632-FREE-ALL-HOB-FILES-RS-FREE-AUDIT.md](M3-S3632-FREE-ALL-HOB-FILES-RS-FREE-AUDIT.md)
- [M3-S3631-RELEASE-MESH-ASSET-RS-FREE-AUDIT.md](M3-S3631-RELEASE-MESH-ASSET-RS-FREE-AUDIT.md)
- [M3-S3630-LOAD-HMT-AND-HOB-RS-FREE-AUDIT.md](M3-S3630-LOAD-HMT-AND-HOB-RS-FREE-AUDIT.md)
- [M3-S3629-FREE-SUBTITLE-OVERLAY-RS-FREE-AUDIT.md](M3-S3629-FREE-SUBTITLE-OVERLAY-RS-FREE-AUDIT.md)
- [M3-S3628-FREE-TXT-FILE-RS-FREE-AUDIT.md](M3-S3628-FREE-TXT-FILE-RS-FREE-AUDIT.md)
- [M3-S3627-LOAD-SPRITE-SHEET-TEXTURE-FRAMES-RS-FREE-AUDIT.md](M3-S3627-LOAD-SPRITE-SHEET-TEXTURE-FRAMES-RS-FREE-AUDIT.md)
- [M3-S3626-LOAD-AND-RELOCATE-ASSET-RS-FREE-AUDIT.md](M3-S3626-LOAD-AND-RELOCATE-ASSET-RS-FREE-AUDIT.md)
- [M3-S3625-LOAD-EXPLOSION-TEXTURES-RS-FREE-AUDIT.md](M3-S3625-LOAD-EXPLOSION-TEXTURES-RS-FREE-AUDIT.md)
- [M3-S3624-FREE-EFFECT-ASSET-BUFFERS-RS-FREE-AUDIT.md](M3-S3624-FREE-EFFECT-ASSET-BUFFERS-RS-FREE-AUDIT.md)
- [M3-S3623-LOAD-SKY-HORIZON-HOB-RS-FREE-AUDIT.md](M3-S3623-LOAD-SKY-HORIZON-HOB-RS-FREE-AUDIT.md)
- [M3-S3622-SPLINE-WALKER-NESTED-RS-FREE-AUDIT.md](M3-S3622-SPLINE-WALKER-NESTED-RS-FREE-AUDIT.md)
- [M3-S3621-SPAWN-CUTSCENE-6C-RS-FREE-AUDIT.md](M3-S3621-SPAWN-CUTSCENE-6C-RS-FREE-AUDIT.md)
- [M3-S3620-NPC-ALLOCATE-INIT-DESTRUCTOR-RS-FREE-AUDIT.md](M3-S3620-NPC-ALLOCATE-INIT-DESTRUCTOR-RS-FREE-AUDIT.md)
- [M3-S3619-PLAYER-CRAFT-BC-RS-FREE-AUDIT.md](M3-S3619-PLAYER-CRAFT-BC-RS-FREE-AUDIT.md)
- [M3-S3618-PLAYER-ATST-A4-BC-RS-FREE-AUDIT.md](M3-S3618-PLAYER-ATST-A4-BC-RS-FREE-AUDIT.md)
- [M3-S3617-ACTOR-4C-RS-FREE-AUDIT.md](M3-S3617-ACTOR-4C-RS-FREE-AUDIT.md)
- [M3-S3616-TICK-VOICE-LINE-RS-FREE-AUDIT.md](M3-S3616-TICK-VOICE-LINE-RS-FREE-AUDIT.md)
- [M3-S3615-MODEL-VIEWER-MESH-CHAIN-RS-FREE-AUDIT.md](M3-S3615-MODEL-VIEWER-MESH-CHAIN-RS-FREE-AUDIT.md)
- [M3-S3614-MODEL-VIEWER-HEADER-RS-FREE-AUDIT.md](M3-S3614-MODEL-VIEWER-HEADER-RS-FREE-AUDIT.md)
- [M3-S3613-LOOKUP-TABLE-RS-FREE-AUDIT.md](M3-S3613-LOOKUP-TABLE-RS-FREE-AUDIT.md)
- [M3-S3612-LOADCHAR-DMA-ARRAY-RS-FREE-AUDIT.md](M3-S3612-LOADCHAR-DMA-ARRAY-RS-FREE-AUDIT.md)
- [M3-S3611-LOAD-ASSET-THEN-FREE-AUDIT.md](M3-S3611-LOAD-ASSET-THEN-FREE-AUDIT.md)
- [M3-S3610-TEXTURE-SCRATCH-RS-FREE-AUDIT.md](M3-S3610-TEXTURE-SCRATCH-RS-FREE-AUDIT.md)
- [M3-S3609-TEXT-TEXTURE-RS-FREE-AUDIT.md](M3-S3609-TEXT-TEXTURE-RS-FREE-AUDIT.md)
- [M3-S3608-FORMAT-MESSAGE-RS-FREE-AUDIT.md](M3-S3608-FORMAT-MESSAGE-RS-FREE-AUDIT.md)
- [M3-S3607-SPEECH-FILE-RS-FREE-AUDIT.md](M3-S3607-SPEECH-FILE-RS-FREE-AUDIT.md)
- [M3-S3606-SPEECH-CACHE-RS-FREE-AUDIT.md](M3-S3606-SPEECH-CACHE-RS-FREE-AUDIT.md)
- [M3-S3605-SKIPPED-NULL-DESTRUCTOR-FREE-AUDIT.md](M3-S3605-SKIPPED-NULL-DESTRUCTOR-FREE-AUDIT.md)
- [M3-S3604-DESTRUCTOR-UNCHECKED-FREE-AUDIT.md](M3-S3604-DESTRUCTOR-UNCHECKED-FREE-AUDIT.md)
- [M3-S3603-6904-POINTER-ALIAS-AUDIT.md](M3-S3603-6904-POINTER-ALIAS-AUDIT.md)
- [M3-S3602-REMAINING-6908-TABLE-BASE-AUDIT.md](M3-S3602-REMAINING-6908-TABLE-BASE-AUDIT.md)
- [M3-S3601-REMAINING-88-STRIDE-INDEXER-AUDIT.md](M3-S3601-REMAINING-88-STRIDE-INDEXER-AUDIT.md)
- [M3-S3600-RELEASE-FADE-INDEX-AUDIT.md](M3-S3600-RELEASE-FADE-INDEX-AUDIT.md)
- [M3-S3599-VOICE-5C-64-ENVELOPE-AUDIT.md](M3-S3599-VOICE-5C-64-ENVELOPE-AUDIT.md)
- [M3-S3598-VOICE-66-74-PUBLICATION-AUDIT.md](M3-S3598-VOICE-66-74-PUBLICATION-AUDIT.md)
- [M3-S3597-VOICE-18-24-FIELD-AUDIT.md](M3-S3597-VOICE-18-24-FIELD-AUDIT.md)
- [M3-S3592-MORT-PUBLICATION-IDIOM-AUDIT.md](M3-S3592-MORT-PUBLICATION-IDIOM-AUDIT.md)

- [M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md](M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md)
- [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md)
- [M5-S3576-RETAIL-ZERO-FILL-PREDECESSOR.md](M5-S3576-RETAIL-ZERO-FILL-PREDECESSOR.md)
- [M5-S3573-ZERO-FILL-CONTRACT.md](M5-S3573-ZERO-FILL-CONTRACT.md)
- [M5-S3572-SOURCE-TRANSITION-JOIN.md](M5-S3572-SOURCE-TRANSITION-JOIN.md)
- [M5-S3565-IMAGE-STAGING-SOURCE.md](M5-S3565-IMAGE-STAGING-SOURCE.md)
- [M5-S3566-SOURCE-RANGE-WRITER.md](M5-S3566-SOURCE-RANGE-WRITER.md)
- [M5-S3567-DMEM-PAYLOAD-PRODUCER.md](M5-S3567-DMEM-PAYLOAD-PRODUCER.md)
- [M5-S3564-IMAGE-DMEM-PRODUCER.md](M5-S3564-IMAGE-DMEM-PRODUCER.md)
- [M5-S3539-SOURCE-WRITER.md](M5-S3539-SOURCE-WRITER.md)
- [M5-S3536-OUTPUT-CONTRACT.md](M5-S3536-OUTPUT-CONTRACT.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3577 remain in the append-only ledger; archived boundary detail is
in `PROJECT-OVERVIEW.md` and the notes above. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
