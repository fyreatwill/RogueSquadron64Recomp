# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); audio inventory
and the incremental de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 3828 (2026-10-03).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-audio/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The real Factor 5 image task is
the qualified audio arm; `ROGUESQ_AUDIO_UCODE=0` selects the silent `Broke`
control. Audio is not production-complete.

The current M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are both zero (`FNV=0x762B22A5`). Retail's
shutdown snapshot can retain 12 nonzero bytes, but the phase-gated snapshot at
hangar VI `0x006AB400`/512 is 408 bytes, nonzero=0; the nonzero bytes are
present in the earlier 1024-wide phase and disappear before hangar. The
expected port descriptor is `0x1798B0 -> DMEM 0xCB0`; its final observed writer
is the legitimate zero-valued `0x800078EC` fill before the image DMA. Session
3818 joined that writer through the active generated scalar-store census:
sequence 664 at physical `0x179A44` is the final writer, and every target
`0x1798B0 -> DMEM 0xCB0` input DMA observed it with zero value. Retail/port
target-phase parity is now paired at the measured scope; no nonzero hangar
producer is established.

The complete generated scalar-store census, central host/RSP writer census,
native page-fault census, and nine bounded exact-offset load candidates are
closed at their measured scopes. Generated code does write the task-data page,
but the paired native source-value capture remains unevaluable because target
fault attribution was absent or an arm crashed before target. Do not infer a
zero producer from those nulls.

The qualified port family bodies execute, but S/L stores go to alternate
objects and I has no hangar edge. The repaired clear witness identifies
`0x8008F2CC`, object `0x801797B0`, length `0x298`; family-edge and clear-object
identity remain unresolved. Port guest route bytes are zero in the qualified
family rows, but retail family reachability has not yet been achieved.

## Next steps

Work only the first applicable item. This is one monotonic backlog.

1. **M5 alternate family-object ownership.** Session 3825 selected H2 at the
   qualified scope: 1,280 S/L/I stores and 257 family-entry rows stayed outside
   the clear-associated `0x801797B0..0x80179A47` object while route-order and
   source-range/source-transition controls were live. Determine whether these
   alternate objects are intended route state or a disconnected output family;
   do not repeat the completed aliasing join. Session 3827's target-valid rerun
   recorded accepted `[route-prep]` and route-handoff rows, correcting the
   stale summary marker, but emitted no exact-route DMA or source-range-reader/
   writer rows. Session 3828 corrected those gates and marker counts: target
   phases and route controls were positive, but exact-route DMA and
   source-range reader/writer rows were still zero. Before interpreting
   ownership, census every target-phase RSP audio-DMA descriptor to determine
   whether the expected descriptor is outside the current overlap windows or
   absent.
2. **M5 port target-phase qualification, closed at this scope.** s3821's pair
   was coverage-invalid because the port arm stopped at VI 640; s3822's
   standalone arm reached both target phases. Do not repeat standalone
   qualification unless the route or build changes.
3. **M5 target-phase retail/port route parity.** s3820's independent oracle
   phase snapshot is zero at hangar (`FNV=0x762B22A5`, 408 bytes), matching the
   qualified port input-DMA payload. The next bounded probe must join the
   retail hangar source snapshot to the port image-stage/source-DMA route in
   one paired capture, including the existing positive controls. Do not repeat
   the retail nonzero-writer census: its shutdown-only 12-byte residue is
   pre-target/transient evidence, not a hangar producer.
4. **M5 image-arm stability discriminator, closed at this scope.** The
   isolated image arm reached both target phases with independent phase and
   M5 controls; s3811/s3812 launch-order failures no longer block producer
   work. Keep the stability breadcrumb passive and do not repeat ordering A/B.
5. **M3 runtime allocator qualification.** The complete generated
   control but could not produce a valid silent/image pair: the image-first
   arm produced 258 family rows and both target VIs, while silent crashed 36
   times in the captured log. Do not repeat launch-order variants. Resume only
   with a new discriminator for arm stability that preserves both controls.
   `rs_zcfree` idiom is closed at s3790; no generated invalid writer or guard
   is justified.
6. **Generated-symbol renaming sweep.** Resume only after the M5 change is
   validated and M3 has no new discriminator. Keep slug
   `generated-symbol-renaming-sweep`; s3796 found no stale callable symbol in
   `0x80009000..0x8000A000` with valid companion positive controls.

## Live hypothesis table

