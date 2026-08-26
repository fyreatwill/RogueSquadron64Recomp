# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2403 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
the append-only ledger remains authoritative for exact commands and probe rows.

Current maintenance marker: Session 2430 (2026-08-26).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- Qualified route: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation requires a named writer, a
  legitimacy judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub used for controls. The image arm performs
  real DMEM work, returns `Broke`, emits generated DMA, and can publish PCM.
  Stock `aspMain` is not this game's contract; MORT is a separate CPU speech
  asset. `docs/M5-AUDIO-PLAN.md` is the de-stubbing design gate.
- The independent retail oracle is the witness for game-side memory claims.
  Whole-RDRAM, phase, status/task, and named-PC controls must pass before a
  retail null is interpreted. It reaches attract, title, and hangar, not a
  mission.
- The zero-output join now admits zero-valued image rows. This is diagnostic
  only: all-zero source, destination, and PCM tuples collide across rows, so
  apparent PCM matches and ordering violations are not yet provenance. s2406
  also propagates route ordinal/row into PCM records for diagnostic identity.
- The image-stage join now records the first post-DMA `slot-sb` and
  `keyon-w40` event for the same arm/phase/ordinal/row, when either exists.
  This is diagnostic only and does not alter audio behavior.
- s2408 revalidated the route prerequisite sequentially: both stub and image
  arms reached title and hangar controls in the same phase-gated recipe. The
  image arm produced target-phase stage and image-DMA rows; the stub control
  produced none, as expected. The downstream-range comparison is now
  authorized.
- s2409 repeated that comparison with both route controls valid. The image
  arm's exact image-range joins remained `stage-only` with no same-identity
  PCM, slot, or key-on event, while the independent key-on census fired in
  the same hangar route. This selects `H-IdentityJoinDefect` at the current
  capture key; it does not identify the missing identity field or legitimize
  any output remap. Artifact: `scratch/agent/s2409_downstream_range_identity/`.
- s2410 added a bounded, observation-only identity table that records each
  image row's first later key-on plus phase/origin, ordinal/row, and a
  64-event sequence candidate. The retail oracle independently passed its
  whole-RDRAM control (12,160 hits), reached title and hangar, and wrote both
  candidate image ranges (768 hits each). The port stub control reached both
  target phases and fired the key-on positive control, but both image-arm
  attempts crashed before title at the existing `0x8000834C` path, so no
  image identity rows were captured. This produces no identity selection; the
  image null is route-invalid. Artifact:
  `scratch/agent/s2410_identity_join/`.
- s2411 reran the bounded identity capture. The stub control reached title and
  hangar and fired the independent key-on positive control, but the image arm
  crashed before title at guest PC `0x8000B650`. It emitted no identity rows,
  so this is route-invalid and selects no identity hypothesis. Artifact:
  `scratch/agent/s2411_identity_join/`.
- s2412 repaired the identity table's phase-scope lifetime and reran the image
  arm. Both target phases and the key-on positive control fired. Of 1,173
  retained stage rows, 1,161 matched phase/origin only, 10 matched
  phase/origin plus the bounded event sequence, and 2 matched all three keys
  (including ordinal/row). This selects `H-SequenceKey` at the current
  capture scope; an independent corroboration run is still required. The
  silent-stub arm exited before title and remains route-invalid. Artifact:
  `scratch/agent/s2412_identity_join/`.
- s2413 independently reran the rebuilt image arm with both route controls and
  the key-on positive control. Of 1,180 retained target rows, 1,168 matched
  phase/origin only, 10 matched phase/origin plus the bounded event sequence,
  and 2 matched all three keys (including ordinal/row). This corroborates
  `H-SequenceKey` at the current capture scope across two valid image runs;
  it does not establish that the sequence is the legitimate downstream
  identity or authorize an output change. Artifact:
  `scratch/agent/s2413_identity_join/image/`.
- s2415 reduced every later PCM source/consumer record against the selected
  class-5/7 rows from s2412 and s2413. Both captures passed title, hangar, and
  key-on controls. All 92,904 retained pairings were later records on a
  different origin (PCM at hangar `0x006AB400`, key-on at title
  `0x00790400`); zero matched same phase/origin and ordinal/row. This selects
  `H-NoDownstreamRelation` for the current identity table, not a legitimate
  destination remap or proof that the PCM is absent. Artifact:
  `scratch/agent/s2415_sequence_pcm_link/`.
