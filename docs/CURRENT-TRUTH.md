# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2227–s2262 is summarized in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) §45; the append-only ledger is
authoritative for exact commands, counts, and probe rows.

Maintained in Session 2273 (2026-08-24); behavioral and source evidence is
current through s2273. This iteration built an unchanged Step 1 audio pair,
but the heavy-trace arm crashed before hangar and the corrected reduced-trace
arm stalled at the first 640 target. Neither arm reached the discriminating
stub/image window; no runtime change was made.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name the writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio remains defaulted to the silent `M_AUDTASK` `Broke` stub. The
  Factor 5 image arm is opt-in through `ROGUESQ_AUDIO_UCODE=1`; C88=`1` is
  also a diagnostic behavior arm. Stock `aspMain` is not the game's MusyX /
  Factor 5 contract, and MORT is a separate CPU speech asset.
- `docs/M5-AUDIO-PLAN.md` inventories the active audio stubs/traps/gates and
  defines the phase-keyed task→DMA→service→slot→voice→PCM discriminator and
  rollback conditions. The plan refresh in s2231 changed no runtime default.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. Its host canary is probe data only; it does not gate
  completion, writeback, or DMA.
- The image arm has qualified target-stage rows. s2268 observed one exact
  phase-10 stage/source/consumer match, and s2272 observed two more exact
  phase-10 matches in a phase-gated staggered pair. The silent arm qualified
  through title and hangar in s2272; its phase-8/10/12 source and consumer
  rows were present but all zero. The measured output contract is complete
  for the observed nonzero rows; the image arm remains opt-in.
- The port-side `field348` source spans are cleared by the legitimate
  `rs_memset` setup call at static callsite `0x8008F2CC`; retail independently
  writes both corresponding spans with nonzero values. The missing nonzero
  producer/order boundary remains diagnostic-only and does not authorize a
  writer guard or task rewrite.
- The M5 key-on comparison is open: exact `(origin,width,PC)` tuple buckets
  show both port-only and retail-only values in every common cell. This is a
  contract boundary, not permission to change the key-on path.
- The VI second-origin publisher/cadence is open. Field, current-register,
  timing, and total-`VI` arms recover the split, but none is default-on.
- s2273's first Step 1 pair was route-invalid: the heavy trace reached title
  and the first 640 target before `findOrCreateMaterial` crashed at guest PC
  `0x8000E29C` with one `[missing-func]`, 11 B40 rows, and 20 route-state
  rows; the corrected reduced trace stalled after the 640 target
  `0x00696100` with one `[missing-func]`, six B40 rows, and ten route-state
  rows, then was SIGKILLed. Neither pair arm reached the required hangar
  control. No audio contract null is interpretable.

## Latest evidence

- s2253–s2255 showed intermittent pre-target route failures in image/silent
  pairs; s2254 qualified both arms through title and hangar. These runs do
  not select an image-specific crash or output explanation.
- s2256–s2259 isolated route-load sensitivity at the tested scope. A
  full-trace silent arm failed while a route-only arm qualified; a later
  single reduced-trace silent control qualified through hangar. This is a
  route-validity constraint, not a runtime mitigation target.
- s2260's fixed image/silent pair qualified both arms. The image arm emitted
  target stage rows, including two nonzero hangar rows, while the silent arm
  emitted none. The first result without `ROGUESQ_LOG_AUDIO_RETURN=1` was a
  measurement defect; it is superseded.
- s2261 added PCM-boundary logging. The image arm produced one exact
  phase-10 stage/source/consumer match, but the silent arm failed before
  title, so the pair was route-invalid for comparison.
- s2262 qualified the silent control with the same reduced trace and route.
  Phase 8/10/12 source and consumer rows were `53/48/6` on each side, all
  `fnv=0xF59C39C5`, `nz=0`. It ended at the known post-target aligned-ROM
  abort, after title and hangar qualification. This is single-source port
  evidence for H-SilentPcmAbsent and makes the silent arm usable in the next
  paired output run.
- s2264's same-build pair was route-invalid for output attribution. The
  silent-first arm passed startup, one `[missing-func]`, both 640 controls,
  title `1024 @ 0x00790400`, and hangar `512 @ 0x006AB400` twice; its phase
  8/10/12 PCM source and consumer rows all remained
  `fnv=0xF59C39C5`, `nz=0`. The image-second arm passed startup controls but
  exited before its first 1024 phase and produced no audio/PCM rows, with
  the crash in `MetalFramebuffer` (`last-guest-pc=0x8000b650`). This pair
   selects route-stability work only; it does not compare image output.