| Hypothesis | Status |
|---|---|
| `H-M5-ProducerAbsent` | Selected for measured pre-input producer classes; only legitimate zero-fill writer observed. |
| `H-M5-ClearIsExpected` | Selected: `0x8008F2CC` allocates and clears the source object before writeback/input DMA. |
| `H-M5-RetailWriterPortEdgeAbsent` | Selected for measured target phases; retail writer families have port bodies but no target-buffer edge. |
| `H-M5-RetailWriterFamilyOtherObject` | Selected for S/L; their stores target alternate objects. |
| `H-M5-RetailWriterFamilyAbsentTargetEdge` | Selected for I; no hangar-phase family edge. |
| `H-M5-FamilyRouteIdentityMismatch` | Selected at s3825 scope: alternate family objects do not join the clear-associated route/source object; semantic ownership remains open. |
| `H-M5-PortGuestRouteZero` | Single-source selected at s3781: qualified port family rows sampled zero route bytes. |
| `H-M5-RetailGuestRouteParity` | Unevaluable: retail has not reached family PCs or target VI in the recipes tried. |
| `H-M5-RetailRecipePreTarget` | Selected for s3782–s3785 recipes; each stayed in 320-wide attract with whole-RDRAM control positive. |
| `H-M5-RetailFamilyReachability` | Selected at s3788: Rice-attached retail reached target VI and all three watched family PCs with positive control. |
| `H-M5-PairedRouteCaptureStable` | Refuted at s3789: independent retail and image control were valid, but silent crashed before paired family rows. |
| `H-M5-RetailPortRouteParity` | Unevaluable at s3789: retail route totals were captured, but no valid silent/image pair existed. |
| `H-M5-SilentPreTargetCrash` | Not deterministic: s3762 reached targets, but paired stability remains parked. |
| `H-M5-Step1ContractGap` | Open downstream of shared task/route/PCM progress; image-stage activity is the first arm difference. |
| `H-M5-OutputConsumerGap` | Refuted at the measured chain: zero exists before image-stage output and PCM consumption. |
| `H-M5-SPYieldOneShotContract` | Selected at s3799: default preserves a pending request while request-only consumes it once; both arms reach phase 640. |
| `H-M5-SPYieldCauseOfStall` | Refuted at s3799: corrected one-shot behavior does not by itself reach title or hangar. |
| `H-M5-PairedRouteCaptureStable` | Selected at s3800: image and silent both reached title/hangar with controls and no crash/abort. |
| `H-M5-ImageStageOnly` | Selected at s3800: image emitted 5,570 stage rows while silent emitted zero; shared PCM/return controls remained active. |
| `H-M5-ImageStageBoundary` | Selected at s3801: image's zero source/stage payload reaches a live image consumer; silent has no image-stage rows but retains PCM controls. |
| `H-M5-SourceInputWriter` | Open: the legitimate writer or fill responsible for the zero source span remains unidentified. |
| `H-M5-PairedArmStartup` | Refuted at s3804 as the primary explanation: `tools/probe.sh` did not make the full-census silent arm stable, while the no-census silent control reached title/hangar. |
| `H-M5-DiagnosticLoadStartup` | Selected at s3804: the full M5 census silent arm crashed before title at guest PC `0x8000B650`; the same-build no-census silent control reached title and hangar with no crash. |
| `H-M5-CommonBaseDiagnosticStartup` | Not reproduced at s3808: minimal and most single-variable arms failed, but all-five reached both targets; s3807's sequential split remains single-run evidence. |
| `H-M5-MinimalRouteTargetValid` | Selected at s3807: minimal image arm reached title `0x00790400` and hangar `0x006AB400` with no crash or abort. |
| `H-M5-DiagnosticLaunchOrderInteraction` | Refuted at s3812: image failed before target in both tested launch orderings while silent reached title/hangar. |
| `H-M5-DMEMTaskBoundaryConsumed` | Unevaluable at s3810: the corrected image arm crashed before target while the silent arm reached hangar; the boundary byte was not observed by a qualified image task. |
| `H-M5-DMEMTaskBoundaryStartup` | Selected at s3810 scope: the legacy contract driver reproduced the pre-target image crash at guest PC `0x8000834C`; s3811 reproduced it after removing the legacy diagnostic bundle, so that bundle is not sufficient as the explanation. |
| `H-M5-MinimalImageStartup` | Selected at s3812 scope: explicit image crashed at `0x8000834C` before target in both launch orderings; explicit silent reached title/hangar. |
| `H-M5-IsolatedImageTargetValid` | Selected at s3813: image-only route reached title/hangar with phase, task, audio-return, route, and no-crash controls. |
| `H-M5-ZeroDMEMProducer` | Refined at s3817: target-valid `SQV`/`SSV` writes are independent of DMA bookkeeping but follow the zero input DMA; they are not its producer. |
| `H-M5-VectorStoreOrdering` | Selected H2 at s3817: 512/512 `0xCB0` rows and 4,096/4,096 broader vector rows have vector sequence after the input DMA. |
| `H-M5-SourceRdramWriter` | Selected on the qualified port route at s3818: final writer is `0x800078EC`, physical `0x179A44`, zero byte; independent retail writer/value parity remains open. |
| `H-M5-RetailSourceWriterParity` | Selected at s3820 for the hangar phase: retail phase snapshot is zero with `FNV=0x762B22A5`, matching the qualified port payload; shutdown-only 12-byte residue is pre-target/transient. |
| `H-M5-RetailZeroWriterLegitimate` | Selected at s3819: hangar-phase retail `0x800078EC` post-store scalar samples are 816 zero, 0 nonzero, 0 mismatch, 0 unsupported. |
| `H-M5-RetailNonzeroWriterIdentity` | Closed at s3820 for hangar: exact phase snapshot has zero nonzero bytes; earlier 1024-wide nonzero bytes are erased before target. |
| `H-M5-PortTargetPhase` | Selected at s3822 for the standalone image route: title 1024 and hangar 512 were reached with all requested controls and no crash/abort. |
| `H-M5-PairedTargetCoverage` | Selected at s3823: the same-build port image and independent retail oracle both fired positive controls and reached title/hangar target phases without crash/abort. |
| `H-M5-RetailPortRouteParity` | Selected at s3823 scope: port hangar source DMA was zero (`FNV=0x762B22A5`, `nz=0`), matching the independent s3820 retail hangar snapshot; the s3823 oracle shutdown snapshot was phase-mixed and is not used as exact-span evidence. |
| `H-M5-FamilyAlternateObject` | Selected at s3824 scope: 1,280 target-phase family stores and 257 family entries were positive, but none joined the clear object `0x801797B0` or its span; the active route snapshot was present. |
| `H-M5-FamilyDisconnectedOutput` | Selected at s3825 scope: the fixed image route reached both target VIs with active route/source controls, while every sampled family entry/store remained outside the clear object and span. |
| `H-M5-FamilyOwnershipRouteWitness` | Unevaluable at s3828: target phases and route-preparation/order/transition/handoff controls fired, but exact-route DMA and source-range reader/writer rows remained absent. |

