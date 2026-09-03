# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3651 (2026-09-03).

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
   Sessions 3586–3651 closed the generated `jal rs_free` census through
   `funcs_7.c` and all of `funcs_6.c`, plus the earlier MusyX/MORT field
   families. The only remaining Gap is s3636
   `attachedMeshOverlayNpcHandler` `0x1C`/`0x20`: opcode 2 frees those
   words when setup stores type `-1` or parent mesh `+0xC` is NULL,
   without a prior NULL store. Do not re-audit a Complete class. Do not add a
   pointer guard without a concrete invalid writer. Do not land a skip-path
   NULL store for that Gap unless a later census identifies that same writer.
   Host `MATERIAL_ARRAY_PTR_GUARD` at `0x80023290` is not an original skip
   of the s3651 free. The closed-class list and per-session notes live in
   [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md) §56.
   The next M3 unit is `freeRenderSubsystemResources` `rs_free` of
   `*0x8011A444` at `0x80018668` (first remaining original `jal 0x80001C98`
   in `funcs_4.c`; `funcs_5.c` has zero sites).
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
| H-NextClassComplete | Selected for `uploadTextureDescriptorData` `$s1`: interior of the converted-buffer malloc; original byte-2 skip always taken on the live caller. |
| H-NextClassGap | Refuted for this `$s1`. Remains selected for overlay `0x1C`/`0x20` (s3636). |
| H-NextClassUnevaluable | Not selected: one converted-buffer identity, one live caller, one original skip covering the interior. |

The current work-unit slug is `m3-next-audio-idiom-audit`.

## Recent evidence ledger

Only the latest boundary transitions are repeated here; the append-only ledger
and evidence notes retain the full history. Sessions 3586–3651 M3 class
closeouts are archived in PROJECT-OVERVIEW §56.

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

Latest boundary notes. Remaining M3 `rs_free` notes for s3586–s3650 stay on
disk and are indexed in PROJECT-OVERVIEW §56; do not treat absence here as
deletion.

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

Sessions 1–3651 remain in the append-only ledger; archived boundary detail is
in `PROJECT-OVERVIEW.md` and the notes above. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