- s2416 audited the existing phase-transition markers without adding runtime
  instrumentation. In both valid captures the title key-on shape was identical,
  but the first hangar task ordinal/row and first 0x300-byte DMA destination
  differed, as did the first five PCM guest-address sequences. No task, DMA,
  ordinal/row, or destination field remained stable across the VI-origin
  transition. This selects `H-NoHandoffKey` at the current marker scope; broad
  event order is not promoted to a legitimate identity. Artifact:
  `scratch/agent/s2416_phase_transition_identity/`.
- s2417 used the retail oracle as an independent handoff witness. The whole-
  RDRAM control fired 10,092 times; title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` both occurred. With the positive execution control at
  `0x80033FCC`, 820 type-2 task rows were captured (1,349 phase hits, 529
  non-type-2), including 572 title rows using `data_ptr=0x80173B20` and 179
  hangar rows using `data_ptr=0x80173CB0`; task pointer remained
  `0x80149470`. The retail task/data relation supplies a stable phase-specific
  handoff discriminator and selects `H-RetailStableWriter` at this scope. The
  earlier `0x800078EC` attempt was invalid because it had no retail execution
  hits; the final run registered the task PC with `--watch-pc`. Artifact:
  `scratch/agent/s2417_retail_handoff_final/`.
- s2418 added an observation-only port task/data handoff table after route
  preparation. The phase-gated driver passed title 1024/0x00790400 and hangar
  512/0x006AB400 in one run, producing 512 handoff rows and two task-phase
  controls. Port rows included the retail-selected title pointer 0x80173B20
  and hangar pointer 0x80173CB0, but also title 0x80171CE0 and hangar
  0x80171E70 rows, with phase-local size variation. This selects
  `H-PortDiffersAtHandoff` at the current capture scope. The task-pointer
  field was zero because it was captured in submitter TLS while audio dispatch
  ran on another thread; it is not ground truth and must be repaired before
  using task-pointer parity. Artifact:
  `scratch/agent/s2418_port_handoff/route640/`.
- s2419 repaired that witness with a release-store/acquire-load shared atomic.
  The same phase-gated image capture passed title and hangar controls and
  emitted 512 handoff rows; every row reported task pointer 0x80149470. The
  phase/data table still contained the extra title 0x80171CE0 and hangar
  0x80171E70 rows, plus phase-local size variation, so the repaired capture
  selects `H-PortDiffersAtHandoff` and closes the TLS probe defect. No task,
  audio, dispatch, or output behavior changed. Artifact:
  `scratch/agent/s2419_task_pointer/`.
- s2420 completed the Step-1 same-build M5 checkpoint after repairing the
  driver to deliver the validated eleven-Start route schedule. The retail
  oracle passed whole-RDRAM, title, and hangar controls. Stub and image port
  arms both reached title and hangar. The image arm showed DMEM change, two
  generated DMAs, `break_pc=0x1328`, and `sp-complete-enter/return`; the stub
  showed no DMEM/DMA activity. Neither arm emitted slot/voice rows, and both
  retained only the pre-existing PCM boundary rows. This selects
  `H-ContractGap` for the image-specific downstream contract at this capture
  scope. No default flip or output change is authorized. Artifact:
  `scratch/agent/s2420_m5_contract_fixed/`.
- s2421 repeated the eleven-Start contract capture with the retail oracle
  whole-RDRAM/title/hangar controls passing. Both port arms reached title and
  hangar. The image arm changed DMEM, emitted generated DMA, reached
  `break_pc=0x1328`, and completed SP service; neither arm emitted slot,
  voice/reap, or MORT rows. PCM source/consumer rows remained the existing
  zero-valued boundary stream and no row closed against the image task/DMA
  identity. This selects `H-MissingImageConsumer` provisionally at the current
  capture key. It does not authorize an output remap or prove the image DMA
  payload is legitimate. Artifact: `scratch/agent/s2421_m5_contract/`.
- s2428 joined the selected title writer to the port task table in the same
  paired, phase-gated capture. Retail whole-RDRAM, title, and hangar controls
  passed; both port arms reached title and hangar. Each arm recorded 256 exact
  `0x80015BC8` writes in `0x169730..0x1698EC`, joined to title ordinal/row 4
  and `task_data=0x80171CE0`. The image arm had a pending DMA identity on
  those rows while the stub had none. No selected-PC writer rows appeared in
  hangar. This selects `H-PortTitleWriterJoin` for the title-only relation,
  not a hangar consumer or output remap. Artifact:
  `scratch/agent/s2428_m5_title_writer_join/`.

## Latest evidence

- **s2418 — port task/data relation differs from the retail handoff.** The
  fresh retail control passed whole-RDRAM, title, and hangar controls. The
  corrected phase-640 port driver reached title and hangar in one run and
  emitted 512 handoff rows plus both task-phase controls. It included the
  retail pointers 0x80173B20/0x80173CB0 but also 0x80171CE0/0x80171E70 and
  phase-local size variation, selecting `H-PortDiffersAtHandoff`. The port
  task-pointer column was zero from a cross-thread TLS probe defect, so this
  does not select task-pointer parity. Artifact:
  `scratch/agent/s2418_port_handoff/route640/`.

- **s2420 — Step-1 M5 contract checkpoint selects an image-specific gap.** The
  independent retail oracle passed whole-RDRAM, title, and hangar controls.
  The same-build stub and image arms both passed title and hangar. The stub
  had 1,413 task ABI rows with unchanged DMEM and zero generated DMA rows. The
  image had 1,055 ABI rows, 2,197 DMA-range rows, 2,190 image-stage rows, and
  repeated `run-task-return`/`sp-complete-enter`/`sp-complete-return` rows with
  `break_pc=0x1328`; payloads were zero and the canary was diagnostic-only.
  Neither arm emitted slot/voice rows, while both emitted the existing PCM
  source/consumer boundary rows. This selects `H-ContractGap` at the current
  checkpoint scope, not a route failure, missing task completion, or proof of
  a legitimate output destination. The first attempt was route-invalid because
  the port arms received no Start input; the fixed rerun used the eleven-Start
  schedule and is the only result interpreted here. Artifact:
  `scratch/agent/s2420_m5_contract_fixed/`.
- **s2421 — image task completion still has no bounded downstream consumer.**
  The independent oracle passed whole-RDRAM, title, and hangar controls, and
  both stub/image port arms passed the same route controls. The image arm
  produced DMEM changes, generated DMA, image-stage rows, `break_pc=0x1328`,
  and SP completion. Neither arm produced slot, voice/reap, or MORT rows;
  PCM source/consumer rows were the pre-existing zero-valued boundary stream
  and did not join the image task/DMA identity. This provisionally selects
  `H-MissingImageConsumer`, while leaving writer legitimacy and any
  phase-transition/shared consumer unresolved. No behavior change is
  authorized. Artifact: `scratch/agent/s2421_m5_contract/`.
- **s2422 — retail candidate writers exist, but no port consumer writer joined.**
  The independent oracle passed whole-RDRAM, title, and hangar controls and
  attributed the candidate title/hangar range to PCs including `0x80015BC8`
  and `0x8000F3A0`; the adjacent range had the `0x8008FBxx`/`0x8008FExx`
  family and `0x800078EC`, and the task-field range had `0x80018F5C/60`.
  Both same-build port arms passed title and hangar. The image arm emitted the
  expected `0x168B50`/`0x168E50`-class and `0x1798B0` DMA rows, but neither
  arm emitted slot, voice, descriptor, or filter-consumer rows. This
  provisionally selects `H-MissingImageConsumer` at the current key. It does
  not identify the semantic role of retail writers, establish payload
  legitimacy, or authorize a writeback, remap, task-data change, gate change,
  or guard. Artifact: `scratch/agent/s2422_m5_writer/`.
- **s2423 — the port writer table sees only the image's own DMA.** The fixed
  recipe armed `ROGUESQ_LOG_M5_PCM_WRITER`; the independent oracle passed
  whole-RDRAM, title, and hangar controls, and both port arms reached title and
  hangar. The silent arm had zero candidate-range writer rows. The image arm
  had 953 rows, all sampled as `kind=2`, `pc=0` image-DMA writes, with zero
  later image-downstream, slot, descriptor, or filter-consumer rows. This
  selects `H-MissingImageConsumer` at the current key and does not authorize
  remapping or writeback. Artifact: `scratch/agent/s2423_m5_port_writer_fixed/`.
- **s2424 — guest-store coverage finds a title-only candidate writer.** The
  first run's flat 256-row budget and thread-local task field were invalidated
  and fixed in the same iteration. The corrected rerun passed the independent
  retail controls and both port routes. Stub and image each recorded 256 title
  rows from `0x80015BC8` into `0x169730..0x169B2C`, joined to
  `ordinal=4,row=4` and `task_data=0x80171CE0`; no guest rows appeared in
  hangar, and image hangar output remained DMA-only. This selects
  `H-PortGuestConsumer` for the title row at this capture key, but not an
  image-specific or hangar consumer; `H-MissingImageConsumer` remains open for
  hangar. No behavior change is authorized. Artifact:
  `scratch/agent/s2424_m5_guest_writer_fixed/`.

- **s2425 — retail field context attributes the candidate roles.** One
  independent Rice-oracle run passed the whole-RDRAM control (10,125 hits),
  title-range control (17 hits), and hangar-range control (108 hits), and
  reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. Retail
  `0x80015BC8` in title traversed the `0x80169730`-class destination family
  with the same `s0=0x801143B0`-class context and adjacent progression as the
  fixed s2424 port guest rows. This selects `H-RetailSameWriter` for the
  observed title writer identity. Retail `0x8000F3A0` instead showed
  phase-specific helper contexts (`s1=0x80165C88` in title versus
  `0x80165DC8` in hangar, with different selectors/arguments) and no
  image-output range, selecting `H-RetailDifferentRole` for that candidate at
  this scope. No hangar image consumer or legitimate writeback/remap is
  established. Artifact: `scratch/agent/s2425_m5_retail_writer/`.

- **s2426 — retail candidate PCs do not write the port image ranges.** The
  independent Rice oracle passed whole-RDRAM (`12,661` hits), title
  (`633` VI phase rows at `0x00790400`), hangar (`1,594` rows at
  `0x006AB400`), and both candidate-PC execution controls (`378,745` hits for
  `0x80015BC8`, `418,954` for `0x8000F3A0`). The exact port image ranges were
  written (`1,536` hits at `0x167650..0x167C50`, `1,125` at
  `0x1798B0..0x179A48`), but no write was attributed to either candidate.
  The first range's observed writer was `0x800078EC`; the second included
  `0x800078EC` plus helper PCs. This selects `H-RetailDifferentRange` at the
  current capture scope and rules out `H-RetailImageRangeWriter`; it does not
  identify the legitimate hangar consumer or authorize a remap. Artifact:
  `scratch/agent/s2426_m5_retail_image_ranges/`.

- **s2429 — retail hangar image ranges are active, but this capture did not
  expose writer attribution.** The oracle passed the whole-RDRAM positive
  control (`12,253` writes), reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and recorded `1,536` writes to
  `0x167650..0x167C50` plus `717` writes to `0x1798B0..0x179A48`. The
  invocation did not request `--pc-hist-watch`, and the global 200-event print
  cap was consumed by the control stream; its shutdown output therefore
  contained no writer-PC attribution. This confirms active retail writes but
  selects no consumer-PC hypothesis. The next run must request phase-gated
  writer histograms explicitly.

- **s2430 — retail hangar image ranges select one writer and one helper set.**
  The independent oracle passed whole-RDRAM (`12,253` writes), title, and
  hangar controls. The exact `0x167650..0x167C50` range recorded `1,536`
  writes, all from `0x800078EC`. The exact `0x1798B0..0x179A48` range recorded
  `717` writes from `0x80007670`, `0x800078EC`, `0x8001E2C0`,
  `0x8001FACC`, `0x8001FADC`, `0x8001FAE4`, `0x8001FAEC`, `0x8001FAF0`,
  `0x8001FAF8`, `0x8001FB10`, `0x8001FB14`, `0x8001FBE4`, and
  `0x8001FD2C`. This selects `H-RetailHangarSingleWriter` for the first
  range and `H-RetailHangarHelperSet` for the second at the oracle's
  phase-gated attribution scope. It does not establish which helper is the
  semantic image consumer or authorize any port change. Artifact:
  `scratch/agent/s2430_retail_hangar_consumer/`.

- **s2403 — retained image-stage bytes are legitimately zero at capture scope.**
  The retail oracle passed whole-RDRAM (`32,791,644` hits), title, and hangar
  controls. In one rebuilt two-arm port run, retained stage-2 and stage-3
  source and destination samples were all zero, with identical FNV/nonzero
  tuples and `exact=1`. This selects `H-StageBytesLegitimatelyZero` and
  refutes a source/destination span mismatch for those rows. The image arm
  later crashed at the existing `0x8000834C` path; no image-hangar claim is
  made. Artifact: `scratch/agent/s2403_stage_bytes/`.
- **s2405 — zero-row completion/PCM contract remains under-discriminated.** The
  retail oracle independently passed whole-RDRAM and exact destination-window
  controls, reaching title and hangar. The corrected image arm reached title;
  its stage-2/3 source and destination tuples were zero. The new zero-admitting
  join saw 4,448 rows, 2,731 completions, 3,436 apparent PCM matches, and
  1,717 ordering violations caused by repeated all-zero tuples; stage 3 also
  produced stage-only rows. The concurrent stub arm stopped before target
  activation, so it is route-invalid. This selects a new zero-join identity
  discriminator, not legitimacy, missing writer, or consumer mismatch.
  Artifact: `scratch/agent/s2405_zero_output_contract/`.
- **s2406 — zero image rows and PCM rows have route identity, but not the same
  DMA range.** The retail oracle passed whole-RDRAM and all four exact windows,
  reaching title and hangar. The validated stub and image arms passed both
  target controls. Same-ordinal/row PCM source and consumer records were
  present, but exact image DMA rows remained `stage-only`; e.g. stage 2 used
  `0x167050`/`0x300` while a same-identity PCM row used `0x167C50`/`0x300`,
  with both payloads zero. This selects `H-ZeroOutputConsumerMismatch` at the
  captured range; it does not identify the legitimate downstream writer or
  key-on consumer. Artifact:
  `scratch/agent/s2406_zero_output_identity/validated/`.
- **s2407 — downstream identity table was instrumented, but the comparison was
  route-invalid.** The retail oracle independently passed whole-RDRAM and all
  four exact windows and reached title/hangar. The concurrent port run reached
  title only on the image arm; the stub arm crashed before the 1024 target.
  The image arm produced 2,864 stage rows, 1,334 image-DMA joins, and 3,282
  PCM rows in the captured log, but zero same-identity post-DMA `slot-sb` or
  `keyon-w40` events. Because the stub control failed and the event path had
  no positive downstream activation, this does not select a consumer
  hypothesis or interpret the image-side zero as a null. Artifact:
  `scratch/agent/s2407_downstream_range_identity/`.
- **s2408 — sequential route controls validate both M5 arms.** The same
  phase-gated driver reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` for both arms without a crash. The stub control produced
  zero image-stage/DMA rows; the image arm produced 432 target-phase
  image-stage rows and 168 image-DMA joins, while both produced PCM rows.
  This selects `H-RouteDriverOnly` from s2407's route hypotheses and
  authorizes repeating the downstream-range table. No downstream consumer
  conclusion follows yet. Artifact:
  `scratch/agent/s2408_downstream_range_identity/`.