- s2265's single-source isolated image+C88=`0` reduced-trace run passed
  startup, one `[missing-func]`, 14 B40 rows, and 28 route-state rows. It
  reached title `1024 @ 0x00790400` at 48.8s and hangar
  `512 @ 0x006AB400` at 78.1s and 114.9s, so the image arm is qualified for
  a paired output run. Phase 8 had `3463/0` image stage rows/nonzero rows;
  phase 10 had `1935/2`, with 2 source and 2 consumer matches; phase 12 had
  935 stage rows and no nonzero rows. PCM source/consumer rows fired in all
  target phases and remained `fnv=0xF59C39C5`, `nz=0`. The process later hit
  the known aligned-ROM abort at `last-guest-pc=0x80001b08`, after target
  qualification. This selects the paired output contract comparison; it
  does not promote the image arm or authorize a guard.
- s2266's image-first pair arm passed startup, one `[missing-func]`, 14 B40
  rows, and 28 route-state rows; it reached title `1024 @ 0x00790400` at
  48.5s and hangar `512 @ 0x006AB400` at 77.7s and 114.1s. Its phase-8/10/12
  image-stage-row counts were `3477/2170/978`, with nonzero counts
  `0/2/0`. In phase 10, the tuple `(dest=0x168250, len=0x300,
  FNV=0x7B70923A)` appeared first as source-only and then as a
  stage-consumer match, with source event `8751` and consumer event `8752`;
  this is one observed tuple with two join records, not two independent
  matches. The silent arm passed startup controls and one `[missing-func]`,
  but crashed in `MetalFramebuffer` at `last-guest-pc=0x8000b650` during
  the 640-width route, before any 1024 phase. The pair therefore selects
  H-PairRouteInvalid and does not interpret image/PCM output differences.
- s2267's isolated silent+C88=`0` arm passed startup, one
  `[missing-func]`, 14 B40 rows, and 28 route-state rows. It reached title
  `1024 @ 0x00790400` at 49.4s and hangar `512 @ 0x006AB400` at 78.9s and
  115.4s. Phase-8/10/12 PCM source and consumer rows were `53/48/5` on each
  side; every row had `FNV=0xF59C39C5`, `nz=0`. The process later hit the
  known aligned-ROM abort at `last-guest-pc=0x80001b08`, after target
  qualification. This selects H-SilentRouteLoadSensitive at the tested scope
  and permits a fresh paired output comparison; it does not identify an
  audio writer or authorize a mitigation.
- s2268's same-build image+C88=`0` / silent+C88=`0` pair passed startup, one
  `[missing-func]`, B40/route-state controls, title, and hangar in both arms.
  The image arm had phase-8/10/12 stage-row counts `3464/3105/1918` and
  nonzero counts `0/2/0`. In phase 10, one row
  `(dest=0x167650, len=0x300, FNV=0x7B70923A, nz=639)` matched both source
  and consumer records at `0x80167650`; the source and consumer also had
  `FNV=0x7B70923A, nz=639`, and the join reported
  `ordering_violation=0`. A second nonzero stage row
  `(dest=0x167350, len=0x300, FNV=0x60F910DE, nz=621)` had no corresponding
  source/consumer join in the capture. The silent arm had no image-stage
  rows, and its phase-8/10/12 PCM source/consumer rows were all
  `FNV=0xF59C39C5, nz=0`. This selects
  H-CompleteImageOutputContract for at least one measured image tuple, while
  leaving completeness of the second stage row open. The silent process hit
  the known post-target aligned-ROM abort; the image driver ended by its
  watchdog after target qualification.
- s2269's same-build pair passed the pre-target controls in both arms—one
  `[missing-func]`, six B40 rows, and ten route-state rows each—but both arms
  stalled at the final width-640 phase and returned the prescribed phase-1024
  timeout. Neither arm reached title/hangar or emitted target image-stage or
  phase-gated PCM rows. This selects H-PairRouteInvalid for this capture and
  does not reinterpret the qualified s2268 output tuple.
