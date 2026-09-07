# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3659 (2026-09-07).

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
ordering remains open. The immediate producer context remains qualified, but
session 3659 found
that the stored-value divergence is not established: the oracle sampled an
aligned word after `sb`, including three bytes that instruction did not write.
Nonzero intermediate words cannot establish nonzero bytes written by memset. See
[M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md).

Do not force the cinematic flag at `0x800B0934`, bypass the state machine, or
rewrite task, audio, PCM, selector, or output state. The default route's null
stage-advancer input is a known route/configuration issue; the validated
real-audio route is the comparison arm.

## Next steps

The backlog is one monotonic sequence. Work only the first applicable item.

1. M5 Step 3: identify the live retail audio task and its source object before
   comparing physical heap addresses. The s3659 scalar-store capture refuted
   the old nonzero-memset inference: 1,844 sampled stores wrote zero, all
   matching the source register. The aligned words were nonzero in 829 cases.
   Exact DMA ordering remains open; do not add a writeback/zero-fill mitigation.
2. Keep the s3554 slot-dispatch failure parked as route-specific absence.
   Revisit only with a new route discriminator; do not add a slot guard.
3. Keep the silent-arm `fillSampleStreamRange` crash separate from the
   real-audio target path, and do not infer target behavior from it.
4. M5's exact DMA ordering remains unresolved and unavailable to the current
   oracle. While it is parked, perform only systematic M3 idiom-class audits.
   Sessions 3586–3658 closed the generated `jal rs_free` census through
   `funcs_7.c`, all of `funcs_6.c`, all of `funcs_4.c`, all of
   `funcs_2.c`, plus `processAssetLoadStep`/`mainEventQueueWorker`
   `0x48($s0)`, `findManifestEntryByName` `$s2`,
   `freeManifestSegmentAssets` `0x40($s0)`,
   `teardownAssetManifestService` `*0x80110D50`, and the earlier
   MusyX/MORT field families. `funcs_5.c`, `funcs_3.c`, and `funcs_0.c`
   have zero sites. The only remaining Gap is s3636
   `attachedMeshOverlayNpcHandler` `0x1C`/`0x20`: opcode 2 frees those
   words when setup stores type `-1` or parent mesh `+0xC` is NULL,
   without a prior NULL store. Do not re-audit a Complete class. Do not add a
   pointer guard without a concrete invalid writer. Do not land a skip-path
   NULL store for that Gap unless a later census identifies that same writer.
   The closed-class list and per-session notes live in
   [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §56.
   The next M3 unit is `rs_zcfree` `rs_free` of incoming `$a0` at
   `0x80005268` (last original `jal 0x80001C98` in `funcs_1.c`).
5. Generated-symbol renaming remains last priority. Resume only when M5 is
   closed and M3 is parked with no new discriminator.

## Active hypothesis table

| Hypothesis | Discriminating result |
|---|---|
| H-RetailWriterSame | Selected for target-phase identity/order: `0x800078EC` writes at 47.4 s before target VI at 48.5 s. |
| H-RetailWriterOther | Refuted for the target-phase write; earlier setup writers are separate activity. |
| H-RetailOrdering | Exact DMA ordering remains unmeasured. |
| H-RetailValue | Whole-word nonzero samples do not establish a nonzero byte store; s3659 measured 1,844 zero bytes with zero mismatches. |
| H-RetailProducer | `0x800052C4` is repeatedly the immediate caller of `0x800078E0`; no earlier constructor was exposed by the repeated field table. |
| H-RetailDmaOrder | No separate DMA event identifier was exposed; ordering remains open. |
| H-CaptureInvalid | Refuted for this run: whole-RDRAM, source-span, writer-PC, and target-phase controls all fired. |
| H-MortComplete | Selected structurally: the `0x8009D7D0..0x8009DD7C` path has complete bounded stages and publication edges. |
| H-MortGap | No concrete missing/invalid writer, consumer, base, or bound was found. |
| H-MortMisread | Not supported: the range is a coherent CPU voice-filter/mix/compand path. |
| H-NextClassComplete | Selected for `teardownAssetManifestService` `*0x80110D50`: one flags-0x81 extra-heap malloc store / one destructor with original NULL skip; generated boot caller passes size 0 so the malloc is an unreferenced original branch. |
| H-NextClassGap | Refuted for this `*0x80110D50`. Remains selected for overlay `0x1C`/`0x20` (s3636). |
| H-NextClassUnevaluable | Not selected: one word, one malloc store, one destructor. |

The current work-unit slug is `m5-audio-source-ownership`.

## Recent evidence ledger

- **3659 — corrected store-width evidence:** all 1,844 sampled retail memset
  stores were zero with zero mismatches, despite 829 nonzero containing words.
  Oracle build and UBSan regression tests passed. Both title/hangar controls
  fired. See [M5-S3659-SCALAR-STORE-EVIDENCE.md](M5-S3659-SCALAR-STORE-EVIDENCE.md).

Only the latest boundary transitions are repeated here; the append-only ledger
and evidence notes retain the full history. Sessions 3586–3657 M3 class
closeouts are archived in PROJECT-OVERVIEW §56.

- **3658 — teardownAssetManifestService rs_free of *0x80110D50:**
  Live writer is `initDmaSlots` flags-0x81 `rs_malloc($s3)`
  store at `0x80004708`. Flag-zero path stores NULL. The only
  generated `initDmaSlots` caller is boot `0x800011EC` with
  `$a0 = 0`, so the malloc is an unreferenced original branch.
  Destructor `0x80005000` has an original NULL skip and zero
  generated callers. `initRsMallocHeap` and `*0x80111260` are
  consumers. Adjacent `0xD48`/`0xD4C`/`0xD54` are size and
  worker-handle words. This selects `H-NextClassComplete`. See
  [M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md](M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md).
- **3657 — freeManifestSegmentAssets rs_free of 0x40($s0):** `$s0`
  is `0x80110A80 + idx*0x50`. Live writer is flags-9
  `rs_malloc` store at `0x80004920`. Two mutually exclusive
  destructors (`$a0 == -1` gated by `0x4E==1`; else single-slot).
  Post-free clears `0x4E`, not `0x40`. `find_manifest_entry`
  `0x80003AC8` walks the payload as a directory. ROM name-table
  `+0x18` is 0; skip does not fire. Six generated callers pass the
  find return or leftover `*0x80137CFC`. This selects
  `H-NextClassComplete`. See
  [M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md](M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md).
- **3656 — findManifestEntryByName rs_free of $s2:** `$s2` is
  flags-9 `rs_malloc(8)` at `0x800048A4`, never stored. DMA dest then
  destructor `0x8000490C`; delay-slot `lw $s2, 0x0($a0)` consumes
  header word 0 as a ROM offset (`$a0` still the malloc). Skip when
  name-table `+0x18 != 0` leaks the unpublished 8-byte buffer; that
  word is ROM-DMA'd by `initDmaSlots`, not this pointer. Slot `+0x40`
  is the later payload malloc. This selects `H-NextClassComplete`. See
  [M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md](M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md).
- **3655 — processAssetLoadStep rs_free of 0x48($s0):** `$s0` is
  `D_80110D60 + (*0x80111240)*0x74`. Live writers are flags-9
  `rs_malloc(0x10)` at `0x80003EA0`/`0x80003F0C` and
  `rs_malloc(0x1000)` at `0x80003FC4`. Type-2 enqueue NULLs the word.
  In-step destructor `0x80003E7C` frees the 0x10 buffer and NULLs;
  caller `0x8000450C` frees leftover (0x1000 or already-NULL).
  `0x10($s0)` is z_stream `next_in`, not a sibling free. This selects
  `H-NextClassComplete`. See
  [M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md](M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md).
- **3653 — initSaveData rs_free of $s2 and freeSaveDataBuffer *0x80112724:**
  `$s2` is flags-8 `rs_malloc(*0x801126C4)` at `0x800065E0`, never
  stored to a global. Two mutually exclusive frees.
  `*0x80112724` is flags-0x81 `rs_malloc` stored at `0x800063D0`;
  remaining loads are consumers. Re-init leaks; it is not a second
  free. See
  [M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md](M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md).
- **3652 — freeRenderSubsystemResources rs_free of *0x8011A444 and four siblings:**
  Live writers are `buildAndRegisterDefaultMaterial` flags-0 `rs_malloc`
  stores at `0x80017D28` / `0x80017D4C` / `0x80017D80` / `0x80017E64` /
  `0x80017E74`. One destructor wrapper; host
  `MATERIAL_ARRAY_PTR_GUARD` is not an original skip. `funcs_4.c`
  `jal rs_free` is exhausted. See
  [M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md](M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md).
- **3651 — uploadTextureDescriptorData rs_free of $s1:**
  `$s1` is incoming `$a1`, the delay-slot interior
  `0x0($s2) + (*(*s2+0xC)*($s1&0xFFFF)+0x14)` of the
  `loadAssetIntoNewSlot` converted-buffer malloc at
  `0x80054970`. Only generated caller is
  `tickWrappingTimerAccumulatorList`. Byte 2 of that
  header is 0 (`fillTextureDescriptorNoCopy` /
  dest-already-set `loadAndDecodeTexture`).
  `copyTextureDescriptorWithData` (the malloc-and-set-1
  clone) is unreferenced. Original byte-2 skip is taken;
  the interior is never passed to `rs_free`. Matching
  destructor of the header is `freeAnimationPhasePool`
  (closed s3634), a different pointer. This selects
  `H-NextClassComplete`. See
  [M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md](M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md).
- **3650 — destroyTextureLUTs rs_free of *0x80128F08 / *0x80128EFC:**
  Live writers are `initTextureLUTAndAllocBuffers` flags-0
  `rs_malloc` stores at `0x8001E274` / `0x8001E290`.
  `initTextureMaterialPools` is an unreferenced clone.
  One destructor pair. Host TEXDATA substitutions are not
  original skips. See
  [M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md](M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md).
- **3649 — maintenance compaction:** `docs/CURRENT-TRUTH.md` exceeded the
  60,000-byte trigger (60,386 bytes / 1,020 lines). Closed M3 `rs_free`
  session-by-session narrative was migrated to PROJECT-OVERVIEW §56; the
  live next unit is unchanged. Soak-queue tail added no post-3577 result.
- **3648 — loadDebugAssets rs_free of $s0:** `$s0` is the matching
  `get_asset_size_extra` `rs_malloc($s2, 8)` at `0x80024768`. Never stored
  to a global. Incoming `$s3` is `*0x8010E008`. The ROM string at
  `0x80000A48` is overwritten before the free. DMA slot `+0x24` is dest
  only; `teardownAssetDma` does not `jal rs_free`.
  `registerHmtTextureInTable` copies pixels and keeps a texture-id
  halfword at `0x80128F22`. One destructor; `-1` skip is paired. Two
  generated callers; zero overlay lookup. One `jr $ra`. `funcs_7.c`
  `jal rs_free` is exhausted. This selects `H-NextClassComplete`. See
  [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md).
- **3636 — attachedMeshOverlayNpcHandler rs_free of 0x1C($s0):** `$s0` is
  `$s2=0x4($s1)` on opcode 2. The only heap-pointer writer of `0x1C`/`0x20`
  is `dispatchOverlaySetupByParentAssetName` `rs_malloc(0x80, 0)` at
  `0x80053DBC` (two-iter `+0x4` walk). Unmatched parent name stores type
  `-1` and skips that loop; NULL parent mesh skips setup. Opcode 2 still
  frees both words with no NULL store. Sibling `freeListEntryPointers` is
  unreferenced. Nine player-craft `spawnNpcOfType` sites. This selects
  `H-NextClassGap`. See
  [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md).
- **3584 — retail source-buffer writer:** all three watches and the target
  phase fired; source-buffer writes were mixed, with 176 phase hits at
  `0x800078EC` and no stable distinct constructor/DMA PC. The
  earlier-constructor boundary is unavailable to this oracle; exact DMA
  ordering remains open. See
  [M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md).
- **3577–3583 — source/input and retail writer/producer:** retail controls
  fired. Target-phase source span was written by `0x800078EC` at 47.4 s
  before the first 512-wide target VI at 48.5 s. The joined tuple is
  `0x800052C4 -> 0x800078E0 -> 0x800078EC` with changing buffer/length
  values and nonzero post-store words, unlike the port's
  `0x801797B0/0/0x298` zero-fill. No independent DMA event identifier was
  exposed. See [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md),
  [M5-S3581-RETAIL-SOURCE-PRODUCER.md](M5-S3581-RETAIL-SOURCE-PRODUCER.md),
  [M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md](M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md),
  [M5-S3583-RETAIL-PRODUCER-REPEAT.md](M5-S3583-RETAIL-PRODUCER-REPEAT.md).
- **3571–3576 — source/input boundary:** port zero-fill from `0x800078EC`
  preceded a zero first target DMA; retail independently reached
  `0x800078E0` with varied lengths, not the port tuple. Sessions 3573–3575
  were unevaluable for parity/order (caller watch not retained).
- **3563–3570 — source/output chain:** target image-stage and source-range
  DMAs completed, but payloads were zero; the immediate observed writer was
  a legitimate zero-valued DMA/writeback. No missing dispatch or completion
  was established.
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

The s3579–s3584 inference of a retail-versus-port stored-value divergence at
`0x800078EC` is unsupported. The retail ROM instruction is `sb $a1, 0($v0)`
(`0xA0450000` at ROM offset `0x84EC`), but the oracle read the entire aligned
word. A byte zero-fill legitimately leaves nonzero neighboring bytes until
later stores clear them. The new scalar-store samples distinguish this case.

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

Latest boundary notes. Remaining M3 `rs_free` notes for s3586–s3657 stay on
disk and are indexed in PROJECT-OVERVIEW §56; do not treat absence here as
deletion.

- [M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md](M3-S3658-TEARDOWN-ASSET-MANIFEST-SERVICE-RS-FREE-AUDIT.md)
- [M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md](M3-S3657-FREE-MANIFEST-SEGMENT-ASSETS-RS-FREE-AUDIT.md)
- [M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md](M3-S3656-FIND-MANIFEST-ENTRY-BY-NAME-RS-FREE-AUDIT.md)
- [M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md](M3-S3655-PROCESS-ASSET-LOAD-STEP-RS-FREE-AUDIT.md)
- [M3-S3654-UNREGISTER-SERVICE-WORKER-RS-FREE-AUDIT.md](M3-S3654-UNREGISTER-SERVICE-WORKER-RS-FREE-AUDIT.md)
- [M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md](M3-S3653-INIT-SAVEDATA-RS-FREE-AUDIT.md)
- [M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md](M3-S3652-FREE-RENDER-SUBSYSTEM-RESOURCES-RS-FREE-AUDIT.md)
- [M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md](M3-S3651-UPLOAD-TEXTURE-DESCRIPTOR-DATA-RS-FREE-AUDIT.md)
- [M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md](M3-S3650-DESTROY-TEXTURE-LUTS-RS-FREE-AUDIT.md)
- [M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md](M3-S3648-LOAD-DEBUG-ASSETS-RS-FREE-AUDIT.md)
- [M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md](M3-S3636-ATTACHED-MESH-OVERLAY-RS-FREE-AUDIT.md)
- [M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md](M5-S3584-RETAIL-SOURCE-BUFFER-WRITER.md)
- [M5-S3583-RETAIL-PRODUCER-REPEAT.md](M5-S3583-RETAIL-PRODUCER-REPEAT.md)
- [M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md](M5-S3582-RETAIL-SOURCE-WRITER-TABLE.md)
- [M5-S3581-RETAIL-SOURCE-PRODUCER.md](M5-S3581-RETAIL-SOURCE-PRODUCER.md)
- [M5-S3579-RETAIL-SOURCE-WRITER.md](M5-S3579-RETAIL-SOURCE-WRITER.md)
- [M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md](M5-S3577-RETAIL-ZERO-FILL-REMAINING-EDGE.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3658 remain in the append-only ledger; archived boundary detail is
in `PROJECT-OVERVIEW.md` and the notes above. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