- **s2411 — identity comparison was again route-invalid.** The stub arm reached
  title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` and emitted
  `keyon-w40`; the image arm died before width 1024 at guest PC `0x8000B650`.
  No image identity rows exist, so phase, ordinal/row, sequence, and no-join
  hypotheses remain unselected.
- **s2412 — bounded identity table selects the sequence key.** After retaining
  stage rows across intervening scope transitions, the valid image arm
  produced 1,173 rows: class 1 (phase/origin only) 1,161, class 5
  (phase/origin plus sequence) 10, and class 7 (all three keys) 2. This is a
  single capture and needs an independent rerun before closing the identity
  defect or changing any output behavior. The stub control was route-invalid.
- **s2413 — independent image capture corroborates the sequence key.** The
  image arm reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`; the key-on positive control fired at event 5321. Its
  1,180-row table split was 1,168 class-1, 10 class-5, and 2 class-7, matching
  the prior valid run's class-5/class-7 population. This closes the need for
  another reproduction of the same identity table, but is still a
  current-scope identity result, not proof of legitimate output consumption.
- **s2414 — sequence-key legitimacy reducer selects the ordered relation.**
  The corrected s2412 `image_retained` artifact and s2413 image log both passed
  title, hangar, and key-on controls. Their complete class-5/7 tables were
  identical: ten sequence-only rows at deltas 25–61 and two full-key rows at
  16–18; every key-on followed its stage event. This selects
  `H-SequenceLegitimate` under the planned discriminator at the current scope,
  while the shared key-on across multiple rows leaves its downstream PCM/task
  legitimacy open. Artifact: `scratch/agent/s2414_sequence_legitimacy/`.