## Evidence ledger — live boundary

- **3785 — combined Start+A retail qualification:** whole-RDRAM control fired
  10,003 times; retail stayed in 320-wide attract for 120 seconds, with no
  target VI or S/I/L family hit and route-byte writes 2/1/0. This is a recipe
  failure, not retail/port parity evidence.
- **3782–3784 — return/Z, repeated-Start, repeated-A:** each whole-RDRAM
  control fired; each recipe remained pre-target with zero target VIs and zero
  family hits. These do not qualify retail reachability.
- **3787 — Start+Z recipe:** whole-RDRAM control fired 10,003 times, but the
  oracle log reported no video plugin attached and remained at width 320 for
  120 seconds. Route-byte writes were 2/1/0; target VIs and all three family
  PCs were zero. This is a recipe/configuration failure, not retail evidence.
- **3788 — Rice-attached Start+Z qualification:** whole-RDRAM control fired
  10,018 times; retail reached title VI `0x00790400` at 18.7s and hangar VI
  `0x006AB400` at 39.4s. The family PCs `0x80007640`, `0x8001E230`, and
  `0x8001F954` executed 3191, 2, and 1367 times respectively. Route-byte
  writes were 12, 6, and 0. This qualifies the independent retail route
  comparison; it does not establish route-byte values or parity by itself.
- **3789 — paired route-state capture remained unevaluable:** Rice retail
  completed with 11,830 whole-RDRAM control writes, title/hangar VIs, 705
  writes in `0x1797B0..0x1798AF`, 1,125 in `0x1798B0..0x179A47`, and 10,995
  executions at `0x800078EC`. The image port arm produced 258 family rows and
  both target VIs without a crash; the silent arm crashed 36 times and had no
  paired family rows. This selects arm-stability H3, not route parity or
  mismatch. The capture script was repaired to use Start+Z, wait for retail
  hangar, wait for oracle completion, and stagger image before silent.
- **3790 — generated `rs_zcfree` idiom census:** the sole caller at `0x80029CFC`
  forwards zlib callback `$a1` into `rs_zcfree` `$a0`; `inflateInit2_` installs
  the paired `rs_zcalloc`/`rs_zcfree` callbacks, and `rs_zcalloc` returns an
  `rs_malloc` result. No alternate generated writer or invalid-value source
  was found. H1 is selected at static scope; runtime allocator legitimacy is
  still unqualified and no guard was added.
- **3791 — bounded generated-symbol lead `0x8008ED6C..0x80091C80`:** the
  companion census found 19 semantic candidates, all already synchronized in
  generated C; the positive-control rows explicitly reported
  `already-synchronized`. The tool changed zero references, so this audio
  range is closed for the rename sweep and no build was needed.
- **3792 — bounded main-overlay symbol lead:** the exact range
  `0x8000040C..0x800027B8` selected `func_8000040C` ->
  `clearMemory16ByteBlocks`; same-run positive controls reported named
  companion entries as already synchronized. The adjacent
  `fake_func_800027B8` is explicitly a fake/data-gap entry and was preserved.
  The rename tool updated five generated references; no build was needed.
