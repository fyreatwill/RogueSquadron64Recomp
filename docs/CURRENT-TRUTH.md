# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed evidence
notes are linked below. Updated for session 3602 (2026-09-03).

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
   `+0x5C`/`+0x64`. Session 3600 closed the unmasked release/fade index
   class. Session 3601 closed the remaining `0x88`-stride voice-table
   indexers as complete. Session 3602 closed the remaining `-0x6908`
   non-a0 table-base users as complete: mix and synth are live-count
   walks versus `-0x6900`; `allocateSongChannelArray` stores the malloc
   pointer and uses `(count&0xFFFF)*0x88` as size (caller clamps to
   `<=0x20`); render consumes mix's already-formed slot pointer; key-on
   indexes the mix-table ping-pong, not this base; shutdown frees the
   `-0x6904` alias. Runtime allocator/lifetime legitimacy remains
   unproven. See
   [M3-S3602-REMAINING-6908-TABLE-BASE-AUDIT.md](M3-S3602-REMAINING-6908-TABLE-BASE-AUDIT.md).
   Retail-entry and SP-yield threads remain parked. The next M3 unit is
   the `-0x6904` pointer-alias class (`allocateSongChannelArray` store
   and init walk, `shutdownAudioEngine` free, `waitForMusyXAudioTaskDone`
   free). Do not add a pointer guard without a concrete invalid writer.
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
| H-NextClassComplete | Selected for the remaining `-0x6908` non-a0 table-base class: count-bounded walks, malloc-size store, or non-index loads. |
| H-NextClassGap | Refuted for this class: no untrusted or sentinel-as-index edge on this base. |
| H-NextClassUnevaluable | Not selected: the `-0x6904` alias is the same malloc pointer, not a mixed object. |

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