- **s2415 — selected key-on has no same-origin downstream PCM identity.** Both
  validated captures passed title, hangar, and key-on controls. The complete
  table contains 92,904 later PCM source/consumer pairings and zero
  same-phase/origin plus ordinal/row matches; every pairing is at the hangar
  origin while the selected key-on is at title origin. This selects
  `H-NoDownstreamRelation` at the current capture scope, leaving a possible
  phase-transition identity gap open. No output behavior is authorized.
- **s2402 — identity is valid at stage entry.** Corrected same-build stub/image
  arms passed route controls; both observed `prepare-clear`, then
  `stage-observe` with `valid=1` and matching `prepare_seq`, followed by
  `return-clear`. This refutes host-clear, guest-clear, and separate-read
  explanations at the captured edge.
- **s2400–s2401 — earlier identity captures were route-invalid.** Missing
  controls, phase-blind budgets, and pre-title crashes made their null rows
  uninterpretable; do not reuse them.
- **s2398–s2399 — route-order/identity labels were superseded.** Logging did
  not perturb title reachability, and the first identity join showed cleared
  stage identity; s2402's corrected publication control superseded both
  interpretations.
- **s2395–s2397 — suppression and producer boundary.** Missing-function
  suppression is required for the qualified title route. The stage-call
  producer is live before title, but the initial route-order run was invalid;
  s2398 supplied the control.