- **3793 — bounded main-overlay continuation:** the exact range
  `0x800027B8..0x8000527C` found 47 companion rows, with positive-control
  rows reporting `already-synchronized`. The only stale generated reference
  was the companion-declared fake/data-gap `0x800027B8`; the regeneration-safe
  mapping propagated it to `data_gap_800027B8` in three generated artifacts.
  No callable rename was selected and no build was needed. The next contiguous
  lead remains open.

- **3794 — bounded main-overlay service/allocator range:** the exact range
  `0x8000527C..0x800078E0` was rerun with the verified companion repository
  path. The census reported 60 companion rows, including named positive
  controls such as `rs_zcalloc`, service-worker routines, and string helpers;
  every row was `already-synchronized`, and the tool changed zero references.
  The earlier attempt used a nonexistent companion path and is discarded as
  unevaluable. H1 and H2 were not selected; H3 selected. The next bounded
  lead is `0x800078E0..0x80009000`.
- **3795 — bounded main-overlay continuation:** the exact range
  `0x800078E0..0x80009000` was run with the verified companion repository
  path. The census reported 21 companion rows, including named positive
  controls such as `rs_memset`, heap/display-list helpers, and RDP emitters;
  every row was `already-synchronized`, and the tool changed zero generated
  references. H1 and H2 were not selected; H3 selected. The next bounded lead
  is `0x80009000..0x8000A000`.
- **3796 — bounded main-overlay render-list range:** the exact range
  `0x80009000..0x8000A000` was run with the verified companion repository
  path. The census reported named positive controls
  `setActiveRenderListPtr` and `emitColorFillRect`; both were
  `already-synchronized`, and the tool changed zero generated references.
  H1 and H2 were not selected; H3 selected. The next bounded lead is
  `0x8000A000..0x8000B000`.
- **3797 — M5 request-only SP-yield lifecycle:** the runtime now evaluates
  `ROGUESQ_SP_YIELDED_REQUEST_ONLY` per poll and consumes the pending request
  when that control arm reports yielded. Completion-wins remains the default.
  This prevents one request from being reported forever in the scheduler retry
  path. Build validation is required before drawing a route or audio
  conclusion.
- **3798 — SP-yield one-shot validation:** the Debug build passed, but the
  corrected paired harness was coverage-invalid: default produced SP completion
  and reset controls without phase 640, while request-only crashed 36 times
  before any yield/phase rows. An earlier harness attempt did show the intended
  one-shot row (`returned=1`, `pending_after=0`) and default completion-wins in
  phase 640, but neither arm reached title 1024. H3 coverage failure selected;
  H1/H2 remain unevaluable. No runtime conclusion.
- **3799 — SP-yield one-shot validation completed:** the same-build A/B run had
  positive controls in both arms and reached phase 640 in both. Default produced
  `returned=0,pending_after=1` with 2 E60 rows; request-only produced repeated
  `returned=1,pending_after=0` with 12 E70 and 12 E80F rows. Neither arm reached
  title 1024 or hangar 512; neither crashed or aborted. The one-shot contract is
  validated, while the missing later progress selects H2 (a different
  scheduler/lifecycle blocker). No audio or route conclusion follows.
- **3800 — paired image/silent qualification:** the same-build harness ran
  image, silent, and the independent retail oracle concurrently. The oracle
  whole-RDRAM control fired and reached title 1024 and hangar 512. Both port
  arms reached title 1024 and hangar 512, each emitted the exact-route and
  family-edge positive controls, and neither crashed or aborted. Image emitted
  5,570 `audtask-image-stage-row` rows; silent emitted zero. Image and silent
  shared 83 task-dispatch, 533/532 audio-return, 101 PCM-source, and 531 PCM-
  consumer rows (image/silent respectively). H2 arm instability and H3 stage
  absence are refuted at this scope; H1 image-stage arm difference is selected.
  This does not identify the stage's zero-valued input writer or output consumer.
- **3801 — image-stage source/consumer boundary:** the independent retail
  control fired and reached title/hangar. The same-build image and silent arms
  both reached title/hangar with phase, PCM, audio-return, and no-crash
  controls. Image emitted 2,240 stage rows, 618 source-DMA reader rows, 16
  stage-byte rows, and 1,118 image-queue rows; its hangar source DMA, stage
  DMEM/DMA, and destination payloads were zero-valued while the image consumer
  was live. Silent emitted no image-stage/source/queue rows but emitted 80 PCM
  source, 295 PCM consumer, and 287 audio-return rows. This selects the
  source-input producer gap and refutes output-only and instrumentation-scope
  explanations at this scope; the writer of the zero source span remains open.
  See [M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md).
