# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and historical evidence remain in the append-only ledger.

Current maintenance marker: Session 3048 (2026-08-28).

## Current state

The qualified port uses `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_LLE_UNGATED=1`, and
`ROGUESQ_LLE_SOLO=1`. `ROGUESQ_SPIN_YIELD=1` is diagnostic and default-off.
`ROGUESQ_AUTOPILOT` is the reliable in-process driver. The game can render
attribution, the N64 logo, the intro cinematic, the star flare, the Factor 5
logo, title-like VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) with the validated input path. Hangar visuals still have
geometry/color artifacts.

M5 currently defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0`
selects the silent `musyx_stub` control. Retail uses Factor 5 MORT audio, not
stock `aspMain`; audio is still partly stubbed. M3 is limited to complete
idiom-class audits. M4 hangar/512 Y=`0x8000` is not live on the first hangar
capture.

The original overlay-dispatch explanation is no longer the current blocker:
qualified runs reach title and hangar boundaries. Factor 5 image tasks and
CPU MORT speech are separate contracts. A `Broke` return proves task
completion, not PCM correctness. The M5 route dependency remains open, but
static generated-symbol work can proceed independently.

## Latest results

Session 3040 ran the M5 Step-1 image/silent qualification after an independent
retail ground-truth preflight. Retail passed the whole-RDRAM positive control
and reached title/hangar, but both concurrent port arms stopped at VI 640
(`0x0066A500`) before title; downstream audio rows are unevaluable. The
driver was corrected in-iteration to launch both arms concurrently, use the
scheduled AUTOPILOT route, and clean up child processes. The corrected run
reproduced the same route boundary. Image and silent dispatch controls were
positive (`44` each, `real_ucode=1/0`), so arm selection and logging ran; no
audio hypothesis was selected and no audio behavior changed. Evidence:
`scratch/agent/s3040_m5_step1_contract_pair_final/`.

Session 3041 ran the new retail-grounded ProducerMark boundary. Retail passed
the whole-RDRAM positive control, reached title/hangar, and executed
`0x8001BCE4` 2,470 times; predecessor `0x8000C628` accounted for 2,446 and
`0x8000BFE8` for 7. The same-build port capture had positive route controls
but stopped at VI 640 `0x0066A500`: 526 route-prepares were all
`accepted=0`, with no producer-mark candidate rows, title, or hangar. This
selects RouteFailure for this capture and leaves the caller/order comparison
and all downstream audio rows unevaluable. Evidence:
`scratch/agent/s3041_m5_producer_mark_boundary/`.

Session 3042 completed the bounded static ProducerMark call-chain audit.
All six direct generated calls to `0x8001BCE4` are present: one from
`bufferArbiterProducerScanWait`, three from `submitGfxFrame`, one from
`advanceVideoFrame`, and one from `initVideoSubsystem`. The generated body,
header, overlay registration, project TOML, and companion map agree. Host
`accepted` is only the committed-VI target predicate for 1024/title or
512/hangar; it cannot reject ProducerMark, so the VI-640 `accepted=0` rows do
not identify a missing caller or an acceptance bug. No behavior change was
justified. Evidence: `scratch/agent/s3042_m5_producer_mark_audit/AUDIT.md`.

Session 3043 completed the bounded VI-commit-to-route ordering audit. The
diagnostic `g_m5_vi_commit` snapshot is published by `osViSetMode_recomp`
immediately after queuing next-state mode data, before the retrace thread's
`update_vi` writes the actual VI registers. This is a real telemetry ordering
mismatch, but route preparation does not consume that snapshot: it reads the
live VI registers and applies the target-pair predicate directly. No route
behavior change is justified, and the VI-640 route failure remains open.
Evidence: `scratch/agent/s3043_m5_vi_commit_order_audit/AUDIT.md`.

Session 3044 completed the bounded audio-task publication-to-consumer audit.
`osSpTaskStartGo` forwards the guest `OSTask*` into the non-GFX SP queue;
`task_thread_func` consumes that same pointer, `run_task` calls
`get_rsp_microcode`, and the selected audio arm observes the descriptor on the
same consumer thread. The queue is the real handoff; the release/acquire
guest-pointer atomic is diagnostic only. No missing writer, wrong consumer, or
missing host ordering edge was found. The only remaining static concern is
descriptor lifetime/reuse because the queue carries a RDRAM pointer rather than
a copy; this is single-source evidence and requires independent temporal
ground truth before changing behavior. Evidence:
`scratch/agent/s3044_m5_task_handoff_audit/AUDIT.md`.

Session 3045 added and ran a regeneration-safe submit-to-consume descriptor
lifetime table. The independent retail oracle passed its whole-RDRAM control,
reached the 512 hangar, and attributed 1,013 type-2 `osSpTaskStartGo` rows to
task `0x80149470` / data `0x80171E70` (`data_size` `1–2`), with callers
`0x80019DEC` and `0x80019D68`. The port lifetime instrument had active phase
logging but zero accepted title/hangar routes and therefore zero lifetime
rows; its positive control did not arm. This selects
`H-MeasurementInsufficient` for the port capture, not descriptor immutability,
reuse, or ordering. No behavior change was justified. Evidence:
`scratch/agent/s3045_m5_task_lifetime/AUDIT.md`.

Session 3046 ran the new retail-grounded producer/signal edge audit. The first
oracle setup omitted Rice and stayed at VI 320, but its whole-RDRAM control
fired; the corrected Rice run again passed that control, reached title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and observed the known
`0x80019DEC`/`0x80019D68` producers plus `0x8001BCE4` consumers. No distinct
signal, payload, or consumer edge appeared. This selects
`H-MeasurementInsufficient` for the new-edge unit and leaves the port VI-640
route boundary unexplained. Evidence:
`scratch/agent/s3046_m5_route_producer_edge/AUDIT.md`.

Session 3047 ran a retail-grounded frame-sync edge audit. Retail's whole-RDRAM
positive control fired, and `0x80019810`/`0x8001983C` executed with callers
`0x8000BC14`/`0x8000BF38`; retail reached title and hangar. The batched port
probe was live and logged 164 pre-target `0x80128CF0` wrapper edges, but no
`0x80138D10` rows and no target-phase route: it stopped at VI 640
`0x0066A500`. This selects `H-MeasurementInsufficient`; the new edge's
missingness and ordering remain unevaluable. Evidence:
`scratch/agent/s3047_m5_frame_sync_edge/AUDIT.md`.

Session 3048 ran a retail-grounded DP event boundary audit. Retail's
whole-RDRAM control fired, reached title and hangar, and executed the DP
consumer at `0x8001C38C` from `0x8001C388` on queue `0x8011A408` in target
phases. The batched port probe was live and recorded 301 receives on that
queue, but only from alternate pre-target callers (`0x8000B650`, `0x8000834C`,
and early one-offs); it stopped at VI 640 with route preparation
`accepted=0`, no title/hangar phase, and no target caller row. This selects
`H-MeasurementInsufficient`; missingness and ordering remain unevaluable.
Evidence: `scratch/agent/s3048_m5_dp_event_boundary/AUDIT.md`.

Session 3038 refreshed the M5 design gate after a direct source survey. The
active inventory remains complete at A1–A20 in `docs/M5-AUDIO-PLAN.md`: the
Factor 5 image is the real `M_AUDTASK` arm, `musyx_stub` is the only explicit
silent control, `aspMain` and `unknown_task_stub` are not live RS64 audio
routes, and `Broke` remains the required RSP completion edge. No production
audio stub or gate was changed. The old s3028 pre-title result is not a
target-phase qualification; the next run must use AUTOPILOT and phase gates.

Session 3037 synchronized the project symbol TOML for
`0x80017AD0`=`setRenderStateFlagByteThree`; generated code, callers, header,
and overlay registration already agreed. The neighboring setter pair is a
positive structural control. Evidence: `scratch/agent/s3037_generated_symbol_rename/`.

Sessions 3030–3036 audited the next generated-symbol candidates. Exact
companion identities were synchronized for `waitForAnyAudioSlot`,
`initSpeechSubsystem`, and `advancePlayerAnimationPhase`. The candidates
`0x8006ACA4`, `0x8006B704`, `0x8007C298`, `0x80099FDC`, and `0x8009C2C8` remain
mechanically unresolved fragments or boundaries and retain placeholders.
Evidence for each audit is in the corresponding `scratch/agent/s30*_generated_symbol_rename/`
directory and the ledger.

The s3028 paired M5 qualification did not reach title/hangar on either arm,
so its downstream audio nulls were unevaluable. Its corrected driver still
requires a fresh target-phase run; do not infer audio equivalence or a
contract gap from that result.

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. Maintenance is complete. M5 design is complete, but Step 1 is
route-blocked at pre-title VI 640; the VI-commit ordering edge is now audited,
so the next M5 unit must use a genuinely new non-ProducerMark handoff angle. M3 is
parked pending a new discriminator.

1. **M5 route repair/handoff — audit event registration/wiring before the DP consumer.**
   The descriptor lifetime table is implemented but route-blocked: the port
   remained at VI 640 `0x0066A500`, so no target-phase enqueue/consume rows
   could arm. Retail independently reaches the target and reuses task
   `0x80149470`. Session 3048 likewise found a live DP queue wrapper but no
   target phase; use the event-registration/wiring boundary before the DP
   consumer as a new angle with positive route controls. Do not repeat the
   s3048 queue-consumer null or infer event ordering from it.

2. **Generated-symbol sweep — continue only with exact companion identities.**
   The synchronized region through `0x80017AD0` is complete. Preserve
   placeholders for fragments, data gaps, and unresolved boundaries; do not
   invent semantic names. Resume at the next candidate only after auditing
   companion map, generated body, callers, header, overlay registration,
   project TOML, and local duplicates. If the sweep becomes a revisit under
   the rule in the user instructions, use the external retail-entry or M4
   boundary instead.

3. **M5 audio de-stubbing — qualify Step 1, then implement one named edge.**
   Resume only after the route boundary is repaired or a target-phase route
   is independently reached. Use the phase-keyed table covering route,
   M_AUDTASK fields, DMEM/DMA, image break/`Broke`, SP completion, guest
   service, slot/voice transitions, MORT class, and PCM joins. Do not change
   a gate, wait, voice guard, or output destination from qualification alone.

4. **M5 route repair/handoff — identify a different producer/signal edge.**
   The s2988 forced 4→5→0 host transition regressed to VI 320. The s2989–s2991
   READY, wait-on-video, and allocation probes were unevaluable at VI 640.
   The `0x8000C0C4` example is the READY caller, not ProducerMark; the actual
   ProducerMark caller probe at `0x8000BFE8` was also unevaluable. Resume only
   with a genuinely new handoff angle and retain task and phase positive
   controls.

5. **M3 crash work — parked.** Resume only as a complete idiom-class audit
   with a named discriminator; passive recurrence belongs in the soak queue.

6. **M4 accumulator origin — blocked at route qualification.** The latest
   revisit had generic controls but zero M4 stage-1 positive-control rows and
   no 512 hangar phase. Do not interpret those nulls.

7. **M5 SP-yield lifecycle validation — parked** pending a route angle that
   reaches target phases.

8. **M5 CPU-side MORT publication — unresolved; callback edge closed.** The
   corrected edge is `serviceStreamingVoice` descriptor `+0x190` to
   `dmaVoiceSampleAndSignal`; `+0x194` is the legitimate speech source. Do
   not repeat this callback audit without a new destination/order edge.

9. **External retail-entry boundary — candidate set rejected (s2903).** The
   oracle reached title/hangar, but the four watched candidate PCs were
   boot/pre-title only. Any revisit needs a different static handoff and
   ground-truth PC attribution.

10. **M5 image task contract / hangar artifact — parked.** No writeback, remap,
   forced state, or mitigation without an `ORIGIN:` naming the writer and
   stating whether its value is legitimate.

11. **M5 route handoff — retail grounded, port route still missing.** Retail
    positively executes `bufferArbiterProducerMark` at `0x8001BCE4` in title
    and hangar. The next route unit must use a new port-side repair/probe
    angle tied to this handoff and retain the positive control.

## Durable boundaries

Factor 5 uses the custom command mappings in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md); do not infer stream
semantics from standard F3DEX. The qualified Factor 5 path is LLE-only.
Interpreter limits, null-GBI guards, and other defensive runtime checks are
safety mechanisms, not explanations.

Ask the retail oracle for ground truth before adding port instrumentation.
Batch every discriminator in one build and run; scope budgets to the target
phase; use SIGKILL and run from `build/`. Follow `make_elf.py` → N64Recomp →
`fixup_game_funcs.py` → CMake. Never hand-edit generated functions for
behavior changes. Never run `git submodule update`, `git checkout -- lib/...`,
`git clean`, or `git reset --hard`. If `lib/` changes, export its patches in
the same iteration. A mitigation-shaped diff requires an `ORIGIN:` line.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Failed
experiments remain in the ledger and project overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Archived progression

Sessions through 3043 established the current M5 boundaries, qualified the
rendering route, and advanced the regeneration-safe symbol sweep. Exact
interval results, counts, and run outcomes are preserved in
`PORTING-STATE.md` and `docs/PROJECT-OVERVIEW.md`.