- **s2381–s2392 — ground-truth and M5 boundary.** Retail gate writers and
  task-field writers are real; task ABI relates the exact field to
  `data_ptr+0x100`; retail writer source is task-related at phase/field scope.
  Exact retail windows are active where retained port stage rows are zero,
  but the port byte capture was not yet an independent byte-level witness.
- **s2386–s2390 — reporter predicate audit.** Corrected raw reporter joins
  associated all retained image candidates; completion requires source and
  consumer on the same DMA range. The retained image-stage nonzero predicate
  found zero at title-stage rows, leaving only the writer/consumer contract
  open. Do not repeat the closed phase-wide provenance join.
- **s2370–s2380 — A1 route boundary.** Retail does not execute the port's
  `0x80001F88` null-function callsite in the target capture. Port arms request
  zero outside resident sections. Retail's effective `osRecvMesg` flag is
  blocking (`$a2=1`) despite the pre-delay call-site label; this does not
  authorize a fallback or flag change.

## Active backlog

Closed investigations are not active work items. This is one monotonic
sequence; #1 is the next campaign priority.

1. **M5 image consumer provenance — active.** Keep `docs/M5-AUDIO-PLAN.md` as the
   design gate. s2425 establishes retail/port parity for the title
   `0x80015BC8` writer family, while s2426 shows neither candidate PC writes
   the exact port image ranges; `0x800078EC` and helper PCs write those ranges
   instead. The next bounded unit must trace the retail-selected title
   writer's exact store/range relation into the image/task identity, or close
   the remaining hangar consumer gap with a new ground-truth discriminator.
   No output remap, task-data change, gate change, or guard is authorized.
   s2427 confirmed the exact retail title-range writer and s2428 joined it to
   the port title task row. The next capture must use a new ground-truth
   discriminator for the unresolved hangar consumer; no behavior change is
   authorized.
   s2429 confirmed both exact hangar ranges are written on retail, but omitted
   the explicit writer-PC histogram required to attribute them. s2430 filled
   that gap: the first range is single-writer `0x800078EC`, while the second
   has the listed helper set. The next unit must execute-watch that complete
   set in the hangar phase to distinguish active consumer entry from
   store-helper execution; no port behavior change is authorized.
   s2431 execution-watched the complete set with valid controls. Every selected
   PC executed in the hangar phase: `0x800078EC` had 408 hits, `0x80007670`
   had 184, and each listed helper had 11–12. This rules out a complete retail
   execution gap and selects `H-RetailHangarExecutionClass`; the semantic
   entry/helper distinction remains open. The next unit must collect one
   phase-gated field-context table for that class; no port behavior change is
   authorized.