- s2270's same-build image-first pair passed the image controls—one
  `[missing-func]`, 14 B40 rows, and 28 route-state rows—and reached title
  `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400` twice. It later exited
  with `CRASH: 36` at a width-640 transition. The silent arm passed one
  `[missing-func]`, six B40 rows, and ten route-state rows but timed out in the
  driver before any 1024 phase. The image run therefore has no paired silent
  target window, and this capture selects H-PairRouteInvalid. The independent
  driver phase timeout and silent run's absence of a 1024 transition agree.
  Single-source, unpaired image evidence did show phase-10 rows
  `(0x168550,0x300,0x60F910DE,621)` and
  `(0x168850,0x300,0x7B70923A,639)`; each later had exact source and consumer
  matches with `ordering_violation=0`. This does not classify the paired
  output contract because the silent arm never entered the target window.
- s2271's same-build silent-first/image-second pair passed one
  `[missing-func]`, 14 B40 rows, and 28 route-state rows in each arm. The
  silent arm reached title `1024 @ 0x00790400` twice but never reached the
  `512 @ 0x006AB400` hangar phase; it later stopped in
  `initSampleStreamBlockCache+1284` with last guest PC `0x80001C94`. The
  image arm reached title once and hangar twice, then stopped at the known
  post-target abort with last guest PC `0x80001B08`.
  Its two nonzero phase-10 rows were
  `(0x168850,0x300,0x60F910DE,621)` and
  `(0x168B50,0x300,0x7B70923A,639)`; both were `stage-only`, with no source
  or consumer join. The silent arm had no hangar image-stage window. With
  s2270's opposite-order pair, image qualification follows the image arm
  while the silent arm fails to qualify hangar in both launch positions;
  this selects arm-specific paired-route sensitivity at the tested scope,
  not a pure launch-order explanation, and leaves the output contract open.
- s2272 first exposed a driver defect: when the silent arm died before 512, the
  shell's compound gate also fell through and launched the image arm without a
  512 confirmation. That continuation was discarded. The corrected driver
  launched the image arm only after emitting
  `silent_first_512=observed; launching image`. Both arms passed startup,
  one `[missing-func]`, 14 B40 rows, and 28 route-state rows. The silent arm
  reached title `1024 @ 0x00790400` at 48.5s and hangar
  `512 @ 0x006AB400` at 77.4s and 114.0s. The image arm reached title at
  49.5s and hangar at 78.8s and 115.4s. The silent arm remained qualified
  after image launch, selecting H-InitialPairContention at this recipe scope
  and refuting live overlap as the reason for the earlier silent failure.
  The image phase-10 summary had 1970 stage rows, two nonzero rows, two source
  matches, two consumer matches, zero stage-only rows, and zero ordering
  violations. The rows were `(0x168B50,0x300,0x2B9E9631,621)` and
  `(0x168E50,0x300,0x6ADD4218,639)`; each had exact source and consumer
  tuples with `source_before_consumer=1`. This selects
  H-CompleteStaggeredTarget at the measured scope and closes the previously
  unmatched image row. Both processes ended at the known post-target abort
  with last guest PC `0x80001B08`; no runtime change was made.
- Independent retail oracle work established the whole-RDRAM control, both
  target origins, nonzero writes to both `field348`-derived spans, and the
  retail task/output writer family. It has not yet joined a retail write to a
  port image-stage row.

## Active backlog

Closed investigations are not active work items. The sequence is monotonic.

1. **M5 Step 1 stub/image validation.** Re-run the unchanged pair with the
   canonical reduced trace that qualified s2272; do not interpret task/output
   nulls until both arms pass title `1024 @ 0x00790400` and hangar
   `512 @ 0x006AB400`. Keep `m5-step1-task-output-contract` active.
2. **M5 key-on tuple contract.** Explain the bidirectional port/retail tuple
   difference using a new pointer-versus-branch discriminator. No key-on
   return or mitigation change follows from the existing table.
3. **M5 A1 second-origin transition.** Identify the natural host field
   publisher and callback-versus-total-`VI` cadence. Diagnostic recovery arms
   remain opt-in.
4. **M5 drain in-loop tick A/B.** Parked after s2125–s2128 failed to place
   both arms in a target comparison. Resume only with a new renderer or
   ground-truth discriminator.
5. **M3 crash work.** Resume only as a systematic idiom-class audit with a
   named discriminator; the dormant `slotDispatcherIter+872` class has
   thousands of clean guarded hangar calls and no authorized mitigation.
6. **Hangar visual artifact.** Malformed-triangle H2 and consumer-mode H1 are
   refuted. H3 is unavailable because the oracle cannot screenshot the LLE
   path; do not repeat the capped `0xD60` scan.