- **3802 — source writer census:** both port arms reached title/hangar with
  positive controls and no crash/abort. The image arm's hangar input DMA read
  all-zero `0x1798B0..0x179A48` from DMEM `0xCB0`; independent transition and
  DMEM-coverage rows showed the same zero-valued vector/DMA producer chain
  before the RDRAM write, with no guest CPU store overlapping the source span.
  Retail whole-RDRAM and `0x800078EC` controls were live, but retail hangar
  payload parity was not reached. See
  [M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md).
- **3803 — paired source census coverage failure:** the Debug build passed and
  the retail oracle independently reached title `0x00790400` and hangar
  `0x006AB400`, with the whole-RDRAM positive control firing and a natural
  45-second shutdown. Three same-build port launch variants were invalid: the
  second-launched arm crashed 36 times at guest PC `0x8000834C`, while the
  first arm could reach the target in one ordering; another run crashed the
  first arm before title. The image arm produced 256 source-range rows only
  when it survived; no paired image/silent census was valid. This selects an
  arm-startup coverage discriminator and leaves the zero-DMEM writer open.
- **3804 — probe-driver and no-census stability qualification:** the Debug
  build passed. The independent retail oracle fired its whole-RDRAM positive
  control. The full-census image arm, launched through `tools/probe.sh`,
  reached title `0x00790400` and hangar `0x006AB400` with 512 source-range
  rows and no crash. The full-census silent arm crashed 36 times before title
  at guest PC `0x8000B650`. A same-build silent control with the M5 census
  variables removed reached title at 13.3s and hangar at 44.5s, with no crash
  or abort. This selects diagnostic-load startup instability and refutes the
  probe-driver/launch-order explanation; it does not identify the source
  writer. See scratch captures `s3802_m5_source_input_writer` and
  `s3804_m5_nocensus_silent`.
- **3805 — image-only retail ground-truth attempt:** the Debug build passed. The
  independent retail oracle fired its whole-RDRAM positive control and ran to
  completion, but the image-only full-census arm crashed at guest PC
  `0x8000834C` after the 320-wide phase. It produced no title/hangar target VI,
  no M5 source/input rows, and no source payload sample. H3 is selected: the
  image census cannot yet qualify the route alone, so H1/H2 remain
  unevaluable. The recipe's image-only wait path was repaired to avoid
  expanding the absent silent PID under `set -u`. Evidence:
  `scratch/agent/s3805_m5_image_source_ground_truth/`.
- **3806 — census startup matrix:** the Debug build passed. The independent
  retail oracle fired the whole-RDRAM positive control and reached title and
  hangar. In one same-build matrix, no-census, source/input-census, and
  full-census image bundles all crashed before title at guest PC `0x8000834C`;
  each had zero target VI and zero M5 census rows. This selects a common
  launch/diagnostic-path failure at this scope and leaves census-category
  isolation unevaluable. Evidence:
  `scratch/agent/s3806_m5_census_startup_matrix/`.
- **3807 — minimal-route startup discriminator:** the Debug build passed. The
  independent retail oracle fired the whole-RDRAM positive control 10,000
  times and reached title/hangar. In the same-build port matrix, the minimal
  route reached title at 49.8s and hangar at 59.7s with no crash or abort; the
  current-base route crashed 36 times before title at guest PC `0x8000834C`,
  with no target VI. This selects the common base diagnostic bundle as the
  startup destabilizer at this scope and does not identify the individual
  variable. Evidence: `scratch/agent/s3807_m5_minimal_route_matrix/`.
- **3808 — diagnostic-variable isolation matrix:** the Debug build passed. The
  independent retail oracle fired its 10,000-hit whole-RDRAM control and
  reached title/hangar. In the same-build sequential port matrix, minimal,
  `LOG_PHASE`, PCM-boundary, and B40 arms failed before target; audio-return
  and route-state reached only 640; all-five reached title at 48.3s and
  hangar at 58.3s with no crash. This refutes the all-five bundle as
  sufficient at this scope and selects launch-order/nondeterministic
  interaction; no individual variable or source join was isolated. Evidence:
  `scratch/agent/s3808_m5_diagnostic_isolation_matrix/`.
- **3810 — DMEM task-data boundary validation:** the Debug build passed. The
  independent retail oracle fired the 10,000-hit whole-RDRAM control and
  reached title/hangar. In the concurrent port arms, silent reached hangar and
  produced task/ABI/SP controls, while corrected image crashed before any target
  VI at guest PC `0x8000834C` in `spTaskSchedulerThread+9556`. This selects
  startup instability for the legacy diagnostic bundle and leaves boundary-byte
  consumption unevaluable; it does not identify a writer or justify a guard.
  Evidence: `scratch/agent/s3810_m5_dmem_task_boundary_validation/`.