2. **M5 task/output closure — closed at current capture scope.** Keep the
   corrected reporter reducer; the earlier task-gap label was a join artifact.
3. **M5 gate polarity/writer join — closed at current capture scope.** No gate
   treatment is authorized.
4. **M5 payload-transformation provenance — closed at current capture scope.**
   Do not repeat the phase-wide candidate join without a new discriminator.
5. **M5 A1 retail flag semantics — closed at current capture scope.** Do not
   repeat the delay-slot watch or change the flag.
6. **M5 A1 pre-target route boundary — closed at current capture scope.** Do
   not add a null fallback or repeat the resident-overlay table.
7. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator.
8. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route table selects `LLE_UNGATED=1, LLE_SOLO=1`: it reaches title
and hangar, while the other arms do not reach both. Menu spin yield is a
diagnostic route aid, not a default behavior change. Factor 5 command mappings
and independent controls are in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md)
and [`tools/oracle/README.md`](../tools/oracle/README.md).

### M5 audio and image output

Direct service entry/exit, service gate/loop, task/AI boundary, image DMEM
work, generated DMA, and reporter association are live on the port. s2406
propagated route ordinal/row identity into PCM records; same-identity PCM rows
exist, but their ranges differ from the exact image DMA destination, so the
current result is a consumer-range mismatch, not proof that zero is legitimate
or corrupt output. Retail independently proves that related memory regions and
task-field writers are active, but no exact legitimate port writeback or
slot/key-on consumer contract has been established.
The s2422 retail witness names writers in the candidate title/hangar and
adjacent/task-field ranges, but the same-build port image arm still has no
bounded slot/voice/descriptor/filter consumer row. This is a valid-control,
single-capture selection of `H-MissingImageConsumer`, not proof that every
retail writer is an image-output writer; port writer attribution remains the
next discriminator. The fixed s2423 capture armed the existing phase-keyed
writer table and found only image-owned DMA writes (`kind=2`, `pc=0`), not a
later CPU/consumer writer; the silent control had none. Continue by closing
the guest-store/consumer coverage gap rather than treating these DMA rows as
retail-writer parity.
s2426's exact-range oracle run found that the port image destinations are
written in retail, but not by either previously selected candidate PC:
`0x800078EC` accounts for the first range and also contributes to the second,
with other helper PCs on the latter. This selects `H-RetailDifferentRange`
for the candidate-PC relation and keeps the hangar image-consumer identity
open. It is ground-truth attribution only; no output remap or mitigation is
authorized.
s2427's independent exact-title-range oracle run passed whole-RDRAM (552,718
hits), title (633 VI rows), hangar (1,593 VI rows), and both candidate-PC
execution controls (643,883 and 680,798 hits). In the title range
`0x169730..0x169B30`, `0x80015BC8` wrote 71,100 times while `0x8000F3A0`
wrote 70 times. This corroborates the title writer identity at the exact
range and selects `H-RetailTitleExactWriter` at this scope. The image-range
attribution remains `0x800078EC`/helpers from s2426; no hangar consumer,
remap, writeback, task-data, gate, or guard is authorized.
s2429's independent oracle run again passed whole-RDRAM, title, and hangar
controls and found `1,536` writes in the first exact image range plus `717` in
the second. Because `--pc-hist-watch` was not armed, this is aggregate-only
ground truth and cannot select a writer or justify a consumer mapping. The
missing attribution is an instrumentation omission, not evidence of no
consumer; no behavior change is authorized.
s2431's independent execution-watch run passed the whole-RDRAM, title, and
hangar controls. It found hangar-phase execution for every selected range
writer PC, including the `0x800078EC` first-range writer and the
`0x80007670`/helper class for the second range. This closes the complete
execution-gap hypothesis but leaves semantic entry versus lower-level helper
identity unresolved; no output remap or mitigation is authorized.
s2432's independent field-context capture again passed the whole-RDRAM,
title, and hangar controls and reproduced exact image-range totals of 1,536
and 1,125 writes. The field table itself was not a usable discriminator:
`0x800078EC` produced 1,361,077 phase hits, saturated its 32,768-row unique
table, and overflowed 932,403 rows, while `0x80007670`, `0x8001E2C0`,
`0x8001FACC`, `0x8001FAF8`, and `0x8001FD2C` produced no field rows despite
range-writer execution. The helper PCs that did produce rows shared the
same broad tuple families, but those rows were not joined to an exact store
event. This selects `H-FieldTableUnjoinable` as an oracle-instrument result,
not a retail semantic-entry or helper conclusion. No output remap, writeback,
task-data change, gate, guard, or default change is authorized.
- s2428's fixed paired port capture passed retail whole-RDRAM/title/hangar
  controls and both port-arm title/hangar controls. Each arm recorded 256
  exact `0x80015BC8` writes in `0x169730..0x1698EC`, joined to title
  ordinal/row 4 and `task_data=0x80171CE0`. The image arm carried a pending
  DMA identity on those rows; the stub had none. No selected-PC writer rows
  appeared in hangar. This selects `H-PortTitleWriterJoin` for the title-only
  relation and leaves the hangar consumer unresolved. Artifact:
  `scratch/agent/s2428_m5_title_writer_join/`.
