# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2403 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md);
the append-only ledger remains authoritative for exact commands and probe rows.

Current maintenance marker: Session 2512 (2026-08-26).

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- Qualified route: `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation needs a named writer, a legitimacy
  judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub. The image arm performs DMEM work, returns
  `Broke`, emits generated DMA, and can publish PCM. Stock `aspMain` is not this
  game's contract; MORT is a separate CPU speech asset. The design gate is
  [`M5-AUDIO-PLAN.md`](M5-AUDIO-PLAN.md).
- The retail oracle is the independent witness for game-side memory claims. Its
  whole-RDRAM, phase, task/status, and named-PC controls must pass before a
  retail null is interpreted. It reaches attract, title, and hangar, not a
  mission.
- The current M5 question is whether the port's generated audio-overlay
  alternate is the legitimate counterpart of retail's second-range consumer.
  The image arm reaches task completion and generated DMA. s2506 joins
  stage-2 image DMA destinations to the generated AI table and its PCM
  consumers; the legitimate nonzero payload writer remains unresolved.

- **s2512 — checkpoint close-out; orphaned loop.sh.new deleted.** The prior
  session left an uncommitted `tools/agent/loop.sh.new` draft. The no-engineering
  churn guard it contained was already committed in commit `7af7d623` before
  s2511. No experiment ran; the .new file was cleaned up. Next is the
  m5-image-payload-writer-provenance work unit (staggered-startup qualified
  image-arm PCM payload writer capture).

- **s2511 — staggering startup separates the paired pre-target failure from
  the later image-arm crash.** The same-build driver waited for the
  single-image baseline to reach the 1024 positive control before starting the
  image-plus-silent pair. Both image arms passed 1024 and reached the 512
  hangar route with image-stage and generated-DMA rows. The pair then crashed
  at `updateHangarBayScene+76424`, while the baseline later crashed at
  `do_rom_read+572`; the silent peer reached its target and was SIGKILLed
  without a crash marker. This supports `H-startup-order` for the earlier
  pre-target symptom and refutes `H-concurrent-resource` as its sufficient
  explanation. It does not identify the later crash writer or the unresolved
  image-to-PCM payload writer. Artifact:
  `scratch/agent/s2511_m5_staggered_image_concurrency/audit.md`.

- **s2510 — the paired-image route failure persists, but the concurrency
  control is incomplete.** A same-build three-arm capture launched
  single-image, image-plus-silent, and silent-control processes with identical
  phase-relative input. Single-image passed its target controls and reached
  1024/512 with image-stage and DMA/join rows. Image-plus-silent remained at
  640 and emitted 36 crash rows at
  `cutsceneDispatchSlotsByFlag+10804`, `last-guest-pc=0x8000834c`, before its
  target positive control. Silent-control also failed to reach 1024 in this
  capture. This supports `H-concurrent-resource` over
  `H-image-renderer-resource` for the paired-image failure, but does not
  separate shared renderer pressure from route/input or startup-order
  divergence because the paired controls missed the target. No writer or
  mitigation claim is authorized. Artifact:
  `scratch/agent/s2510_m5_image_concurrency/audit.md`.

- **s2509 — the image-arm failure is pair-specific in the bounded capture.**
  A same-build three-arm run launched single-image, paired-image, and
  paired-silent processes with identical phase-relative input. Single-image
  passed the target controls and reached phase 10 with 1,636 image-stage rows
  and no crash marker. Paired-silent reached the target route, while
  paired-image stalled before the 1024 gate and emitted zero image-task rows.
  No arm emitted a crash symbol or renderer exception. This selects
  `H-concurrent-resource` over `H-image-renderer-resource` for the observed
  failure, but leaves `H-route-input` unresolved because paired-image lacked
  its positive control. No behavior, mitigation, or writer claim changed.
  Artifact: `scratch/agent/s2509_m5_image_crash/audit.md`.

- **s2507 — the joined-buffer writer census was blocked before the target
  route.** The first qualified image-arm attempt reached 640 then crashed in
  `cutsceneDispatchSlotsByFlag`; the fixed retry reached only 640 and timed
  out waiting for 1024. Both passed the early AI-table control (16 rows), and
  the retry emitted 896 real image-arm dispatches, but neither emitted target
  image-DMA, PCM-consumer, guest-writer, RSP-writer, or host-writer rows. This
  selects no writer hypothesis: the discriminator is unevaluable because its
  target controls are absent. It localizes the next M5 question to same-build
  stub/image route reachability. No behavior or mitigation changed. Artifact:
  `scratch/agent/s2507_m5_joined_payload_writer/audit.md`.

- **s2508 — the image arm causes the current route failure.** A same-build
  direct A/B launched silent and image arms concurrently with identical
  phase-relative input. The silent arm reached title and hangar, passed its
  early controls, and recorded 96 PCM source/consumer pairs with no crash.
  The image arm crashed before title at `last-guest-pc=0x8000B650` in
  `plume::MetalFramebuffer::MetalFramebuffer`, with zero target task, image,
  return, or PCM rows. This selects `H-image-causes-route-stall` over
  route-independent and stub-degenerate explanations for this route. It does
  not identify the pre-title renderer crash's writer or permit a mitigation.
  Artifact: `scratch/agent/s2508_m5_audio_arm_route/audit.md`.

- **s2500 — no active generated kind=1 PCM-store caller exists.** The sibling
  generated tree has 51 `funcs_*.c` files and zero
  `rs64_m5_pcm_writer_store` callsites or candidate-range literals. Its only
  two AI consumers are `osAiSetNextBuffer_recomp` at `0x8008EE00` and
  `0x8008EE84`; the s2308 wrapper insertion is an opt-in fixup pass and is not
  present in the active output. Historical backup helper copies are not
  runtime callers. This selects `H-kind1-absent` at the active generated
  boundary and leaves the direct writer of the AI ring rooted at `0x801096B0`
  open. Artifact: `scratch/agent/s2500_m5_kind1_writer_audit/audit.md`.

- **s2501 — the active generated AI table root is `0x801496B0`, not the
  documented `0x801096B0`.** The exhaustive store/callee census found no
  active generated store reaching `0x801096B0` or its derived slots. In
  `runAiAudioStreamPlaybackLoop`, `0x80150000 - 0x6950` constructs
  `0x801496B0`; the loop initializes sixteen `0x300`-spaced heap pointers
  there, and the two AI consumers read those entries. `0x801096B0` appears
  only as a generated code address in `funcs_49.c`, including an unrelated
  `sd` at `0x801096B4`. This selects `H-ring-unresolved` rather than claiming
  the physical ring writer absent; the address identity must be resolved
  before attribution. Artifact:
  `scratch/agent/s2501_m5_ai_ring_writer_audit/audit.md`.

- **s2502 — the documented `0x801096B0` AI-ring root is an address typo.**
  Independent companion symbols identify `D_801496B0` in the main-overlay
  audio region, while the active generated loop constructs that address and
  initializes sixteen `0x300`-spaced AI-buffer pointers there. The companion
  map and active generated output place `0x801096B0` in mission-overlay code;
  only a nearby `D_801096B9` byte is listed. This selects `H-root-typo` and
  resolves root identity, but does not identify the heap-buffer writer or
  image-to-AI handoff. Artifact:
  `scratch/agent/s2502_m5_ai_ring_root_audit/audit.md`.

- **s2503 — the active AI-buffer allocation/table producer is generated game
  code.** The corrected exhaustive static census found one root-table store at
  `0x8008EDA4`, a sixteen-iteration `0x300`-stride derived-entry store at
  `0x8008EDB8`, and two consumers at `0x8008EE00`/`0x8008EE84`. The same
  function allocates and clears the `0x3000`-byte region. Companion symbols
  independently identify `D_801496B0` and
  `runAiAudioStreamPlaybackLoop`. This selects `H-writer-generated` for
  allocation/table provenance, but the clear is not PCM production; the
  nonzero payload writer remains open. Artifact:
  `scratch/agent/s2503_m5_ai_buffer_writer_audit/audit.md`.

- **s2504 — no nonzero PCM payload writer joins the corrected AI table in the
  active generated tree.** The exhaustive static census found the allocation,
  root store, sixteen `0x300`-stride entry stores, `0x3000` zero clear, and
  both AI consumers at `D_801496B0`; it found no post-clear generated store,
  copy, or nonzero-producing callee derived from that root. Host
  `queue_audio_buffer`/`queue_samples` paths consume guest data and do not
  write the blocks, while the existing RSP-DMA observer has no statically
  joined destination. This selects `H-payload-unresolved`, not
  `H-payload-host`: an indirect/RSP output writer remains open. No behavior
  or mitigation changed. Artifact:
  `scratch/agent/s2504_m5_pcm_payload_writer_audit/audit.md`.

- **s2505 — the image-arm RSP destination remains unresolved against the AI
  table.** The image stages issue `DO_DMA_WRITE` with stage-2 destination
  `MEM_W(0x44, r2)` and stage-3 destination `MEM_W(0x348) + 0x100`; neither
  expression derives from `D_801496B0[i]`. The AI root is the dynamic return
  from `rs_malloc`, while the host image/DMA hooks only observe runtime
  destinations. This selects `H-rsp-destination-unresolved`, not a joined or
  distinct destination, because static code cannot compare the runtime DMEM
  field with the allocator result. No behavior or mitigation changed. Artifact:
  `scratch/agent/s2505_m5_rsp_destination_join/audit.md`.

- **s2506 — image DMA destinations join the generated AI table at runtime.**
  The same qualified run captured the full table rooted at `0x80166450`, 800
  image-DMA rows, and 90 PCM-consumer rows. Target stage-2 destinations
  `0x166A50`, `0x166D50`, and `0x167050` equal table entries 2, 3, and 4;
  consumers used the table entries with 768-byte buffers. This selects
  `H-rsp-destination-joined` and refutes a distinct or unresolved destination
  at this boundary. The joined stage-2 payloads were zero, so this does not
  identify the nonzero payload writer. Artifact:
  `scratch/agent/s2506_m5_rsp_destination_runtime_join/audit.md`.

- **s2497 — the image-to-AI-buffer handoff is absent at the static boundary.**
  The exhaustive census found two generated `osAiSetNextBuffer_recomp`
  callsites, both in `runAiAudioStreamPlaybackLoop` at `0x8008EE00` and
  `0x8008EE84`. They pass a `0x300`-byte pointer from the independent
  `0x801096B0` heap-backed ring/table; the pointer and byte count are the only
  values that survive through `queue_audio_buffer` to `queue_samples`.
  `M_AUDTASK.data_ptr`, image-stage `dest`, image DMA event, and image ordinal
  do not enter this call chain. This selects `H-handoff-absent`, refutes an
  explicit image identity, and does not establish a reconstructed stable
  relation. Artifact: `scratch/agent/s2497_m5_image_handoff_audit/audit.md`.

- **s2499 — `kind=2` is an image-DMA observer, not a PCM-ring writer.** The
  static census found one workspace producer of `rs64_m5_pcm_writer_dma`:
  `rs64_probe_audio_dma_write` after an image-stage RSP DMA is recorded. The
  wrapper stores the DMA destination/length and calls `rs64_pcm_writer_note`
  with `pc=0` and `value=0`; no workspace caller of the guest-store wrapper
  `rs64_m5_pcm_writer_store` was found. This selects `H-kind2-host` for the
  requested writer-provenance boundary and rules out treating the `kind=2`
  control row as a game-side PCM writer. The external generated tree is absent
  from this workspace, so the actual CPU-store callsite census remains open.
  Artifact: `scratch/agent/s2499_m5_kind2_writer_audit/audit.md`.

- **s2498 — no phase-valid slot/voice-to-PCM writer join was found.** The
  qualified port capture passed phase/image/completion/identity controls and
  recorded 91 PCM-consumer rows, including nonzero buffers, plus live slot
  instrumentation. It recorded zero candidate guest-writer and second-range
  writer rows; its only image-to-slot downstream row was phase 8, outside the
  target 512 route. The retail oracle whole-RDRAM control fired 1,508,968
  times, while target writer/post-PC controls remained zero. This selects
  `H-no-consumer-contract` at the observable writer-to-consumer boundary and
  does not establish an image-independent voice cause. Both port attempts
  reproduced a late `do_rom_read` crash after the target rows; no behavior or
  mitigation change was made. Artifact:
  `scratch/agent/s2498_m5_slot_voice_pcm_join/audit.md`.

- **s2496 — the first port PCM consumer still has no image identity join.**
  The static census identifies guest `rs_memset` at `0x800078EC` as the retail
  PCM-ring writer boundary and `queue_samples` after `osAiSetNextBuffer_recomp`
  as the first host consumer boundary. The qualified port run passed the
  target controls (512 / `0x006AB400`), recorded 1,671 image-stage rows and
  completions, and recorded 48 phase-10 PCM consumer rows. No image-stage
  source or consumer join matched; one nonzero consumer-only row had no image
  identity, while the port guest-writer hook recorded no candidate row. This
  selects `H-image-consumer-identity-gap` at the observable port boundary and
  refutes an unreachable consumer. Retail's independent `0x800078EC` writer
  evidence is not a port writer attribution. No task, output, gate, or
  mitigation change was made. Artifact:
  `scratch/agent/s2496_m5_first_image_consumer/audit.md`.

- **s2495 — image stages do not yet join the matching type-2 load by identity.**
  The qualified port capture reached phase 10, width 512, origin `0x006AB400`
  and passed the target load, descriptor, scheduler, image-stage, and return
  controls. It recorded 171 type-2 loads, 316 stage-2 rows across 314 image
  ordinals, and 257 returns; all 316 image joins remained `stage-only`, with no
  source or consumer identity. Loads and image stages were interleaved, but
  image rows contain neither the type-2 task pointer nor its data pointer, and
  several image stages occur per load. This selects
  `H-image-load-distinct` at the observable identity boundary and refutes
  `H-image-load-unobservable`; temporal adjacency is insufficient to select a
  joined image/load pair. The later phase's load-row absence is a phase-budget
  artifact. Artifact: `scratch/agent/s2495_m5_image_downstream_join/audit.md`.

- **s2494 — the port's own `osSpTaskLoad` matches the retail audio boundary.**
  The qualified port capture reached both target phases and passed the
  descriptor/scheduler controls. At hangar `512 / 0x006AB400`, its generated
  load rows used `task_ptr=0x80149470`, type 2, `data_ptr=0x80171E70` or
  `0x80173CB0`, `data_size=1`, and zero output/yield pointers, matching the
  independent retail oracle's 477 type-2 rows at `0x80033E3C`. The distinct
  type-1 `gspTask=0x800377C8` rows are graphics scheduler descriptors, not the
  audio load task. This selects `H-port-load-matches-retail` and supersedes the
  s2493 descriptor-to-load mismatch as a join artifact. The direct load
  boundary is closed; the legitimate downstream image-task/output/PCM join
  remains open. Artifact:
  `scratch/agent/s2494_m5_port_load_join/audit.md`.

- **s2493 — retail `osSpTaskLoad` does not join the port's probed descriptor.**
  The independent oracle passed the whole-RDRAM control, reached hangar, and
  recorded 477 phase-gated type-2 rows at `0x80033E3C`, using task pointer
  `0x80149470` and image `data_ptr` values `0x80171E70`/`0x80173CB0`. The
  qualified port reached both 512 phases and recorded 718 descriptor controls,
  but its phase-12 `gspTask` descriptor remained `0x800377C8`, type 1, with no
  retail task-pointer or data-pointer equality. This selects
  `H-retail-load-differs-from-port` for the attempted join and refutes
  generated-alternate equivalence at this boundary. The pointers are distinct
  scheduler/task objects; no remap or mitigation is authorized. Next: capture
  the port's own `osSpTaskLoad` entry and join that directly to the retail rows.
  Artifact: `scratch/agent/s2493_m5_retail_task_join/audit.md`.

- **s2492 — retail does not execute `osSpTaskYielded` in the target phase.**
  The independent oracle whole-RDRAM control reached 10,000 callbacks. A
  driven run with Rice, eleven verified Start presses, VI trace and VI poll
  reached the retail hangar at width 512 / origin `0x006AB400`; PIF reads also
  confirmed the input path. A range watch over `0x80034420:0x800344D0` recorded
  24,732 SP-status-block executions, including `0x80034420/24`, but the exact
  `osSpTaskYielded` watch at `0x80034450` recorded zero executions and zero
  task rows. This selects `H-retail-osSpTaskYielded-not-executed` and makes the
  requested direct descriptor comparison unavailable, not mismatched. The
  next join point is retail `osSpTaskLoad` at `0x80033E3C`. Artifact:
  `scratch/agent/s2492_m5_retail_task_join/audit.md`.

- **s2491 — preserving the guest pointer ABI repairs the descriptor table.**
  After the oracle whole-RDRAM positive control reached 10,000 callbacks, the
  qualified port capture reached 512 / `0x006AB400` and emitted 26 target
  descriptor controls and comparison rows. In every selected field,
  `MEM_W == explicit aligned bytes == TO_PTR`; the aligned raw layout remains
  a coherent OSTask. The callback still logs the raw 32-bit identity but now
  sign-extends it before `MEM_W`/`TO_PTR`. This selects
  `H-pointer-sign-extension-fixed` and refutes `H-pointer-ABI-not-causal` at
  this boundary. The later `submitSceneNodeRender` crash is separate. Artifact:
  `scratch/agent/s2491_m5_descriptor_abi/audit.md`.

- **s2490 — `MEM_W` and `TO_PTR` agree because the callback truncates the
  guest pointer.** The oracle whole-RDRAM control passed at 10,000 callbacks;
  the qualified hangar capture produced 36 phase-10 and 28 phase-12 comparison
  rows. In every row `MEM_W` and `TO_PTR` matched, while explicit aligned reads
  from `rdram + (task_ptr - 0x80000000)` contained the coherent OSTask fields.
  Static inspection supplies the independent explanation: both runtime
  address expressions subtract the sign-extended `0xFFFFFFFF80000000` base,
  but `rs64_m5_descriptor_yield` accepts `task_ptr` as `uint32_t`, so the
  callback argument is zero-extended before those expressions run. No
  descriptor remap or behavior change is authorized. Artifact:
  `scratch/agent/s2490_m5_descriptor_compare_hangar/audit.md`.

- **s2489 — explicit raw-byte layout separates the descriptor representation.**
  After the oracle whole-RDRAM positive control fired 10,000 callbacks, the
  qualified Debug capture reached title and hangar. A phase-keyed table recorded
  all 64 raw bytes at `gspTask=0x800377C8` and three interpretations per field.
  In 64 hangar rows, direct host-aligned reads consistently formed an OSTask
  tuple (`type=1`, guest-RDRAM pointer fields); byte-offset-`^3` and
  byte-swapped aligned reads did not. This selects
  `H-byte-layout-is-aligned-host` and refutes `H-byte-lane-transform`. It is
  **single-source port evidence**: the oracle positive control validates its
  watch, not these descriptor values. The pre-existing `MEM_W` row still
  disagrees with the explicit aligned read, so that discrepancy is now the
  discriminator; no remap or guard is authorized. Artifact:
  `scratch/agent/s2489_m5_descriptor_layout/audit.md`.

- **s2488 — the proposed `MEM_W` endian correction did not change the
  descriptor fingerprint.** The Debug build succeeded and the corrected
  capture reached the 512/hangar phase; scheduler and descriptor controls
  fired. Every hangar row still emitted the exact s2487 sixteen-word sequence,
  including implausible `0x0A8C2907`. This is an inconclusive single-source
  result: it does not select legitimate or garbage descriptor contents because
  the assumed byte representation/task base has not been separated. The
  retail oracle could not run because its debugger-enabled core dylib is
  absent. Artifact: `scratch/agent/s2488_m5_descriptor_decode/audit.md`.

- **s2487 — gspTask descriptor is populated, stable, and joined to the
  scheduler dispatch in the hangar phase.** Two recipe bugs suppressed all
  prior descriptor rows: (a) `ROGUESQ_LOG_AUDIO_RETURN` was absent, causing
  `audio_route_log_enabled()` to return false and disabling all phase-gated
  hooks; (b) `PROBE_KEYS_FROM_PHASE=1` cannot navigate to the hangar because
  Start keys fire only after 1024 is reached. Corrected probe (boot-relative
  keys, `ROGUESQ_LOG_AUDIO_RETURN=1`) reached 512/0x6AB400 at ~49 s and
  captured 1602 yield rows; 74 in the hangar. The sixteen words at
  `gspTask=0x800377C8` are non-zero and identical across all observations:
  `0A8C2907,88C3045E,...` (endian-invalid struct-cast values, same defect
  noted in s2484). Scheduler dispatch rows at 512 show
  `event_payload=task_ptr=0x800377C8` with `yield_match=1, payload_match=1`
  — gspTask is both the event payload and the task restarted via
  `osSpTaskLoad/osSpTaskStartGo` in the hangar (a yield-and-restart cycle).
  `H-DescriptorPopulated` selected; `H-DescriptorStaleOrEmpty` and
  `H-DescriptorWriterUnjoined` refuted at the dispatcher boundary. Open:
  endian-correct per-field decode (MEM_W per word) to verify type,
  `data_ptr`, `yield_data_ptr` against retail ground truth. Artifact:
  `scratch/agent/s2487_m5_descriptor_capture/audit.md`.

- **s2486 — descriptor instrument built; target route missed due to recipe
  bugs.** Zero descriptor rows in both captures; the causes were the two
  bugs described in s2487. The durable fixup at `osSpTaskYielded_recomp` is
  correct and remains in place. Artifact:
  `scratch/agent/s2486_m5_descriptor_capture/audit.md`.

- **s2485 — the later scheduler pointer is the normal `gspTask` OSTask
  descriptor.** The generated census found no reads/writes or wrapper-specific
  accesses in the `0x40`-byte object at `0x800377C8`; the data-symbol table and
  companion decomp independently name it `gspTask` with type `OSTask`, and
  `spTaskSchedulerThread` passes it specifically to `osSpTaskYielded`. This
  selects `H-DescriptorIsOSTask` at the static boundary and rules out a
  generated wrapper field pattern. It does not identify the descriptor writer
  or join its field contents to the later task. Artifact:
  `scratch/agent/s2485_m5_descriptor_audit/audit.md`.

- **s2481 — the target image-route SP completion is consumed.** The qualified
  eleven-Start capture reached hangar width 512 and passed both lifecycle
  lines: one SP registration and 64 runtime SP completions, plus target-route
  queue rows showing external delivery followed by guest receive on
  `0x8011A420/0x80128C70`. This selects `H-SPConsumed`, rules out a registration
  gap and a published-but-unconsumed SP message at this boundary, and leaves
  the post-receive output/consumer contract open. The run later crashed in
  `recomp::do_rom_read` after 13 frames; that late failure is separate from the
  completed lifecycle observation. Artifact:
  `scratch/agent/s2481_m5_runtime_sp_lifecycle/audit.md`.

- **s2482 — the first post-receive consumer is a generic scheduler handoff.**
  Static control flow places the target receive in `spTaskSchedulerThread` at
  `0x80019CD0`; it reads the fixed event byte from `0x80128C70`, then uses the
  separately held pending-task pointer at `0x801372D8` for
  `osSpTaskLoad`/`osSpTaskStartGo`. The s2481 image joins independently retain
  `source_matches=0`, `consumer_matches=0`, and `stage-only`. This selects
  `H-LaterConsumer` at the first post-receive boundary and rules out a direct
  image-DMA identity consumer there. The later slot/voice/PCM/output join is
  still open; no remap or guard is authorized. Artifact:
  `scratch/agent/s2482_m5_post_receive_consumer/audit.md`.

- **s2483 — the scheduler handoff is event-payload sourced, but identity is
  unresolved.** Static inspection finds the event-type-1 path loading the word
  at `0x80128C70+4` at `0x80019D28`, storing it at `0x80019D3C` into the
  active pending-task slot, and immediately passing it through
  `osSpTaskLoad`/`osSpTaskStartGo`. The deferred path repeats that promotion at
  `0x80019F84`. The independent s2481 capture proves the target receive and
  image-stage DMAs but lacks the event `+4` payload/task identity, so it cannot
  distinguish an image-task join from a distinct later task. This corrects the
  s2482 shorthand `0x801372D8`; the generated address expression is
  `0x80130000-0x72C8 = 0x80128D38`. `H-UnresolvedHandoff` selected; no
  behavior change. Artifact:
  `scratch/agent/s2483_m5_scheduler_task_identity/audit.md`.

- **s2484 — the scheduler payload is a distinct later-task pointer.** The
  required retail-oracle attempt failed `DebugSetCallbacks` with the installed
  non-debugger Homebrew core, so no retail null was interpreted. The corrected
  port probe sampled immediately after `0x80019D28` and, with target SP receive
  and image-stage controls live, recorded stable `event_payload=task_ptr=
  0x800377C8`. Same-run image-stage ABI rows carried changing `data_ptr` values
  such as `0x80171E70`/`0x80173CB0`, never `0x800377C8`. This selects
  `H-LaterTaskHandoff` at the `OSTask.data_ptr` join, rules out an image-task
  identity equality at that boundary, and leaves the descriptor layout and
  later consumer open. The probe's raw host-struct field decode was endian
  invalid and is discarded. Artifact:
  `scratch/agent/s2484_m5_scheduler_identity/audit.md`.

- **s2479 — containing-task completion is runtime-owned, not generated.** The
  complete static table found the image arm's terminal `0x1328` `Broke` edge,
  its two generated DMA edges, the host image-join reporter, and the runtime
  `task_thread_func` publication. Only the runtime's unconditional
  `sp_complete()` after successful `run_task` publishes the containing-task
  SP event; no generated completion or PCM-output writer is reachable after
  `0x1328`. The s2478 `complete=0` field is a source/consumer join result, not
  SP completion. This selects `H-ContainingTaskRuntime` and treats
  `0x1328` as a legitimate terminal image-task contract. Artifact:
  `scratch/agent/s2479_m5_containing_task_completion/audit.md`.

- **s2480 — generic SP publication is live, but the target image route was not
  reached.** The prescribed image-arm run passed the event-wiring controls:
  one SP registration for `0x8011A420/0x80128C70` and 64 runtime SP
  completions. It emitted no image-route or audio-task ABI rows and remained
  on the title/640-width route, so the target SP consumer discriminator is
  unevaluable. This is not evidence for consumption, non-consumption, or a
  registration gap on the image route. Artifact:
  `scratch/agent/s2480_m5_runtime_sp_lifecycle/audit.md`.

- **s2478 — the host-local bridge reaches the target image task but not its
  containing-task completion.** Independent retail controls passed, and both
  port arms reached the target hangar route. The image arm produced two
  target stage rows with matching DMAs and no `0x800155EC` lookup failure or
  `get_function(0)`, while the containing task remained `complete=0` with no
  output-PCM row. This selects `H-ContainingTaskInternalOnly` at the target
  join boundary, rules out an unchanged continuation lookup failure in the
  reached route, and leaves the post-bridge containing-task contract open.
  ORIGIN: `0x800155EC` is the legitimate PC+8 written by the JAL at
  `0x800155E4`; the zero completion is not being mitigated and its writer is
  unresolved. Artifact:
  `scratch/agent/s2478_m5_continuation_bridge_validation/audit.md`.

- **s2476 — the continuation tail is host-local, not map-registered.** The
  exhaustive generated census found one variable-register tail lookup in
  `convertMat3x4ToN64Mtx`: it copies `$ra` to `$t9` and dispatches through
  `LOOKUP_FUNC(ctx->r25)`. Its sole caller writes the legitimate PC+8 link
  `0x800155EC`, which is that caller's local `after_4` continuation. The
  runtime map registers function starts and overlay offsets only; no
  `after_N` continuation registration exists. This selects
  `H-HostContinuationOnly`, refutes `H-ContinuationMap` at the inspected
  scope, and leaves the bridge design open. Static-only; no code or guard
  change. Artifact: `scratch/agent/s2476_m5_continuation_audit/audit.md`.

- **s2477 — the host-local continuation bridge builds, but the smoke run missed
  the target phase.** The durable fixup now replaces the converter's terminal
  `LOOKUP_FUNC(ctx->r25)` with a host return after the sole caller's generated
  `after_4` continuation; the existing s2467 terminal probe is included in
  the match so the change survives regeneration. The Debug build passed. A
  qualified 30-second run reached only intro/attract 640 phases and recorded
  zero `Failed to find function`, `get_function(0)`, or inherited-r31 markers,
  but did not exercise `0x800155EC`. This is a code-change plus non-target
  smoke result, not evidence that the bridge is correct at the converter
  boundary. ORIGIN: the legitimate writer remains the JAL at `0x800155E4`,
  and `0x800155EC` remains its legitimate PC+8 host-local continuation.
  Artifact: `scratch/agent/s2477_m5_continuation_bridge/audit.md`.

- **s2475 — the missing guest link is real, but a raw intra-function link is
  not a registered continuation.** The regenerated callsite at `0x800155E4`
  has delay slot `addiu $a1,$sp,0x10`, so it does not alter `$ra`; the fixup
  wrote the legitimate MIPS link `0x800155EC` before calling
  `convertMat3x4ToN64Mtx`. The qualified port run then changed the failure from
  `get_function(0)` to `Failed to find function at 0x800155EC`, proving the
  converter consumed the link but the host function map has no entry for the
  generated `after_4` continuation. This selects the incomplete-continuation
  branch, refutes the delay-slot explanation, and leaves continuation
  lowering/mapping open. The retail oracle positive control was unavailable in
  this environment because its script/watch harness is absent; no retail null
  was interpreted. Artifact: `scratch/agent/s2475_m5_converter_callsite_fix/audit.md`.

- **s2469 — the live setupCameraMatrices caller supplies the inherited zero.**
  The independent retail control completed with whole-RDRAM and driven VI
  controls. The qualified port's resolver positive control for `0x8009123C`
  fired; the exhaustive regenerated caller probe then recorded 23 phase-4
  rows, all from `runMenuModelViewerScreen` callsite `0x800C2D84`, with
  `r31=0`, `r4=0x800CF090`, and `r5=0`. The existing setup-to-traverse row
  also had `r31=0`, followed by the known `get_function(0)` abort. This selects
  `H-SetupCallerZero` and rules out setup's introduction of the zero and an
  unreachable statically selected caller. The first caller supplying zero to
  `runMenuModelViewerScreen` remains open; no behavior change was authorized.
  Artifact: `scratch/agent/s2469_m5_setup_caller_boundary/audit.md`.

- **s2470 — the live runMenuModelViewerScreen caller supplies the inherited
  zero.** The independent retail control completed with whole-RDRAM and driven
  VI controls. The regenerated exhaustive caller census found one generated
  callsite, `menuOverlayInit` at `0x800C5C9C`; its phase-4 row had
  `r31=0`, `r4=0`, and `r5=0`. The resolver positive control for `0x8009123C`
  fired 85 times in the same run. This selects `H-ModelViewerCallerZero`,
  rules out an in-entry zero introduction and an unreachable static caller,
  and leaves the earlier caller that supplies zero to `menuOverlayInit` open;
  no behavior change was authorized. Artifact:
  `scratch/agent/s2470_m5_model_viewer_caller_boundary/audit.md`.

- **s2471 — the live menuOverlayInit caller supplies the inherited zero.** The
  independent retail control passed whole-RDRAM and driven VI controls. The
  regenerated exhaustive caller census found eight generated
  `mainGameLoop` callsites to the menu-init entry; the final port capture
  recorded the live call at `0x8003E090` in phase 2 with `r31=0`,
  `r4=0x80130B40`, and `r5=9`. The resolver positive control fired 83 times,
  and the known model-viewer caller row also fired. Phase-4 and phase-3 gates
  produced no menu-init rows because this caller precedes them; the final
  unconditional capped capture corrected that measurement boundary. This
  selects `H-MenuInitCallerZero`, refutes an in-entry zero introduction and an
  unreachable static caller, and leaves the earlier caller that supplies zero
  to `mainGameLoop` open. No behavior change was authorized. Artifact:
  `scratch/agent/s2471_m5_menu_init_caller_boundary/audit.md`.

- **s2472 — `mainGameLoop` has no materialized generated caller.** The
  independent retail oracle passed whole-RDRAM and exact-range controls,
  reached title and hangar, and the qualified port retained the resolver
  positive control 85 times. An exhaustive generated-tree census found no
  direct or literal indirect call to `mainGameLoop`; the new entry capture
  recorded phase 2 `r31=0`, `r4=0x80163E00`, and `r5=0x8013AF00`. This selects
  an external/runtime entry boundary and refutes a missed generated caller as
  the source of the zero. The runtime dispatch site that constructs this
  entry context remains open. The newer recompiler again failed on `cache`
  after clearing output, so the run used the restored s2471 generated tree
  with the diagnostic applied directly; no behavior change was made. Artifact:
  `scratch/agent/s2472_m5_main_loop_caller_boundary/audit.md`.

- **s2473 — the runtime constructs the inherited zero before the main worker.**
  The independent retail oracle passed its whole-RDRAM positive control and
  reached title and hangar. A single qualified port run captured zero `r31` at
  the registered game entry, the host entry wrapper, and the
  `run_thread_function` context for the main worker (`addr=0x80000C68`) before
  the generated `mainGameLoop` entry also observed zero. This selects
  `H-RuntimeZero`, refutes `H-ContextClobber` at the construction boundary, and
  makes an overlay wrapper unnecessary as the source explanation. It does not
  establish whether the zero is valid thread-entry ABI or a missing continuation
  value. Artifact: `scratch/agent/s2473_m5_runtime_entry_boundary/audit.md`.

- **s2468 — setupCameraMatrices supplies the inherited zero.** The independent
  retail oracle passed whole-RDRAM and freelist controls and reached hangar.
  The qualified port's same-run resolver positive control fired; at phase 4,
  the new pre-call capture recorded `setupCameraMatrices` with `r31=0`, and
  the paired `traverseSceneGraphRecursive` entry also had `r31=0`, before the
  converter's terminal null dispatch. This selects `H-SetupCallerZero` and
  rules out a traverse call-lowering or in-traverse clobber at this boundary.
  The first earlier caller supplying zero remains open; no behavior change is
  authorized. Artifact: `scratch/agent/s2468_m5_setup_traverse_boundary/audit.md`.

- **s2467 — the converter inherits a zero before its terminal indirect edge.**
  The independent retail oracle passed its whole-RDRAM and freelist controls
  and reached hangar. The qualified port capture passed the same-hook
  `0x8009123C` resolver positive control, then recorded the first null tuple at
  phase 4: converter entry `r31=0`, terminal `r25=0`, `r4=0x80710040`, and
  `r5=0x80165DB0`. This selects `H-CallerContextZero` and rules out an
  in-converter register overwrite or unseen lowering edge. The first earlier
  caller that supplied zero remains open; no behavior change is authorized.
  Artifact: `scratch/agent/s2467_m5_inherited_r31/audit.md`.

- **s2465 — the earliest pre-target null dispatch is inside the named matrix
  converter.** The first resolver capture was instrument-valid but saturated
  its ordinary 64-row phase-4 budget on repeated `0x80029CD0` requests. The
  fixed same-run capture retained priority rows and observed the indirect
  positive-control target `0x8009123C`, then `get_function(0)` at phase 4 with
  native frames `convertMat3x4ToN64Mtx` → `traverseSceneGraphRecursive`.
  The independent full null-resolver backtrace agrees and continues through
  `setupCameraMatrices` → `runMenuModelViewerScreen` → `menuOverlayInit`.
  This selects `H-TargetBoundary` and rules out `H-EarlierBoundary` and
  `H-PhaseMismatch` for this route. The zero-producing callsite/field remains
  open; no guard or dispatch/audio change is authorized. Artifact:
  `scratch/agent/s2465_m5_pre_target_capture/audit.md`.

- **s2466 — the complete static converter census identifies inherited `$ra` as
  the zero-source edge.** `convertMat3x4ToN64Mtx` copies `ctx->r31` into
  `ctx->r25` at `0x80018D84` and its terminal `LOOKUP_FUNC(ctx->r25)` is the
  only indirect edge. Its sole generated caller,
  `traverseSceneGraphRecursive` at `0x800155E4`, uses a continuation-style
  call and writes no new `ctx->r31`; the converter therefore inherits the
  shared context's earlier `$ra`. This selects `H-CallerContextZero` at static
  ABI/context scope, rules out a converter field/register zeroing source and
  an unaccounted converter lowering edge, and leaves the first earlier caller
  that supplied zero open. Static-only; no build, instrument, guard, dispatch,
  or audio change. Artifact:
  `scratch/agent/s2466_m5_zero_source/audit.md`.

- **s2463/s2464 — the dynamic callback capture selects H-PhaseMismatch as
  route diagnosis.** The independent retail oracle passed the whole-RDRAM
  control, reached hangar origin `0x006AB400`, and observed 314
  `spawnNpcOfType`/`0x800400BC` executions plus 3,220 `slotDispatcherIter`
  executions. The qualified port build fired its indirect resolver positive
  control, reached only phase 4 (`640`, origin `0x0066A500`), then aborted
  in `get_function(0)` through `convertMat3x4ToN64Mtx` with last guest PC
  `0x80001F88`. No pre-target boundary row was emitted before the abort;
  per the defined discriminator, this selects `H-PhaseMismatch` as the route
  diagnosis. `H-ZeroWriter`, `H-ValidWriter`, and `H-UnresolvedWriter` are
  unevaluable in the current configuration and refuted as interpretable by
  these rows. No callback polarity, guard, dispatch change, or audio change
  is authorized. Artifact:
  `scratch/agent/s2463_m5_dynamic_callback_capture/audit.md`.

- **s2454 — no port runtime dispatcher body replaces retail `0x8002BEEC`.**
  The source candidate table finds `get_function`/`rs64_m5_dispatch_boundary`
  is only a lookup observer, while `rs_memset` is reached through 88 direct
  generated calls. The complete audio-overlay candidate at `0x8008F2CC`
  (`allocateSongChannelArray` -> `rs_memset` -> `after_6`) is the only
  statically grounded second-range-capable alternate. This selects
  `H-PortGeneratedAlternate` at source scope and rules out a generated/runtime
  `__osDispatchThread` replacement; live provenance remains open.

- **s2455 — the matched port provenance capture is blocked before the target
  phase.** Retail controls passed, including hangar origin `0x006AB400` and
  target-PC rows. The rebuilt qualified port arm reproduced an abort at 4.3s
  in `get_function(0)` from `convertMat3x4ToN64Mtx` (last guest PC
  `0x80001F88`), with no phase-gated M5 witness rows. This is a non-result for
  `H-PortF2CC/H-PortOtherStatic/H-PortDynamic`, not evidence for any one arm.
  The immediate blocker is the pre-phase null-dispatch boundary.

- **s2456 — the reported pre-phase PC is not a lookup callsite.** The external
  generated census contains 28,385 `LOOKUP_FUNC` expansions, but none in
  `convertMat3x4ToN64Mtx`; `0x80001F88` is only the return delay-slot `nop` of
  `buildHeapFreeList`. The retail oracle passed `[gpr-ctl]` and the whole-RDRAM
  control but observed zero executions of `0x80001F88` in 3,557 VI, with no
  hangar phase rows. This is a non-result for the original missing-target,
  legitimate-zero, and bad-data hypotheses; the resolver needs a native
  caller capture before the stale guest-PC breadcrumb can be interpreted.

- **s2457 — the first null is reached from generated menu code, but the guest
  breadcrumb is stale.** A first-hit resolver capture recorded requested
  `0x00000000`, guest `0x80001F88`, and a native backtrace through
  `convertMat3x4ToN64Mtx` → `traverseSceneGraphRecursive` →
  `setupCameraMatrices` → `runMenuModelViewerScreen`. The same rerun's
  indirect positive control resolved `0x8009123C` before the abort. This
  selects `H-ResolverGeneratedCaller` for the native boundary and
  `H-StaleGuestBreadcrumb` for the reported guest PC; it does not identify
  the zero-producing generated callsite or authorize a missing-function stub.

- **s2458 — the port image arm reaches a generated alternate, but not the
  retail-grounded second-range relation.** Retail controls passed: whole-RDRAM
  writes 12,661, exact image-range writes 1,536/1,125, and 594 hangar-phase
  `0x8002BEEC` → `0x800078EC` predecessor rows; `0x8008F2CC` executed 6 times.
  In the paired qualified port run, the image arm reached title and hangar,
  produced 8,351 image-stage rows and 4,149 completed joins, all
  `stage-only`, and no PCM or consumer-only rows. Its phase-scoped static
  `rs_memset` table retained 1,024 rows; the first hangar row was callsite
  `0x8008F2CC`, `dst=0x801797B0`, `len=0x298`, with active Factor 5 identity,
  followed mainly by `0x800052C4`. This selects
  `H-PortGeneratedAlternate` at static-callsite scope and rules out an
  observed port second-range consumer join. The stub arm crashed before the
  target phase, so its null target-phase rows are a non-result. This is
  single-source port-boundary evidence paired with independent retail ground
  truth; no output remap, task-data change, gate, or guard is authorized.

- **s2459 — generated-alternate equivalence remains a qualified non-result at
  the port boundary.** The corrected retail oracle passed whole-RDRAM (12,661),
  exact ranges (1,536/1,125), 627 hangar-phase `0x8002BEEC` -> `0x800078EC`
  predecessor rows, and six `0x8008F2CC` executions. The paired port image arm
  crashed before target capture in `matchKeywordWithPriority`
  (`last-guest-pc=0x8000834C`); a fixed image-only attempt with
  `ROGUESQ_DRAIN_INLOOP_TICK=1` also crashed in `slotDispatcherIter`
  (`last-guest-pc=0x80007904`). The passed controls qualify the missing port
  tuples as a non-result, but do not select equivalent versus bootstrap-only.
  The initial oracle command without Rice/hold controls is setup-only and
  excluded. Artifact: `scratch/agent/s2459_m5_generated_alternate_equivalence/audit.md`.

- **s2460 — the pre-target static audit finds one explicit terminal edge.**
  `matchKeywordWithPriority` has one generated caller at `0x800A9248`, a valid
  `after_22` continuation, and no resolver in its body. `slotDispatcherIter`
  loads `slot->update_func` and passes it through `LOOKUP_FUNC` at `0x8003E974`,
  so `update_func==0` explicitly reaches `get_function(0)` and can terminate
  before target capture. This selects `H-PreTargetBoundary` for the
  `slotDispatcherIter` family, does not identify the field writer, and rules out
  a generated continuation mismatch at the named match call. The
  `0x8000834C`/`0x80007904` breadcrumbs remain unrelated return delay-slot
  stamps. Static-only; no behavior change. Artifact:
  `scratch/agent/s2460_m5_pre_target_boundary/audit.md`.

- **s2461 — the corrected port capture remains blocked before the M5 target
  join.** The retail oracle passed its whole-RDRAM control with 11,206,982
  writes, reached 512/`0x006AB400`, and observed `0x800078EC` 624 times from
  predecessor `0x8002BEEC`. The port reached 1024 and its indirect resolver
  positive control fired, but crashed 0.6 seconds into the first target frame
  with `last-guest-pc=0x80007904`; no target-phase slot pre-call,
  `m5-dispatch-boundary`, or `get_function(0)` row was emitted. The initial
  all-category attempt was discarded because its bounded slot budget ended in
  phase 6; the phase-8 rerun is a qualified non-result for
  `H-ZeroUpdateTerminal` versus `H-NonzeroSlotThenMatch`, not evidence for
  either. Artifact:
  `scratch/agent/s2461_m5_zero_update_port_fixed/audit.md`.

- **s2462 — the complete static slot-callback audit selects
  `H-UnresolvedWriter`.** The generated tree has 144 `slotDispatcherIter`
  callsites across 72 callers. `allocateNpcSlot` legitimately zeros a new
  context callback at `0x8003E65C`; `spawnNpcOfType` installs the handler
  argument at `0x800400BC`; and `setupNpcUpdateFunctions` supplies nonzero
  handlers on recognized type-table branches. The handler argument is dynamic,
  and the unsupported-type path can leave a fresh context uninstalled, so the
  static census cannot prove a reachable post-install zero or a universal
  nonzero invariant. This does not identify the live s2461 field writer and
  authorizes no guard or dispatch/audio change. Artifact:
  `scratch/agent/s2462_m5_slot_callback_provenance/audit.md`.

## Latest evidence

- **s2452 — the retail second-range boundary has no generated dispatcher body.**
  Static inspection places `0x8002BEEC` inside retail `__osDispatchThread`
  (`0x8002BD74..0x8002BEEF`), immediately before `__osCleanupThread`; the
  generated tree contains no body or label for that runtime dispatcher. The
  known generated alternate at `funcs_23.c:0x8008F2CC` directly calls
  `rs_memset`, continues at `after_6`, and performs writeback-cache setup. The
  88-site direct-call census contains no literal `0x8002BEEC` caller. This
  selects `H-DifferentGeneratedBoundary`, rules out a malformed direct call at
  that literal boundary, and leaves the port-side runtime replacement open.
  Artifact: `scratch/agent/s2452_m5_caller_lowering/audit.md`.
- **s2451 — `rs_memset` does not consume guest `$ra` in either body.** The
  generated and retail bodies have no `$ra` reads/writes or return-dependent
  branch beyond terminal `jr $ra`. This rules out a body-level return/link
  explanation for the missing second-range consumer; the caller/data-path
  divergence remains open.
  Artifact: `scratch/agent/s2451_rs_memset_ra_audit.txt`.
- **s2450 — direct and indirect calls share the generator's no-link contract.**
  The recompiler emits a plain `(rdram, ctx)` invocation for named, reference,
  runtime-lookup, register-lookup, and generated `jal` calls; `needs_link_branch`
  only emits an `after_N` continuation. This selects
  `H-GeneratorIntentionalNoRA` at the source/output contract scope, but does
  not establish whether that contract is semantically valid for `rs_memset`.
  Artifact: `scratch/agent/s2450_direct_jal_audit/`.
- **s2449 — no generated static `rs_memset` callsite writes `ctx->r31`.** All
  expected 88 `jal 0x800078E0` sites were audited with their preceding and
  delay-slot instructions; none writes `r31`. Together with s2448 this selects
  `H-GeneratedDirectCallOmitsRA` and rules out an observed caller overwrite.
  Artifact: `scratch/agent/s2449_static_audit.tsv`.
- **s2448 — every observed static caller already has zero guest `ra`.** A
  fixed paired capture passed retail and port route controls; both arms retained
  1,024 caller rows and every row had `ra=0`. The indirect positive control
  resolved in both arms. This selects `H-CallsiteAlreadyZero` at the live caller
  boundary, without identifying the lowering cause.
  Artifact: `scratch/agent/s2448_m5_static_rsmemset_callsite_abi_fixed/`.
- **s2447 — the generated `rs_memset` entry loses every static caller return
  address.** The corrected phase-scoped rerun passed independent retail and
  port controls; 88 static sites were enumerated and all retained title/hangar
  rows had `ra=0`, including second-range destinations. The indirect positive
  control resolved. This selects `H-StaticCallerContextLost`, without locating
  whether the omission is at the callsite or wrapper.
  Artifact: `scratch/agent/s2447_m5_static_rsmemset_callsites_fixed/`.
- **s2446/s2445 — the port reaches the second-range helper through a stable
  static path.** The live indirect target control resolved, but
  `get_function(0x800078E0)` was not observed; `0x800078EC` is a loop block
  inside `rs_memset`, not an independent target. Port rows at the helper had
  zero saved `ra`, so `H-PortStaticRsMemsetPath` supersedes the earlier
  `H-PortAlternatePath` label. The semantic caller and lowering boundary remain
  unresolved.
- **s2442 — retail grounds the semantic caller.** With independent controls,
  the exact second-range store rows at `0x800078EC` joined
  `PREVIOUS_PC=0x8002BEEC` 632 times; the generated `0x8008F2CC` callsite ran
  six times. Stable store context included `ra=0x8008F2D4` and
  `a0=0x801797B0`. This is retail-only evidence and authorizes no port change.
- **s2430/s2431/s2434 — retail range activity is real.** The first exact range
  is written by `0x800078EC`; the second has `0x80007670` and helper PCs. All
  selected PCs execute in hangar, and exact-store rows at the helper advance
  through the range with varied pre-store words. The semantic helper/caller
  relation was closed by s2442, but the port consumer is still open.
- **s2420–s2428 — M5 route and title controls are valid.** Stub and image arms
  reach title and hangar under the qualified route. The image arm changes DMEM,
  emits generated DMA, reaches `break_pc=0x1328`, and completes SP service; the
  stub does not. The title `0x80015BC8` writer joins the port title task row,
  while no bounded hangar slot/voice/descriptor/filter consumer joins the image
  identity. No output remap, task-data change, gate change, or guard is
  authorized.
- **s2408–s2419 — downstream identity and handoff remain unresolved.** The
  sequence key is reproducible for stage-to-key-on ordering, but later PCM rows
  have a different phase/origin. Retail provides stable phase-specific task/data
  handoff pointers; port emits additional task/data rows and differs at that
  boundary. These are observation-scope results, not permission to remap output.

## Active backlog

Closed investigations are not active work items. This is one monotonic sequence;
#1 is the next campaign priority.

1. **M5 generated alternate equivalence — closed at the direct load boundary.**
   The host-local bridge reaches the target image task; SP completion and
   consumption are confirmed; the scheduler dispatches gspTask (0x800377C8)
   with `event_payload=task_ptr` in the hangar phase (yield-and-restart cycle).
   The explicit raw-byte table shows a coherent aligned-host OSTask layout.
   the corrected callback now makes all three port views agree. The s2493
   retail comparison instead found a distinct type-2 load task at
   `0x80149470`; the port now matches those fields at its own load entry. The
   earlier gspTask mismatch was a descriptor-vs-audio-task join error.
2. **M5 generated image downstream join — active.** s2496 found the first
   host PCM consumer live without an image identity; s2497 selected
   `H-handoff-absent` for the generated AI-buffer path; s2498 selected
   `H-no-consumer-contract` because neither the port candidate writer nor the
   retail target writer joined the consumer under passed controls. s2499
   identifies `kind=2` as host-side image-DMA bookkeeping, not a game-side PCM
   writer. s2500 closes the active generated `kind=1` wrapper census with zero
   callers; s2501 found that the active generated loop actually roots its
   pointer table at `0x801496B0`, while `0x801096B0` is a code address in the
   generated tree. s2502 selects the root-typo hypothesis from independent
   companion symbols and closes the address discrepancy. s2503 selects
   `H-writer-generated` for allocation/table provenance: the generated loop
   allocates, clears, and lays out the sixteen AI buffers, then submits them
   through both AI calls. It did not identify a nonzero PCM payload writer.
   Next, locate that payload writer. Do not map through `gspTask`, infer an
   image identity from hashes or timing, or change task/output fields without
   a named writer and independent retail evidence. s2504 did not find a direct
   generated payload writer; s2505 found no static RSP-destination equality.
   s2506 performed the runtime join and selected
   `H-rsp-destination-joined`. s2507 could not reach the target phase with the
   writer census: the image arm crashed or stalled at 640 in two attempts.
   s2508's same-build A/B selects the image arm as the route failure: silent
   reached title/hangar while image crashed before title in MetalFramebuffer.
   s2509's three-arm capture shows the single image arm reaches the target,
   while only the concurrent image arm stalls before its positive control;
   concurrent-resource is selected for this route, with route/input
   divergence still open. s2510 reproduced the paired-image pre-target
   failure, but the paired-silent control also missed 1024, so shared renderer
   pressure versus route/input or startup-order divergence remained open. s2511's
   staggered-start control made both image arms pass 1024 and reach hangar,
   selecting startup-order as the explanation for that pre-target symptom. The
   later image-arm crash and image-to-PCM payload writer remain open. Next, use
   the now-reachable target route for one batched writer-provenance capture;
   require image-stage and consumer controls before interpreting any writer
   null.
3. **M5 gate polarity/writer join — closed at current capture scope.**
4. **M5 payload-transformation provenance — closed at current capture scope.**
5. **M5 A1 retail flag semantics and pre-target route boundary — closed at
   current capture scope.**
6. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator.
7. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
   H3 is unavailable because the oracle cannot screenshot the LLE path.
8. **Generated-symbol renaming — parked.** Resume only after M5 closes or M3
   obtains a new discriminator; do not invent names for unresolved placeholders.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route is `LLE_UNGATED=1, LLE_SOLO=1`; it reaches title and hangar,
while other arms do not reliably reach both. Menu spin yield is a diagnostic
route aid, not a default behavior change. Factor 5 mappings and independent
controls are in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md).

### M5 audio and image output

Direct service entry/exit, service gate/loop, task/AI boundary, image DMEM work,
generated DMA, reporter association, and target-route SP queue consumption are
live on the port. The image arm's
downstream identity is not yet a legitimate slot, voice, PCM, or output mapping.
Retail proves related ranges and task-field writers are active, including the
second-range helper/caller relation, but does not prove a port equivalent.
Zero-valued rows are diagnostically ambiguous; no output remap or mitigation is
permitted without a named legitimate writer and an `ORIGIN:` line.

### VI, M3, M4, and generated symbols

Retail/port VI selector and current-line publication remain unresolved outside
the qualified route. M3 is parked pending a complete idiom audit. M4
accumulator-origin work is parked. Generated-symbol renaming remains parked at
the useful boundary.

## Superseded conclusions

These were believable before qualified routes or independent controls, but are
superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing input or
  wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- The s2190–s2197 and s2283/s2284 second-origin/A1 matrices, the s2228 and
  s2242–s2259 image/pair crash splits, and s2288's stub-first route conclusion.
- s2304's route-wide PCM gap, s2307's fixed addresses, s2308's zero-fill
  interpretation, s2325's destination-role split, and s2335–s2342's
  inactive-parent/gate labels.
- s2346's output-metadata-writer-absent label and the successive s2347–s2360
  candidate, overflow, value, task-field, and source/payload labels where later
  controls superseded them.
- s2376's input-dependent A1 label, s2379's unresolved flag split, s2383's
  missing-completion label, and s2399's identity-cleared label.
- s2445's `H-PortAlternatePath` label and s2446's original assumption that
  `0x800078EC` was a callable function target; corrected boundary inspection
  and the live indirect positive control superseded them.

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