- **3811 — minimal DMEM-boundary pair:** the Debug build passed. The same-build
  reduced concurrent pair retained phase, task-contract, audio-return, route,
  and no-crash controls. Silent reached title `0x00790400` and hangar
  `0x006AB400` with 514 task-handoff, 523 audio-return, and 20 route rows;
  image remained at 320-wide startup and produced 36 crashes at guest PC
  `0x8000834C` in `spTaskSchedulerThread+9556`, with zero target or diagnostic
  rows. This refutes the legacy diagnostic bundle as the sole startup cause,
  leaves DMEM-byte consumption unevaluable, and selects launch order as the
  next discriminator. Evidence:
  `scratch/agent/s3811_m5_minimal_boundary_pair/`.
- **3812 — corrected image-first minimal pair:** the Debug build passed. The
  corrected same-build pair explicitly set `ROGUESQ_AUDIO_UCODE=0` on silent.
  Image launched first, remained at 320-wide startup, and crashed at guest PC
  `0x8000834C` in `spTaskSchedulerThread+9556` before task-contract,
  audio-return, route, or target-VI rows. Silent reached title and captured
  159 frames at hangar with `musyx_stub` controls. The preceding nominal pair
  was invalid because both arms used image audio and both reached target.
  Combined with s3811's reverse ordering, this refutes launch-order interaction
  and selects deterministic image-arm startup failure at this scope; DMEM-byte
  consumption remains unevaluable. Evidence:
  `scratch/agent/s3812_m5_image_first_boundary_pair_fixed/`.
- **3813 — isolated image-arm qualification:** the Debug build passed. One
  image-only phase-gated run reached title at 13.4s and hangar at 24.6s,
  captured 159 frames, and had no crash or abort. Positive phase/task/
  audio-return/route controls were live. At hangar, the stage-3 input DMA
  repeatedly read DMEM `0xCB0`, length `0x198`, to `0x1798B0`, with
  `FNV=0x762B22A5` and `nz=0`; the stage consumer was live. This selects the
  qualified zero-DMEM producer boundary and closes the isolated-startup
  blocker. Evidence: `scratch/agent/s3813_m5_image_isolated_qualification/`.
- **3814 — producer census coverage invalid:** the Debug build passed and the
  same isolated image route reached title and hangar, captured 159 frames, and
  produced 22,850 target input-DMA rows with zero crashes/aborts. However, the
  prescribed source-writer/DMEM census gates were omitted from the command:
  source-writer, DMEM-coverage, and producer-control rows were all zero. The
  run therefore selects H3 coverage-invalid and adds no producer conclusion;
  its zero input payload is not independent evidence. Evidence:
  `scratch/agent/s3814_m5_zero_dmem_producer/image/run.log`.
- **3815 — qualified zero-DMEM producer census:** the Debug build passed. The
  isolated image route reached title at 13.4s and hangar at 24.6s, with 159
  frames and no crash/abort. Positive phase, RSP-source, source-reader,
  DMEM-coverage, source-writer, source-transition, and input-DMA controls all
  fired. At hangar, the RSP source row for DMEM `0xCB0` was zero-valued; the
  input DMA wrote `0x1798B0..0x179A48` with `FNV=0x762B22A5`, `nz=0`; and the
  corresponding source-range writer rows were zero-valued DMA writes. DMEM
  coverage showed zero `kind=vector` writes in the source window, while the
  input predecessor field exposed no nonzero CPU writer (`prev_writer_pc=0`).
  This selects H2 at the qualified route scope and leaves the exact vector
  fill origin open. Evidence:
  `scratch/agent/s3815_m5_zero_dmem_producer/image/run.log`.
- **3817 — DMEM vector-store ordering:** the Debug build passed. The isolated
  image route reached title `0x00790400` and hangar `0x006AB400`; phase and
  source controls were live, with no crash/abort. The new shared sequence join
  recorded 1,319 target input-DMA markers. In the source-range join, all 512
  sampled `0xCB0`-window vector rows had `vector_seq > input_dma_seq`; an
  independent broader `0xDxx` sample had 4,096/4,096 rows with the same
  ordering. This refutes the hypothesis that the observed `SQV`/`SSV` stores
  precede and are overwritten by the input DMA, and selects a source-RDRAM
  writer/clear chain as the next boundary. Evidence:
  `scratch/agent/s3817_m5_vector_store_ordering/image/run.log`.
- **3818 — qualified port source-RDRAM writer join:** the Debug build passed.
  The isolated image arm reached title at 13.5s and hangar at 24.7s, captured
  159 frames, and had no crash or abort. The scalar-store positive control
  fired; target input-DMA rows repeatedly read `0x1798B0..0x179A48` with
  `FNV=0x762B22A5`, `nz=0`, while the final joined CPU writer was sequence 664
  at PC `0x800078EC`, physical `0x179A44`, length 1, value zero. This selects
  the legitimate port clear/fill writer at the measured scope and closes the
  port-side writer-attribution gap; retail writer/value parity remains open.
  Evidence: `scratch/agent/s3818_m5_source_rdram_writer/image/run.log`.