The first same-identity post-DMA slot/key-on fields are now available in the
image join. s2408 validated both route controls, but its image arm still
produced no same-identity downstream rows. s2409 independently observed
hangar key-on events while the image join still classified every captured row
as `stage-only`; the current conclusion is an identity-key mismatch, not an
absent consumer or a valid destination remap.
The s2410 identity table is present in the runtime, but its original phase
scope discarded rows before the downstream event. s2412 retained rows across
scope transitions and selected a sequence-key join. s2413 reproduced the same
class-5/class-7 population in a second valid image capture, and s2414 found the
same ordered event-delta table in both captures. This selects the sequence as a
legitimate identity candidate at the current scope, but does not prove that its
key-on event is the legitimate PCM/task consumer identity. s2415 found no
same-origin PCM/task record after the selected key-on in either valid capture;
all retained downstream PCM records were at the hangar origin. This selects
`H-NoDownstreamRelation` at the current key and leaves a phase-transition
identity gap open. No behavior change is authorized: do not
promote C88, invent output metadata, remap destinations, alter task data,
force a consumer, or add a guard without a new discriminator and named writer
legitimacy.

### VI, M3, M4, and generated symbols

Retail/port VI selector and current-line publication remain unresolved; prior
A1 matrices were route-invalid. M3 is parked pending a complete idiom audit.
M4 accumulator-origin work is parked. Generated-symbol renaming is parked at
the useful boundary; do not invent names for the unresolved placeholder
functions identified in the project overview.