Generated-symbol renaming is closed at the useful boundary. The remaining
placeholder holds are `func_8000040C`, `func_800927B0`, `func_80092A54`,
`func_80092CF0`, and `func_800E9AE0`; do not re-census or invent names.

## Durable boundaries

### Route, rendering, and Factor 5

Factor 5 command mappings and independent-ground-truth requirements are in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result. The accepted four-arm route table selects
`LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title and hangar, `01` reaches
title only, and `10`/`00` reach neither. Menu spin yield is a diagnostic route
aid, not a default behavior change.

### M5 audio and image output

Direct service entry/exit, the service gate/loop, slot-0 status sequence, and
the task/AI boundary are live on the port. Retail independently matches the
status cycle and reaches the target route. s2132–s2140 close the sampled
AI-status and RSP-image/task-field boundaries: MORT speech is separate, both
systems write `data_ptr+0x100`, and stock `aspMain` is not a substitute.

The measured output boundary is now complete for the observed nonzero rows.
The image arm changes DMEM, completes, and emits generated DMA. s2268
qualified one exact nonzero phase-10 stage/source/consumer tuple; s2272's
phase-gated stagger qualified both arms and produced two additional exact
nonzero tuples, with source-before-consumer ordering and no stage-only rows.
The silent control's independently qualified PCM boundary remains all-zero.
Retail writes the corresponding field spans and a separate task/output span.
This closes output-contract completeness at the measured scope without
promoting the image arm or authorizing a writeback, consumer, slot, gate, or
guard change.

Do not re-flip the image default, force C88, skip or allow
`matchKeywordWithPriority`, add a wait/slot guard, or land a copyToRAM/CIMG
writeback guard. Do not treat last-guest-PC `0x8000834c` as the abort site.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-`VI` arms recover the
split; the natural host publisher and cadence are unidentified.

### Key-on, M3, and M4

Retail executes the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with no guard
hits. The exact phase-keyed tuple table is complete and bidirectionally
different at all common cells; dynamic pointer operands versus branch state
remain the useful discriminator.

The `-0x25A4` pointer-chase, six-site PIC, ten-site audio-slot,
slot-dispatch, two-line overlay-move, and leftover `fake_func_*` size class
audits are closed at their stated scopes. M3 resumes only as an idiom-class
audit. M4 accumulator/beam evidence rules out the old shade-lane theory but
is not pixel ground truth.

## Superseded conclusions

Detailed reversals are archived in `PROJECT-OVERVIEW.md` §§26 and 35–45 and
the append-only ledger. Operationally:

- The old overlay/menu explanation, “640 is intrinsically flaky,” missing
  input/wait-return claims, and unqualified PCM-null claims were believable
  before the qualified route and same-run controls; they are superseded at
  their measured scopes.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations were believable before the complete
  task/consumer and writer-specific tables. Current evidence shows real image
  work, mixed retail gate behavior, and sampled nonzero joins; none permits a
  default or guard change.
- The s2190–s2197 second-origin and caller conclusions were coverage/scope
  artifacts. The open boundary moved to host VI-state publication/cadence.
- s2228's detail-ring crash and s2242–s2259's image/pair crash splits are
  intermittent route-load observations, not selected intrinsic image or
  writer defects. s2254 and s2259 provide qualified controls.
- s2271's order-swapped pair made arm-specific paired-route sensitivity look
  plausible because the image arm qualified when second while the silent arm
  failed to reach hangar when first. s2272's phase-gated stagger kept the
  silent arm qualified after the image launch and closed both image joins, so
  the earlier result is superseded as an intrinsic arm defect; initial
  pre-target paired contention remains the selected route explanation at this
  recipe scope.
- s2269's pre-target controls followed by a shared width-640 stall and s2270's
  image-first/silent split are route-invalid observations. They do not make
  the qualified s2268 output tuple disappear or explain the route-load
  sensitivity; the next order-swapped pair tests that boundary.
- s2260's first pair was measurement-invalid because the route identity gate
  was absent; s2261's pair was route-invalid because the silent arm failed
  before title. s2262 supplies the missing qualified silent control, without
  selecting an output fix.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical addresses and
  should be phase-gated by VI callbacks.
- A null is worthless without a same-run positive control. Batch every arm
  and counter in one build/run, scope budgets to the phase, and use VI gates
  rather than elapsed time for animated scenes.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`,
  or `git reset --hard`. If `lib/` changes, export submodule patches in the
  same iteration.
- A mitigation is not an explanation: name the writer, state legitimacy,
  and add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