- **3819 — independent retail source-writer/value parity:** the oracle run
  completed normally with the whole-RDRAM positive control (11,125 writes),
  reached hangar origin `0x006AB400` at width 512, and recorded 1,125 writes
  to `0x1798B0..0x179A48`. In that phase, retail PC `0x800078EC` made 816
  scalar stores into the span; every captured stored value was zero, with
  `mismatch=0` and `unsupported=0`. The same run's final 408-byte snapshot
  contained 12 nonzero bytes (`FNV=0x0726A645`), and the writer histogram
  included `0x8001E2C0`, `0x80007670`, the `0x8001FAxx` family, and
  `0x800078EC`. Thus the port zero writer is a legitimate retail writer, but
  complete source-span parity is refuted; the nonzero writer identity remains
  open. Evidence: `scratch/agent/s3819_m5_retail_source_writer/oracle.log`.
- **3820 — retail nonzero-writer discriminator:** the first oracle capture
  retained the whole-RDRAM positive control (11,125 writes), exact-span control
  (1,125 writes), and hangar phase. Its shutdown summary had 12 nonzero bytes,
  but the command did not print their phase address set. The fixed same-recipe
  capture added `--phase-snapshot-watch 1`: the title/1024 phase contained the
  nonzero bytes, while the hangar/512 phase was exactly 408 bytes,
  nonzero=0, `FNV=0x762B22A5`; its only phase writer was `0x800078EC` (408
  bytes). This selects transient/intermediate H1 at the measured scope and
  refutes a nonzero hangar writer (H2). Evidence:
  `scratch/agent/s3820_m5_retail_nonzero_writer/oracle-fixed.log`.
- **3781 — guest route sample:** image-only port reached both target VIs and
  produced 257 family rows; all three sampled guest route bytes were zero.
  Retail controls passed but did not reach a family PC. Single-source port
  evidence; no mitigation authorized.
- **3780 — family route/object join:** image-only port passed controls and both
  target VIs; S/I/L entry controls produced 257 rows, all with `target_arg=0`,
  and the route snapshot was inactive. H1 versus H2 remained unevaluable.
- **3778 — repaired clear witness:** image-only port recorded
  `a0=0x801797B0`, `a2=0x298`, and the matching clear object. Family stores
  remained on alternate objects; the stale-register witness explanation is
  refuted.
- **3768–3770 — family edge/store provenance:** S/L and I controls were
  positive; S/L stores stayed outside both target buffers and I lacked a
  hangar edge. Retail independently executed the family PCs in target phases.
- **3762–3764 — qualified Step 1 comparison:** image and silent both reached
  title/hangar and shared task, route, PCM, and audio-return progress; image
  alone emitted image-stage/DMA rows. Aligned image input was already zero.
- **3751–3758 — upstream boundary:** candidate route loads and censused
  generated/central host/RSP writers did not produce a nonzero task-data value;
  native target-value attribution was unevaluable because target rows were
  absent or an arm crashed before target.
- **3730–3748 — source and route boundary:** expected source descriptors and
  DMA joins were confirmed; source payload stayed zero on the port while
  independent retail payload was nonzero. Scalar, central API, and native
  host-writer classes were closed at their measured scopes.

Detailed notes remain in linked `M5-S37xx-*.md` files and the append-only
ledger. Do not repeat a boundary whose discriminator is already closed.

## Durable operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `Broke`. Never infer audio behavior from
a route that fails to reach the target phase.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes current
truth. Phase-gate animated comparisons on VI transitions. Batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches. Never run
submodule update, checkout, clean, or hard reset commands. Kill runs with
SIGKILL and run from `build/`. A mitigation-shaped change needs an `ORIGIN:`
line naming the writer and stating whether its value is legitimate.

- **3821 — paired retail/port route capture remained coverage-invalid:** the
  initial probe arm omitted the validated route settings and crashed at
  `0x8000834C` before target. A corrected arm enabled LLE, spin-yield, in-loop
  drain, the validated autopilot schedule, and existing route/source controls;
  it was stable with 4,277 route-order and 466 producer rows but remained at
  VI 640, with no title-1024 or hangar-512 rows. The independent retail arm
  fired its whole-RDRAM control, reached hangar, and recorded the exact zero
  snapshot `FNV=0x762B22A5`. H3 is selected: route parity is unevaluable until
  the port target phase is qualified. No mitigation or code change is
  justified. Evidence: `scratch/agent/s3821_m5_retail_port_route_fixed/`.
- **3822 — standalone port target-phase qualification:** the Debug build passed.
  The exact validated image route reached title VI `0x00790400` at 14.3s and
  hangar VI `0x006AB400` at 23.6s, then remained alive through the 90-second
  SIGKILL watchdog. Phase, task-contract, route-order, RSP-source,
  source-producer, source-writer, and source-transition controls all fired;
  no `[CRASH]` or `[ABORT]` marker appeared. This selects standalone target
  reachability and refutes the paired-run-only port stall at this scope. The
  route-parity result remains open until the paired retail/port capture.
  Evidence: `scratch/agent/s3822_port_target.log`.