## Superseded conclusions

These were believable before qualified routes or independent controls, but are
superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing input or
  wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- The s2190–s2197 and s2283/s2284 second-origin/A1 matrices; they were
  coverage artifacts. The s2228 and s2242–s2259 image/pair crash splits were
  intermittent route loads.
- s2288's stub-first route conclusion and s2286's logger-removal explanation.
- s2304's route-wide PCM gap, s2307's fixed addresses, s2308's zero-fill
  interpretation, and s2325's destination-role split.
- s2335–s2342's inactive-parent/gate labels; later positive controls reached
  the C88 writer boundary. s2345's task-output-gap label was superseded by
  completed reporter intervals.
- s2346's output-metadata-writer-absent label; s2347–s2356 successively
  resolved unrelated candidates, overflow, and value ambiguity; s2357 named
  the task field and s2359–s2360 established the remaining source/payload
  boundary.
- s2376's input-dependent A1 label, s2379's unresolved flag split, and
  s2383's missing-completion label; later independent captures superseded
  each with queue/flag, callee-entry, and callback evidence.
- s2397's implied logging-induced route failure and s2399's
  `H-IdentityClearedBeforeStage` label; same-build controls and s2402's
  corrected identity publication superseded them.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument; arm its
  whole-RDRAM positive control first.
- A null requires a same-run positive control. Batch counters and A/B arms in
  one build/run, scope budgets to the phase, and use VI gates rather than time.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
