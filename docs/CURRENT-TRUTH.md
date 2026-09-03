# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3628 (2026-09-03).

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
   and `freeTxtFile` globals `rs_free` as complete.
   Session 3628 closed `0x800558F8`/`0x80055910`:
   `0x8009ECA0`/`0x8009ECA8` are the matching `loadTxtFile`
   `rs_malloc` stores (game vs voice mode). Both frees
   NULL-skip and NULL after. `0x8009ECA4` is a
   `findAssetAcrossSegments` handle torn down, not a
   third `rs_free`. Four destructor callers. Runtime
   allocator/DMA/scene-pairing legitimacy remains unproven.
   See
   [M3-S3628-FREE-TXT-FILE-RS-FREE-AUDIT.md](M3-S3628-FREE-TXT-FILE-RS-FREE-AUDIT.md).
   Retail-entry and SP-yield threads remain parked. The next
   M3 unit is `freeSubtitleOverlay` `0x800562CC`
   (`*0x80139010`). Do not add a pointer guard without a
   concrete invalid writer.
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
| H-NextClassComplete | Selected for `freeTxtFile`: `0x8009ECA0`/`0x8009ECA8` are the matching `loadTxtFile` `rs_malloc` stores; both destructor frees NULL after. |
| H-NextClassGap | Refuted for this class: no free of a non-allocator or already-freed value; sibling `0x8009ECA4` is an asset handle, not a third `rs_free`. |
| H-NextClassUnevaluable | Not selected: one original heap-pointer writer per word. |

The current work-unit slug is `m3-next-audio-idiom-audit`.

## Recent evidence ledger

Only the latest boundary transitions are repeated here; the append-only ledger
and evidence notes retain the full history.

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
- **3585 — `stopVoicesByHandle` handle-provenance audit:** all four direct
  callers iterate the two linked-list heads and pass node `+0x8`; the visible
  constructor stores the generated handle at `+0x8` and copies
  `voice_record+0x64` to node `+0xC`. The node/layout interpretation is
  consistent, but the consumer has no local bound check on the copied slot
  index and its complete writer/lifecycle legitimacy remains unclassified.
  No guard or runtime change followed. See
  [M3-S3585-STOP-VOICES-HANDLE-AUDIT.md](M3-S3585-STOP-VOICES-HANDLE-AUDIT.md).
- **3576 — retail predecessor input:** retail `0x800052C4` reached
  `0x800078E0` with varied lengths (`0x18`, `0x3C`, `0x208`, `0x4F0`,
  `0x1008`, `0x8000`), not the port tuple. This selected an observed-edge
  input divergence.
- **3573–3575 — entry contract:** port zero-fill arguments were qualified;
  the retail entry and controls were live, but the first caller watch was
  not retained. Those runs were unevaluable for parity/order, not evidence of
  absence.
- **3571–3572 — transition join:** port nonzero initialization preceded a
  zero-fill from `0x800078EC`, and the first target source DMA carried zero.
  Retail independently showed the writer family in the source span.
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
