# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2403 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
the append-only ledger remains authoritative for exact commands and probe rows.

Current maintenance marker: Session 2408 (2026-08-26).

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

## Latest evidence

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

1. **M5 audio de-stubbing — active.** Keep `docs/M5-AUDIO-PLAN.md` as the
   design gate. Repeat the downstream-range table now that the sequential
   stub/image route prerequisite is validated, using the existing
   image-stage/PCM/slot/key-on diagnostics. Do not change task data, audio,
   gate, fallback, dispatch, VI, output behavior, or the nonzero predicate.
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
The first same-identity post-DMA slot/key-on fields are now available in the
image join. s2408 validated both route controls, but its image arm still
produced no downstream rows; the range comparison is the next discriminator,
not a conclusion about the consumer.
No behavior change is authorized: do not promote C88, invent output metadata,
remap destinations, alter task data, force a consumer, or add a guard without
a new discriminator and named writer legitimacy.

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
