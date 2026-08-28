# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and historical evidence remain in the append-only ledger.

Current maintenance marker: Session 3060 (2026-08-28).

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

Session 3057 mapped retail PC `0x80035798` to libultra
`__osViSwapContext` (`0x80035550–0x800358AC`), the VI-register commit
consumer, not a missing game overlay writer. The port has the corresponding
`events.cpp::update_vi` implementation and its `osViSetMode` publication path.
All four generated game-side VI callsites are present, but the s3056 port log
contains only requests of widths 320, 2, 640, and 640, so no 1024 descriptor
exists for the consumer to commit. This rejects missing-writer and aliasing at
the runtime boundary and does not select descriptor corruption. The upstream
game-side mode-selection call/state that should request 1024 remains open.
Evidence: `scratch/agent/s3057_m5_vi_writer_mapping/AUDIT.md`.

Session 3058 ran the retail-grounded VI request attribution. The oracle
passed the whole-RDRAM positive control, reached title at width 1024 and
hangar at width 512, and its `exec-prev` histogram attributed the 1024-capable
`osViSetMode` path to `0x8001B8DC` (142 calls), with only 6 calls from
`0x8001B720` and 5 from `0x8001BB54`. The companion map and generated tree
identify `0x8001B8DC` as `applyPendingViChanges`; the corresponding port path
exists, but the s3056 same-build capture showed it submitting width 640 rather
than 1024. This selects `H-RequestDescriptor`, rejects a missing direct
caller, and does not by itself prove why the descriptor source differs.
Evidence: `scratch/agent/s3058_m5_vi_request_attribution/AUDIT.md`.

Session 3059 completed the bounded static descriptor-source audit. The
`applyPendingViChanges` callsite at `0x8001B8DC` selects from the four-record
table at `0x80128D50`, with the width-bearing field at `+8`. Retail's title
request uses `0x80128DA0` (the `+0x50` record, width 1024), while the
qualified port capture used `0x80128DF0` (the `+0xA0` record, width 640).
`initVideoSubsystem` populates all four records through its existing copy
loop, and the port passes the selected pointer unchanged to `osViSetMode`.
This selects `H-SourceSelection`, rejecting a missing writer and pointer
aliasing at this boundary; the selector-state divergence remains open.
Evidence: `scratch/agent/s3059_m5_vi_descriptor_source/AUDIT.md`.

Session 3060 completed the bounded generated-symbol audit at `0x80017AE0`.
The companion map, generated body, callers, header, overlay registration, and
project TOML all agree on `setViewStateBytesAndFadeScale`, its `0x48`-byte
extent, and its callable setter semantics. No rename was needed; the next
sweep candidate is `0x80017B28`. Evidence:
`scratch/agent/s3060_generated_symbol_rename/AUDIT.md`.

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

Session 3049 audited event registration and DP completion wiring. Retail's
whole-RDRAM control fired, reached title and hangar, and saw `osSetEventMesg`
only for SI/AI plus zero executions of `dpInterruptHandlerThread`; its target
phase still reached the DP consumer at `0x8001C38C` on queue `0x8011A408`.
The same-build port positively registered DP event 9 to that queue with
message zero and produced repeated DP completion rows, but remained at VI 640
`0x0066A500`. This is a route-wiring divergence closest to
`H-EventDeliveryWrong`, not a missing port registration or an unevaluable
measurement. No behavior change was justified. Evidence:
`scratch/agent/s3049_m5_event_registration_edge/AUDIT.md`.

Session 3050 audited direct `osSendMesg` producers for DP queue
`0x8011A408`. Retail's positive-controlled oracle reached hangar and recorded
zero target-phase sends to that queue despite 72,158 watched `osSendMesg`
executions. The same-build port wrapper positive control fired, but the run
stopped at VI 640 and recorded zero phase-4 sends, only receives from
`0x80007904`/`0x8000B650`. This rejects a divergent direct producer and points
to external DP-queue delivery; the writer/interrupt edge is still unproven.
Evidence: `scratch/agent/s3050_m5_direct_dp_producer/AUDIT.md`.

Session 3051 ran the corrected retail-grounded external DP-delivery watch.
Retail passed the whole-RDRAM and execution positive controls, reached the
hangar, and executed `0x8001C38C` (receive from `0x8011A408`) and
`0x8001C3D4` (forward to `0x8011A7E8`) 243 times each in the target phase.
The port's existing batched DP-event instrument was live but stopped at
VI-640 origin `0x0066A500`, so its target-phase delivery remained
unevaluable. This selects `H-MeasurementInsufficient` for the port capture;
the retail pair is real, but the missing port handoff is not localized. The
zero watch at handler entry `0x8001C328` is not interpreted as absence because
the body PCs were positive in the same run. Evidence:
`scratch/agent/s3051_m5_external_dp_delivery/AUDIT.md`.

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