- **3823 — paired target-phase route parity:** the Debug build passed. The
  same-build port image arm and independent retail oracle both fired their
  positive controls and reached title `0x00790400` and hangar `0x006AB400`
  without crash or abort. Port hangar source-DMA rows repeatedly read
  `0x1798B0 -> DMEM 0xCB0` with `FNV=0x762B22A5`, `nz=0`. The oracle scalar
  control independently fired at `0x800078EC` with 256/256 zero stores,
  zero mismatches, and s3820 supplies the exact retail hangar-span parity
  (`408 bytes`, `nz=0`, same FNV). The s3823 oracle shutdown snapshot was
  phase-mixed and is not used as exact-span evidence. This selects paired
  target coverage and parity at the measured scope; family route/object
  identity remains open. Evidence:
  `scratch/agent/s3823_m5_paired_route_parity/`.
- **3824 — family route/object identity join:** the Debug build passed. The
  first image-only launch was coverage-invalid because it stayed at VI 640;
  the fixed validated launch reached title 1024 and hangar 512 with all six
  family controls, clear-witness, route, and source-DMA controls positive and
  no crash/abort. It recorded 1,280 target-phase family stores (S=512,
  I=256, L=512), all with `target=0`, `clear_exact=0`, and `clear_span=0`,
  plus 257 family-entry rows with `target_arg=0`. The clear witness was
  `0x801797B0`, length `0x298`, and the route snapshot was active. This
  selects legitimate alternate-object writes at the measured scope and
  refutes an aliasing join; alternate-object route identity remains open.
  Evidence: `docs/M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md`.
- **3825 — fixed alternate family-object route join:** the Debug build passed.
  An initial direct launch stayed at VI 640 and was coverage-invalid. The fixed
  validated image route reached title `0x00790400`/1024 at 13.3s and hangar
  `0x006AB400`/512 at 24.6s, with no crash or abort. Family, clear-witness,
  route-order, and source-range/source-transition controls were positive. The
  1,280 phase-qualified family stores and 257 family-entry rows remained
  outside `0x801797B0..0x80179A47`; no store had `target=1`, `clear_exact=1`,
  or `clear_span=1`, and family entries had `target_arg=0`. This selects H2
  (alternate family objects are disconnected from the active source object) at
  the measured scope and leaves their semantic ownership open. Evidence:
  `scratch/agent/s3825_m5_family_route_object_join_fixed/`.
- **3826/3827 — alternate family-object route witness:** the Debug build passed
  and the target-valid capture reached title 1024/hangar 512 with family,
  store, and source-transition controls. Raw logs contain accepted
  `[route-prep]` and route-handoff rows; the prior summary searched stale
  marker names. The one-time DMA hook controls fired, but exact-route DMA and
  source-range reader/writer rows were zero. No H1/H2 ownership conclusion is
  drawn. Evidence: `scratch/agent/s3826_m5_family_object_join/`.
- **3828 — corrected route witness:** the Debug build passed and the target-valid
  image capture emitted 7,279 accepted route-prep, 15,963 route-order, 141
  route-transition, and 4,066 route-handoff rows, plus both target phases and
  family controls. The DMA hook control fired, but exact-route DMA and both
  source-range reader/writer witnesses were zero, so ownership remains
  unevaluable (H3). Evidence: `scratch/agent/s3826_m5_family_object_join/`.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The s3579–s3584 retail-versus-port stored-value inference at `0x800078EC` is
unsupported: retail executes a byte store while the oracle read an aligned word
containing neighboring bytes. The request-only SP-yield/viewer-stall chain is
limited to the old diagnostic arm. The old cinematic-pool/audio-slot
interpretation was superseded by the MusyX voice-table measurement.

## Evidence index

See the session-specific notes linked above and:

- [M5-S3736-EXACT-RETAIL-BYTE-JOIN.md](M5-S3736-EXACT-RETAIL-BYTE-JOIN.md)
- [M5-S3769-RETAIL-PORT-FAMILY-EDGE.md](M5-S3769-RETAIL-PORT-FAMILY-EDGE.md)
- [M5-S3770-FAMILY-STORE-PROVENANCE.md](M5-S3770-FAMILY-STORE-PROVENANCE.md)
- [M5-S3778-CLEAR-EDGE-WITNESS-REPAIRED.md](M5-S3778-CLEAR-EDGE-WITNESS-REPAIRED.md)
- [M5-S3780-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3780-FAMILY-ROUTE-OBJECT-JOIN.md)
- [M5-S3781-GUEST-ROUTE-SAMPLE.md](M5-S3781-GUEST-ROUTE-SAMPLE.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3785 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