Session 3052 added a host-side sequence table joining `send_dl` entry/return,
`dp_complete`, DP external enqueue, and DP external delivery. The build
succeeded and the fixed port capture produced 726 sends, 553 returns, 553 DP
completions/enqueues, and 99 deliveries. Same-sequence ordering was
`send-return` → `dp-complete` → `external-enqueue`, with delivery later on the
consumer thread. The phase control fired, but the run again stopped at VI 640
origin `0x0066A500`; title/hangar route preparation never accepted. The first
instrument cap was corrected in-iteration to independent per-edge budgets.
This selects `H-MeasurementInsufficient` for the target-phase discriminator;
no route behavior change was justified. Evidence:
`scratch/agent/s3052_m5_route_order/AUDIT.md`.

Session 3053 extended that table to action dequeue, SP completion, and
display-list callback edges. The retail oracle independently passed its
whole-RDRAM control and reached title/hangar. The port table was positive:
559 action/dequeue and callback rows, 559 DP completion/enqueue rows, and 455
external deliveries. Pre-target ordering was internally consistent but the
port remained at VI 640 with route preparation `accepted=0`. Evidence:
`scratch/agent/s3053_m5_gfx_action_order/AUDIT.md`.

Session 3054 (checkpoint) analyzed the s3053 run.log `osViSetMode_recomp`
data. The game issued exactly 4 osViSetMode calls: widths 320, 2 (corrupt),
640, 640. The game **never called osViSetMode(width=1024)** in the AUTOPILOT
run. The route predicate at `src/main/main.cpp:1376–1380` fires only when
`rs64_vi_committed_width()` returns 1024 (title) or 512 (hangar). Older
successful runs (e.g. PORTING-STATE line 23336) confirm the transition
"vi_width=1024 (was 640) origin=0x00790400" is the correct title-screen
signature. The M4 summary shows steady-state VI at width=640, origin=0x005D4500.
This selects `H-TitleOsViNotCalled`: the game code path that calls
osViSetMode(width=1024) is not reached in current AUTOPILOT runs. All
sessions 3040–3053 returned H-MeasurementInsufficient because the route
predicate is unreachable when the VI never transitions to 1024. The
DP-event, ProducerMark, and action-order measurements are all structurally
downstream of this stall — they were measuring inside a phase that never arms.

Session 3055 attempted the required retail-grounded VI-mode discriminator.
The 90-second port AUTOPILOT arm reproduced exactly four `osViSetMode` calls
(widths 320, 2, 640, 640), zero width-1024 calls, and the VI-640 origin
`0x0066A500`. The corrected oracle arm included the whole-RDRAM positive
control but exited before emulation because the debugger-enabled mupen core
was absent at the documented Homebrew path; the initial recipe also exposed
that this frontend does not support the stale `--positive-rdram` option. No
retail caller/width attribution was obtained, so no VI hypothesis is selected.
Evidence: `scratch/agent/s3055_m5_vi_mode_oracle_setup/AUDIT.md`.

Session 3056 repaired the debugger-enabled mupen64plus prerequisite and ran
the retail-vs-port VI-mode discriminator with both positive controls. Retail's
whole-RDRAM watch reached 10,000 callbacks, then retail reached title at width
1024 around 17.3s and hangar at width 512 around 38.4s. The VI-register watch
attributed the 640→1024 transition to `pc=0x80035798`. The concurrent port
capture logged exactly four `osViSetMode` calls (widths 320, 2, 640, 640), zero
width-1024 calls, and remained at VI 640 origin `0x0066A500`. This selects
`H-TitleOsViNotCalled` for the port and rules out port-side VI suppression for
this capture. Evidence: `scratch/agent/s3056_m5_vi_mode_oracle_setup/AUDIT.md`.

## Next steps

Priority is maintenance, then M5, then systematic M3, then the generated
symbol sweep. Maintenance is complete. M5 design is complete, but Step 1 is
route-blocked at pre-title VI 640; event registration/completion is live in the
port and the next unit must use a different handoff edge. M3 is
parked pending a new discriminator.

1. **Generated-symbol sweep — continue only with exact companion identities.**
   The synchronized region through `0x80017AE0` is complete. Preserve
   placeholders for fragments, data gaps, and unresolved boundaries; do not
   invent semantic names. Resume at the next candidate only after auditing
   companion map, generated body, callers, header, overlay registration,
   project TOML, and local duplicates. If the sweep becomes a revisit under
   the rule in the user instructions, use the external retail-entry or M4
   boundary instead.

2. **M5 VI-mode stall — identify the selector-state divergence.** Session
   3059 found retail selecting `0x80128DA0` while the port selected
   `0x80128DF0`; both are populated by `initVideoSubsystem` and the pointer
   is passed unchanged. Continue only with a bounded static audit or
   retail-grounded selector-state attribution that can name the divergent
   producer/state.

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
