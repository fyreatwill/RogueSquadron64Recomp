# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history is
in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2147
(2026-08-21); behavioral and source evidence is current through s2147.

This file is intentionally compact. The s2080–s2108 archive is in
`PROJECT-OVERVIEW.md` §40.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield remains
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- `docs/M5-AUDIO-PLAN.md` controls incremental audio work. The default audio
  path is a silent `Broke` stub. The Factor 5 image arm is opt-in through
  `ROGUESQ_AUDIO_UCODE=1` and is not defaulted on.
- The image arm performs real DMEM work and generated DMA writes, then returns
  `Broke` and fails the reserved host canary. The s2113 contract witness
  records the generated completion edge as guest PC `0x1328`, host exit
  `Broke`, task `output_buff=0`, and the phase-keyed post-DMA/PCM joins.
- The s2135 static MORT boundary census selected
  `H-ExistingFactor5ConfigMatches`: the companion retail `aspMainText` image
  is exactly `factor5b_rsp.toml` ROM `0x09ABE0..0x09BB60`, with companion
  `aspMainData` at ROM `0x0A5A00..0x0A5D20`. The generated image reads the
  audio task's `data_ptr`/`data_size`, uses the `data_ptr+0x100` output DMA,
  and exits through `break` PC `0x1328` as `Broke`. Retail MORT is not a
  second RSP image: manifest entry `speech` is the uncompressed ROM range
  `0x583D90..0x8A1174`, containing 546 MORT descriptors consumed by the
  named CPU voice path. This rejects a new MORT RSP segment at the current
  source/config boundary; no runtime dispatch or default-arm change follows.
- The s2136 retail task-buffer census passed its independent whole-RDRAM
  positive control (`45,200` writes after the threshold), reached title VI
  `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`, and supplied 256
  post-store samples for each watched task field. The fixed `aspTask` fields
  were `ucode=0x80099FE0`, `ucode_data=0x800A4E00`, nonzero `data_ptr` values
  `0x80173B20`/`0x80171CE0`, and `data_size` values `2`/`1`; both
  `output_buff` fields had zero writes. This selects
  `H-RetailTaskMatchesFactor5b` at the task-field boundary and rejects
  `H-RetailOutputBuffContract` and `H-RetailTaskBoundaryUnresolved` for the
  covered route. The run did not dynamically watch each retail
  `data_ptr+0x100` destination, so that downstream edge remains an explicit
  validation item; no port task-field, output-routing, RSP-config, or
  default-arm change follows.
- The s2137 same-build port task comparison passed positive dispatch controls
  and reached title VI `1024 @ 0x00790400` plus hangar VI
  `512 @ 0x006AB400` in both the `musyx_stub` and opt-in `factor5_ucode_b`
  arms. The stub emitted zero audio DMA and zero-nonzero PCM rows. The image
  emitted real DMEM-to-RDRAM DMA with fixed `ucode=0x80099FE0`,
  `ucode_data=0x800A4E00`, nonzero task `data_ptr`/`data_size`, and zero
  `output_buff` fields; its stage-3 `field348=0x80178C80` destination was
  `0x80178D80`, exactly `field348+0x100`. In hangar phase 10, two image
  stage-2 ranges joined both PCM source and consumer callbacks exactly:
  `nz=621`, FNV `0x2B9E9631`, and `nz=639`, FNV `0x6ADD4218`, with
  `complete=1` and no ordering violations. Together with the independent
  s2136 retail task-field line, this selects `H-PortTaskFieldsMatchRetail`
  at the sampled port boundary and rejects output-buffer mismatch,
  data-pointer/output-relation mismatch, and coverage-unresolved hypotheses.
  The image still exits at guest break PC `0x1328` with `canary_ok=0`; no
  task-field rewrite, output-route change, new RSP config, or default-arm
  change follows.
- The s2138 host-only MORT census compiled the independent
  `CMORTDecoder::Decode` reference and passed the speech positive controls:
  546 descriptors, all `MORT` headers, descriptor-type counts
  `419/59/36/17/9/6`, and rates `8000:440`/`16000:106`. The mandated rows
  `0,1,419,545` all decoded to stable nonempty PCM rows, selecting
  `H-MORTReferenceMatches` only for those four 8000-Hz/type-0 samples. The
  selection covers neither the 16000-Hz class nor nonzero descriptor types,
  so the full codec-variant boundary remains open; no audio arm, task ABI,
  output route, or default-arm change follows.
- The s2139 host-only MORT census reused those positive controls and decoded
  indices `4,58,90,104` across descriptor types `1,2,3,5` and both rates.
  All four rows were complete, signed-16-bit, and nonempty: type 1/8000 had
  `67200` samples and FNV `0x998CAF3C`, type 2/8000 had `110080` samples and
  FNV `0x58E9C3D2`, type 3/16000 had `141600` samples and FNV
  `0xC68F3CAF`, and type 5/16000 had `205760` samples and FNV
  `0xBF30B582`. This is single-source reference evidence selecting
  `H-MORTReferenceMatchesExtended` for the
  sampled rate/type classes and rejects layout/endian failure,
  codec-variant failure, and reference unavailability at those rows. Type 0
  at both rates and type 4 remain unsampled; s2140 separately closed the
  sampled retail `data_ptr+0x100` output boundary. No audio arm, task ABI,
  output route, host shortcut, guard, or default-arm behavior changed.
- The s2140 retail oracle watch passed its independent whole-RDRAM positive
  control with `363506` writes, the task-block route control with `41220`
  writes, and reached title `1024` plus hangar `512 @ 0x006AB400`. It wrote
  both exact observed destinations: `0x00173C20` (`data_ptr=0x80173B20`)
  `490` times and `0x00171DE0` (`data_ptr=0x80171CE0`) `1291` times. The
  bounded surrounding ranges were active (`115180` and `197106` writes),
  and the task block retained both source pointers with the expected fixed
  `0x80099FE0`/`0x800A4E00` fields. Post-store samples at both exact
  destinations primarily identified writer PC `0x80090CA4`. Together with
  the s2137 port-side `field348+0x100` row, this supplies independent retail
  and port lines selecting `H-RetailDataPtrOffset100` at the sampled output
  boundary. No task-field, output-route, audio-arm, host shortcut, guard, or
  default-arm change follows.
- The s2142 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800C64B0`: no-edit regeneration left `func_800C64B0` in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `initHangarDisplayItemTimers` in `.ovl.mission` at the same start, size
  `0x11C`, and end boundary `0x800C65CC` immediately before unchanged
  `tickHangarDisplayItemAnimations`. The generated prototype, definition,
  overlay entry, and only generated caller (`hangarVehicleDisplayNpcHandler`
  at `jal 0x800C64B0`) all used the human name. The prior s417 live-crash
  warning remains a runtime-risk record; this static table found no
  boundary or caller conflict. The full pipeline succeeded; no game run or
  runtime behavior changed.
- The s2143 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800E71D0`: no-edit regeneration left `func_800E71D0` in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `transformCraftAnchorsApplySubFx3` in `.ovl.mission` at the same start,
  size `0x1C0`, and end boundary `0x800E7390` immediately before unchanged
  `tickFighterSquadronWithSplinePaths`. The leftover `fake_func_800E71C8`
  at `0x800E71C8` size `0x8` was unchanged. The generated prototype,
  definition, overlay entry, and only generated caller
  (`tickFighterSquadronWithSplinePaths` at `jal 0x800E71D0`) all used the
  human name. The prior s413 live-crash warning remains a runtime-risk
  record; this static table found no boundary or caller conflict. The full
  pipeline succeeded; no game run or runtime behavior changed.
- The s2144 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800EC110`: no-edit regeneration left `func_800EC110` in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `allocObjectPoolNode` in `.ovl.mission` at the same start, size `0x278`,
  and end boundary `0x800EC388` immediately before unchanged
  `unlinkAndFreeChildNpcNode`. The leftover `fake_func_800EC10C` at
  `0x800EC10C` size `0x4` was unchanged. The generated prototype,
  definition, overlay entry, and only generated caller
  (`createAndInitObject` at `jal 0x800EC110`) all used the human name. The
  prior s415 live-crash warning remains a runtime-risk record; this static
  table found no boundary or caller conflict. The full pipeline succeeded;
  no game run or runtime behavior changed.
- The s2145 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800EC6F0`: no-edit regeneration left `func_800EC6F0` in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `tickCraftMountedAnimationEffect` in `.ovl.mission` at the same start,
  size `0x538`, and end boundary `0x800ECC28` immediately before unchanged
  `craftMountedAnimationNpcHandler`. The leftover `fake_func_800EC6EC` at
  `0x800EC6EC` size `0x4` was unchanged. The generated prototype,
  definition, overlay entry, and only generated caller
  (`craftMountedAnimationNpcHandler` at `jal 0x800EC6F0`) all used the
  human name. The prior s415 live-crash warning remains a runtime-risk
  record; this static table found no boundary or caller conflict. The full
  pipeline succeeded; no game run or runtime behavior changed.
- The s2146 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800ED150`: no-edit regeneration left `func_800ED150` in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `claimSongSlotForCurrentHandle` in `.ovl.mission` at the same start,
  size `0xB0`, and end boundary `0x800ED200` immediately before unchanged
  `tickActiveSongSlots`. The leftover `fake_func_800ED148` at
  `0x800ED148` size `0x8` was unchanged. The generated prototype,
  definition, overlay entry, and only generated caller
  (`tickActiveSongSlots` at `jal 0x800ED150`) all used the human name.
  The prior s403 live-probe miss remains a runtime-risk record; this
  static table found no boundary or caller conflict. The full pipeline
  succeeded; no game run or runtime behavior changed.
- The s2147 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800FEF10`: no-edit regeneration left `func_800FEF10` in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `stepObjectOrientationTowardTarget` in `.ovl.mission` at the same start,
  size `0xEF0`, and end boundary `0x800FFE00` immediately before unchanged
  `resolveCraftAnimationNodeHandles`. The leftover `fake_func_800FEF04` at
  `0x800FEF04` size `0xC` was unchanged. The generated prototype,
  definition, overlay entry, and both generated callers
  (`updateSplineCraftTransform` and `updatePlayerCraftPhysics` at
  `jal 0x800FEF10`) all used the human name. The prior s416 live-crash
  warning remains a runtime-risk record; this static table found no
  boundary or caller conflict. The full pipeline succeeded and linked
  `_stepObjectOrientationTowardTarget`; no game run or runtime behavior
  changed. Mission-overlay human-versus-placeholder mismatches are now
  exhausted.
- The s2133 same-build stub/image comparison reached title and hangar in both
  arms. In image phase 10, two generated stage rows were nonzero (`nz=621`
  and `639`) and each had exact source/consumer PCM joins with matching FNV,
  while the stub arm remained zero. This selects `H-PortAIQueueMatches` at
  the sampled phase-gated host callback boundary; the run-lifetime
  `[pcm-sanity]` sampler missed those transient rows and is not evidence
  against the join. No AI-status, task-routing, output, wait, or default-arm
  change is authorized.
- In the route-qualified hangar sample, stage-2 `0x6F0`/`0x300` rows matched
  nonzero DMA payloads and PCM source/consumer spans exactly. The same scope
  had `output_buff=0`, `canary_ok=0`, and `exit=1`. This selects
  `H-ImageDestIsPCM` only at the sampled stage-2 boundary; it is not
  permission to change the task ABI or output routing.
- The s2113 image-arm table independently matched two nonzero phase-10
  stage-2 spans (`nz=621` and `639`) to actual dmem-to-RDRAM DMA ranges and
  exact PCM source/consumer spans, with completion before both PCM edges and
  no ordering violation. This rejects `H-WritebackLoss` and `H-NoValidOutput`
  at that sampled boundary and selects `H-TaskExitMapping` for the legitimate
  `break 0`/`Broke` edge. `output_buff=0` remains an ABI-semantics question,
  not evidence of a failed route.
- The required same-run stub/image A/B did not reach target phases in one
  pair: the image arm reached title/hangar while the stub arm crashed in
  phase 6; an earlier pair had the inverse pre-target crash. The successful
  image contract result is therefore single-arm evidence, not a cross-run A/B
  conclusion. No output or exit mapping change is authorized.
- The s2114 paired validation and its explicit-LLE retry both failed before
  target-phase coverage: the first pair bus-faulted after the 640-wide phase,
  while the retry's image arm exited pre-target and its stub arm remained at
  640-wide until SIGKILL. The phase logger fired only pre-target controls, so
  this adds no contract evidence and does not select any ABI hypothesis.
- The s2115 pair again split before the contract discriminator: the stub arm
  reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, while the
  image arm's positive LLE/audio controls fired (194 LLE tasks, 42 audio
  dispatches) before a pre-target SIGSEGV in `waitForAnyAudioSlot+1060`, last
  guest PC `0x8000834c`. This is another coverage failure; no ABI hypothesis
  is selected.
- The s2116 four-arm C88 coverage contrast reached title `1024 @ 0x00790400`
  and hangar `512 @ 0x006AB400` in both image arms and in the C88=0 stub arm.
  The C88=1 stub arm alone crashed pre-target at
  `waitForAnyAudioSlot+1060` with last guest PC `0x80095d54`. Both image arms
  passed positive LLE/audio controls and emitted target task rows, so C88 did
  not split image-arm admission in this recipe. Per the planned discriminator
  this selects `H-RouteRecipeFailure` because one stub control missed target
  coverage; it does not select an image C88 hypothesis and reopens the C88=0
  contract A/B.
- The s2117 prescribed C88=0 contract pair was a coverage failure. The stub
  control reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`,
  with 3006 LLE tasks, 87 stub dispatch controls, and target stub rows. The
  image arm passed its LLE/audio positive controls (557 LLE tasks and 48 real
  audio dispatches) but stopped in the pre-target 640-wide phase at
  `renderFlatMeshFaceGroup+17288`, guest PC `0x8000e7fc`, after a bus error.
  It emitted no target ABI, DMA, join, or PCM rows. This selects no contract
  hypothesis; absent image rows are coverage failure, not evidence for a
  destination, writeback, or output-validity claim.
- The s2118 prescribed C88=0 pair reached title and hangar in both arms. The
  stub control passed positive controls with 2859 LLE tasks and 85 stub
  dispatches; its shared title-phase rows showed the silent contract
  (`dma_count=0`, `canary_ok=1`, `break_pc=0`, `exit=1`). The image arm passed
  positive controls with 4354 LLE tasks and 108 real dispatches. In hangar
  phase 10 it produced two nonzero stage-2 spans (`nz=621` and `639`) whose
  generated `0x6F0`/`0x300` DMA ranges and PCM source/consumer rows matched by
  guest span, byte count, full-span hash, and nonzero count; the matched join
  completed before both PCM edges with no ordering violation. Image rows
  recorded `output_buff=0`, `canary_ok=0`, `break_pc=0x1328`, and `exit=1`.
  This same-build target comparison selects `H-TaskExitMapping` and rejects
  `H-OutputRoute`, `H-WritebackLoss`, and `H-NoValidOutput` at the sampled
  boundary. The stub later crashed after hangar in `do_rom_read`; that does
  not erase the already-observed target rows. No output or exit mapping
  change is authorized.
- The s2119 retail oracle gate census passed its independent whole-RDRAM
  positive control (`38511` writes), reached title `1024 @ 0x00790400` and
  hangar `512 @ 0x006AB400`, and recorded `17` writes to physical `0xA0F50`.
  The target post-store samples contained both `0x00000000` and
  `0x01000000`; the observed writer-PC samples were `0x8008EB7C` (zero),
  `0x8008ED48` (zero), and `0x8008EC88` (nonzero). The auxiliary countdown
  watch at `0x14998A` wrote once; the worker flag at `0x14974C` wrote `17824`
  times with three nonzero values. This is single-source retail evidence:
  it rejects `H-GateNeverLive` and selects `H-GateMixed`, but does not yet
  identify which port writer controls the live task route.
- The s2120 same-build retry supplied the independent port line. Both C88 arms
  reached title and hangar, and both showed the named
  `reapplyDisplayMode:reapply-success` writer at `0x8008EC88` with final gate
  0 versus 1. C88=0 produced two nonzero phase-10 stage-2 spans (`nz=621`,
  `639`) and one exact source/consumer PCM join; C88=1 produced no nonzero
  stage or phase-10 PCM row. This selects `H-C88-ReversedOrSuppressing` at
  the sampled route: the named writer is causal, but gate 1 suppresses the
  observed nonzero image/PCM activity. The first s2120 pair was a coverage
  failure because its C88=0 arm crashed before title; it is not evidence.
- The title path is separately selected as `H-InputZero`: title-stage input,
  transform, and DMA payloads were zero. A hangar sample had nonzero input,
  transform, and matching DMA payload, rejecting transform annihilation and
  DMA write loss for that sample.
- The image-stage writer reaches the host canary span through three guest
  loops. The only reachable image-side `Broke` edge is the generated
  `break 0` after the final DMA write. This does not establish the meaning of
  every task-field destination.
- C88 testing with explicit 0 versus 1 reached both target phases in both
  arms in the s2120 retry. C88=0 stored gate 0 and produced the sampled
  nonzero stage/PCM join; C88=1 stored gate 1 and produced no nonzero
  stage/PCM row. Together with the retail writer-PC census, this selects
  `H-C88-ReversedOrSuppressing` at sampled port gate scope, not a default
  behavior change.
- Retail independently observed the live `0x8008EB40` B40 writer. In the
  phase-keyed port/host route tables, both arms fired B40 write/return and the
  same early reapply entry/success edges; B40=0 stored 0 while B40=1 stored 1.
  The s2111 whole-tree census covered 71 generated `lbu` sites. Both arms
  reached title VI `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`. In
  both target phases the unique read/branch table matched exactly: every
  observed value was 0, with the same guest PCs, branch PCs, directions, and
  route ordinals. The phase-7 route origin differed (`0x0062B800` versus
  `0x00695C00`) and the VI transitions differed only in timing. This refutes
  `H-B40-Consumer` at the sampled route boundary and selects
  `H-RecipeVariance`; the phase-7 origin/state writer remains open.
- The s2112 phase-keyed route-state table was positive in both arms. At phase
  7, callsite, `reapplyDisplayMode` entry, and route rows matched on all four
  arguments, `a1_gate`, state bytes `0x80141AD0`/`0x8013B038`/`0x80141AD1`,
  route ordinal, and boundary VI state; both arms had origin `0x00695C00`.
  Both later recorded `audio_nonzero=0` and function exit `0`. Independent VI
  traces differed in timing and later phase count only, so this pair selects
  `H-RecipeTiming` and does not identify a phase-7 state writer.
- The s2121 retail oracle census passed its independent whole-RDRAM positive
  control (`10000` callbacks, then automatic removal), reached title VI
  `1024 @ 0x00790400`, and reached hangar VI `512` including
  `0x006AB400`. All eight `musyxKeyOnVoice` execution watches recorded zero
  hits and the execution-watch table had zero rows. This is single-source
  retail evidence for `H-KeyOnRetailDead` at the covered route; it does not
  prove the port class is dead or make any guard-removal change safe. The
  initial prescribed run was unevaluable because its global 200-hit cap was
  exhausted by boot writes; the fixed same-control run enabled detail logging
  for all eight PC watches after the positive-control threshold.
- The s2122 port-side key-on census passed the same positive route controls
  (`2841` LLE tasks, `84` audio dispatches, title `1024 @ 0x00790400`, and
  hangar `512 @ 0x006AB400`). In hangar phase 10, five entries reached the
  normal tail five times; each entry took four nonzero divide witnesses with
  divisor `0xC0`, and none of the eight early-return guard sites fired. Two
  qualifying slot transitions at `0x800909F4` were `0x65 -> 0x00` and
  `0x78 -> 0x02`. The first emitted table row is the phase-control row before
  the first entry; the subsequent event rows are the measured counts. This
  selects `H-PortKeyOnNormal` for the sampled port route and rejects the
  port-dead, guard-hit, and invalid-divisor alternatives without authorizing
  any guard change. The run later hit the existing unaligned `do_rom_read`
  assertion after target coverage; that terminal crash is unrelated to this
  contract result.
- The s2123 retail completion-wait census passed its independent whole-RDRAM
  control (`40799` writes, with the watch removed at `10000`), reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and continued to `3875`
  VI. Exact retail writer rows showed `0x80091ECC` seeding the `0x8014998A`
  halfword to `0x0010` and `0x800916A4` decrementing it; the aligned word
  had `3086713` reads and `7669` writes. The worker word at `0x14974C` had
  `22292` reads and `12455` writes, including the retail `0x8008F490`
  `0x03` writer at hangar VIs `2267` and `3139`. The status range had
  `48507` reads and `10675` writes; retail `serviceVoicePoolFrame` executed
  `3324` times and its `0x8009B7EC` byte-store reached `0x154620` at hangar
  VI `2895`. Independent execution witnesses also recorded
  `waitForMusyXAudioTaskDone=5`, `shutdownMusyXVoices=3`,
  `drainAudioAndFinalizeSpeechBuffer=1`, `musyxSynthFrame=3832`, and
  `waitForAnyAudioSlot=4`. Together with the generated/companion instruction
  offsets, this selects `H-RetailWaitContract` at the covered retail route
  and rejects retail-no-wait and pre-target-only explanations. It does not
  select the port pump arm, remove a wait guard, or authorize any runtime
  change; the evidence is an independent retail line plus generated/companion
  instruction mapping.
- The s2124 same-build port pump A/B was a coverage failure. Pump-on passed
  the LLE/task controls, reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and at phase 12 emitted the wait contract through
  `waitForAnyAudioSlot` return plus audio-drain enter/exit. It then hit the
  existing `do_rom_read` crash family, last guest PC `0x80001B08`.
  Pump-off reached only 640-wide phases, emitted pre-target post-wait and
  drain controls, and crashed at the existing `0x8000B650` breadcrumb before
  title. No target-phase countdown, spin-2, or pump-stall rows were present
  for pump-off. This selects `H-CoverageFailure`; it does not select a pump
  hypothesis or authorize a wait/guard change.
- The s2125 phase-repaired pump A/B reached title `1024 @ 0x00790400` and
  hangar `512 @ 0x006AB400` in both arms. Positive controls fired in both
  arms (`2845`/`3552` LLE tasks and `85`/`94` audio dispatch rows for
  pump-on/off). At the target phase both arms emitted the same ordered wait
  edges through `wait-post-any-slot`, audio-drain enter/exit with one
  iteration, and the same `waitmusyx-spin2-arm n=0 val=1` before the
  existing `do_rom_read` crash (`last guest PC 0x80001B08`). Neither arm
  emitted `audio-wait-pump-stall` or `waitforslot-guard-fire`. This refutes
  `H-PumpRequired` and `H-SecondFlagOwner` at the sampled route and selects
  `H-PumpIrrelevant` only for route admission/target wait behavior; the
  phase-12 ordered contract is matched, but no direct countdown seed/exit
  row was emitted, so no wait or task semantic change is authorized.
- The s2126 drain-tick A/B built successfully and supplied positive LLE/audio
  controls in both arms. The default-tick control reached title VI `1024 @
  0x00790400` and hangar VI `512 @ 0x006AB400`, with five drain entries and
  four clean `iters_this_call=1` exits, and no drain timeout, forced-idle, or
  wait-for-slot guard rows. The `ROGUESQ_DRAIN_INLOOP_TICK=0` arm reached only
  the pre-target 640-wide phases and timed out at the 600-second gate; a
  phase-repaired `tools/probe.sh` retry also died at VI 640 with last guest PC
  `0x8000B650`. This selects `H-CoverageFailure` for s2126 and supplies no
  evidence for or against the drain contract. No audio, wait, task, or guard
  behavior changed.
- The s2127 phase-repaired drain-tick A/B again passed positive controls in
  both arms. The default-tick control reached only VI 640 and crashed in the
  existing RT64 `fullSync`/Metal barrier path with last guest PC
  `0x8000834c`, so it never reached the title or hangar gates. The tick-off
  arm reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, with
  five drain entries, four clean `iters_this_call=1` exits, and no timeout,
  forced-idle, or wait-for-slot guard rows before the existing
  `do_rom_read` crash at `0x80001B08`. This selects `H-CoverageFailure` again
  and supplies no drain-contract comparison; no audio, wait, task, or guard
  behavior changed.
- The s2128 prescribed pair first proved stale: the built binary contained no
  `ROGUESQ_DRAIN_INLOOP_TICK` gate. After the required make-ELF, N64Recomp,
  fixup, and CMake regeneration, a narrow legacy-s1976 fixup gate was added
  around the existing host tick injection and the pair was rerun. The fixed
  control enabled the gate, passed LLE/audio controls, and reached title and
  hangar before the existing `do_rom_read` crash at `0x80001B08`; tick-off
  passed controls but stopped pre-target at VI 640 in the existing RT64
  `fullSync`/Metal barrier family at `0x8000834c`. This is the third
  consecutive `H-CoverageFailure` result for the drain-tick A/B and selects
  no drain hypothesis. The drain thread is parked; no audio, wait, task,
  renderer, or guard behavior changed.
- The s2129 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800AD380`: removing the duplicate main-overlay claim and naming the
  mission-overlay entry caused the ELF to emit
  `computeTrackedObjectWorldAnchor` in `.ovl.mission` at that address with
  size `0x98`, unchanged boundary `0x800AD418`, and the generated prototype,
  definition, overlay entry, and three callers all resolving to the human
  name. The full make-ELF/N64Recomp/fixup/CMake pipeline succeeded; no game
  run or runtime behavior changed.
- The s2130 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800AE3F0`: the no-edit regeneration left the placeholder in place, while
  the prescribed two-line mapping move caused the ELF to emit
  `initPlayerCraftTrailBuffers` in `.ovl.mission` at the same start, size
  `0x1D4`, and end boundary `0x800AE5C4`. The generated prototype,
  definition, overlay entry, and only generated caller all used the human
  name. The prior s407 live-crash warning remains a runtime-risk record; this
  static table found no boundary or caller conflict. The full pipeline and
  diff checks succeeded; no game run or runtime behavior changed.
- The s2131 bounded generated-symbol unit selected `H-MissionMapping` for
  `0x800C41B0`: no-edit regeneration left `func_800C41B0` in place, while the
  prescribed two-line move caused the ELF to emit `plotRadarBlipColumn` in
  `.ovl.mission` at the same start, size `0x1AC`, and end boundary
  `0x800C435C`, immediately before unchanged `plotRadarBlipRow`. The generated
  prototype, definition, overlay entry, and all four generated call sites use
  the human name. The full pipeline and diff checks succeeded; no game run or
  runtime behavior changed.
- The s2132 retail-oracle PCM/AI census passed its independent whole-RDRAM
  positive control (`33,346` writes), reached title VI `1024` and hangar VI
  `512 @ 0x006AB400`, and observed nonzero audio-buffer pointer-table state,
  `8,874` aligned countdown writes, `14,439` worker-flag writes, and `8,556`
  executions of retail `osAiSetNextBuffer` at `0x80029E80`. The gate watch
  recorded `17` writes with both zero and one values. This selects
  `H-RetailAIQueued` at the covered retail route and rejects
  `H-RetailAIBridgeNotUsed`; it does not prove the port's opt-in image arm
  produces valid PCM or authorize a host/task change. The initial unaligned
  countdown watch, the PIF/status-poll coverage-only retry, and the
  voice-base-watch coverage-only retry are not evidence against the result.
- The s2133 port-side same-build comparison passed positive LLE/audio controls
  and reached title VI `1024 @ 0x00790400` plus hangar VI `512 @ 0x006AB400`
  in both arms. The stub produced `2768` LLE tasks and no audio DMA rows; the
  image produced `1749` phase-10 image stage rows and two nonzero
  stage/source/consumer matches with `nz=621` and `639`, full-span FNV
  equality, and zero ordering violations. The image task still reported
  `break_pc=0x1328`, `exit=1`, `output_buff=0`, and `canary_ok=0`. The
  phase-gated consumer callback supplies nonzero PCM evidence, but the
  separately sampled `[pcm-sanity]` rows were all zero because its lifetime
  sampling missed the transient phase-10 rows. This selects
  `H-PortAIQueueMatches` at the sampled port boundary; it does not authorize
  changing `osAiGetStatus_recomp`, output routing, waits, guards, or the
  default audio arm. Both drivers later hit the existing terminal crash
  family after target coverage.
- The s2134 retail-oracle voice-codec census passed the independent whole-RDRAM
  positive control (`10,000` callbacks before watch removal), reached title VI
  `1024 @ 0x00790400` and hangar VI `512 @ 0x006AB400`, and observed all seven
  named voice decode/filter functions: `decodeAndFillVoiceBlock` (`0x8009C904`),
  `filterVoiceSampleBlock` (`0x8009D7D0`), `applyVoiceDelayFilter`
  (`0x8009D8C4`), `runVoiceLatticeFilter` (`0x8009D980`),
  `renderVoiceAudioBlock` (`0x8009DB44`), `audioMixStereoBlock8`
  (`0x8009DC98`), and `audioCompandS16` (`0x8009DD7C`). The same run also
  observed `musyxSynthFrame` (`0x8009123C`) and `osAiSetNextBuffer`
  (`0x80029E80`). This selects `H-RetailMORTDecoderLive` at the covered
  retail route and rejects `H-RetailVoicePipelineNoDecoder`; it does not yet
  identify the port RSP ROM segment, task ABI, or authorize a default-arm or
  runtime change.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not active
work items.

1. **Generated-symbol renaming sweep.** The M5 `data_ptr+0x100` boundary is
   closed at the sampled output edge: s2140's independently watched retail
   destinations agree with s2137's port `field348+0x100` relation. s2147
   selected `H-MissionMapping` for `func_800FEF10` /
   `stepObjectOrientationTowardTarget` and exhausted the mission-overlay
   human-versus-placeholder mismatches. The next lead is `func_800B2630` ->
   `buildFormatMessageGlyphBuffer`; validate it with a no-edit versus
   two-line symbol-file move and a fresh ELF/generated boundary and caller
   table. The s419 `m4_known_bad.txt` record is a live-crash warning, not a
   static-boundary skip.
2. **M5 drain in-loop tick A/B — parked.** The s2125 phase-repaired pump
   pair selected `H-PumpIrrelevant` only at route scope. s2126–s2128 all
   supplied positive controls but failed to put both drain arms in the target
   comparison; do not repeat the same recipe. Resume only with a genuinely
   new renderer-recovery or ground-truth discriminator.
3. **M3 crash work.** Only systematic idiom-class audits with a named
   discriminator. The dormant `slotDispatcherIter+872` class has 7659 clean
   hangar calls in its guarded run; no mitigation is authorized.
4. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
   because the oracle cannot screenshot the LLE path. Do not repeat the
   `0xD60` scan.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and independent-ground-truth requirements are
in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

Forced LLE is the route gate under the common wrapper. The accepted four-arm
table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title and hangar,
`01` reaches title only, and `10`/`00` reach neither. This is recipe-level
port evidence, not an explanation of the audio callback or PCM boundary.
Menu spin yield is a diagnostic route aid, not a default behavior change.

The route history is preserved in `PROJECT-OVERVIEW.md` §§36–41. s2093–s2096
closed the wrapper, task-thread, SP external-delivery, and guest-receive route
at the qualified recipe scope. The next route question is specifically the
B40 reader/branch after the selected pre-title split, not a reopening of the SP
queue result.

### M5 status and service

The generated tree reaches both target phases and the status census. Direct
service entry/exit and the service gate/loop are live. The port observes the
legitimate slot-0 sequence through the service store at `0x8009B7EC`, guest
address `0x80154620`, including `0x03 -> 0x00`. A later input-driven shutdown
call 3 exits after that store with status `0x00`; the earlier `0x02 -> 0x03`
spin is not a missing writer.

The retail oracle independently observes the same status-table cycle and the
`0x8009B7EC` writer. It does not execute the port crash labels
`0x8000B650`/`0x80095D54`; that is a PC-scope boundary, not permission to
change the port wait or guard behavior.

The s2122 port key-on census is now a normal-path contract at the sampled
hangar phase: the generated function enters, performs four valid `0xC0`
divides, and reaches its normal tail with no early-return guard hit. The
qualified slot transitions are legitimate `musyxRenderVoiceSamples` writes;
this result does not alter the audio stub or remove any defensive guard.

The s2123 retail census independently establishes that the completion-wait
contract is live on the qualified retail route: the countdown seed/decrement,
worker/status memory activity, and named wait/service/shutdown execution all
occur after the positive control and through the hangar phase. The port-side
pump-on/off comparison is still required; this result is not permission to
remove the current pump, wait timeout, or status guard.

The s2125 phase-repaired port pump pair supplies the missing target coverage
from s2124. Both arms reach the same title/hangar route and the same phase-12
wait/drain/second-spin sequence, while pump-stall and wait-for-slot guard
controls remain silent. The raw `musyxSynthFrame` countdown reads show
decrement activity in both arms but differ in total amount with route timing;
they are not treated as direct seed/exit proof. This closes the pump's sampled
route-admission question without changing the pump, wait, task ABI, or guards.

The s2128 fixed drain-tick pair is the third coverage-only result for A10.
The control enabled the gate and reached title/hangar; tick-off stopped at
the pre-target VI-640 renderer barrier. The initial pair was invalid because
the binary lacked the requested gate, so it was not used as evidence. The
legacy fixup gate is instrumentation around the existing host tick injection,
not a drain or game-value change. A10 is parked pending a new discriminator.

The s2132 retail oracle supplied the missing AI-ordering ground truth. After
the whole-RDRAM control, the route reached title and hangar, wrote both values
of the MusyX gate, seeded/decremented the aligned completion countdown, wrote
nonzero worker status, populated the 16-entry audio-buffer pointer table, and
executed retail `osAiSetNextBuffer` `8,556` times. This selects
`H-RetailAIQueued` for the covered retail route and rules out a retail-no-AI
explanation. It is one independent source; the subsequent s2133 port
comparison supplied the separate PCM source/consumer and host-callback line.
No AI-status shortcut, task ABI, or default-arm change follows.

The s2133 same-build port comparison supplied the missing nonzero host-boundary
line. Both arms reached the target phases with positive controls; the image
arm's phase-10 stage rows `nz=621` and `639` matched both source and consumer
spans by address, byte count, FNV, and nonzero count, with no ordering
violations. The stub arm remained zero. The `[pcm-sanity]` logger's lifetime
sampling missed the two transient nonzero callbacks, so its all-zero sampled
rows are a measurement-coverage limitation, not a silent-PCM result. The
image `break_pc=0x1328`, `exit=1`, canary failure, and `output_buff=0` remain
the task boundary; no host/task/default change is authorized. The s2135 static
census now identifies the existing RSP image and separate MORT speech asset;
s2136's retail task-field table selects `H-RetailTaskMatchesFactor5b` at the
covered task boundary. s2137's same-build port table then selects
`H-PortTaskFieldsMatchRetail`: both arms reached the target phases, the image
had the expected fixed fields and zero output buffer, its stage-3 destination
matched `field348+0x100`, and two nonzero stage/PCM joins matched by address,
length, FNV, and nonzero count. The s2140 retail oracle then passed its
whole-RDRAM and task-block controls, reached title/hangar, and wrote both
exact physical `data_ptr+0x100` destinations. This closes the sampled
retail/port output edge as `H-RetailDataPtrOffset100`; no task-field or
output-route change follows.

The s2134 retail oracle supplied the independent codec-side boundary. After
the whole-RDRAM control and title/hangar gates, all seven named voice
decode/filter functions executed, as did `musyxSynthFrame` and
`osAiSetNextBuffer`. This selects `H-RetailMORTDecoderLive` for the covered
retail route. The s2135 static census then identified the existing
`factor5b_rsp.toml` image/task boundary and the separate `speech` asset. It
does not prove that `factor5_ucode_b` is the MORT decoder or settle the
runtime meaning of every task field. The s2136 retail task-field census
selected `H-RetailTaskMatchesFactor5b`: the fixed image/data pair and
nonzero `data_ptr`/`data_size` co-occurred with zero output-buffer writes.
The s2137 port comparison established the matching fixed fields and sampled
`field348+0x100` relation. The s2138/s2139 reference tables now cover type-0
rows plus types `1,2,3,5` across 8000/16000 Hz with stable nonzero PCM. The
s2140 retail oracle then supplied the independent dynamic write line: both
observed `data_ptr+0x100` destinations were written after the positive
control and title/hangar gates. Together with s2137's port relation this
selects `H-RetailDataPtrOffset100` at the sampled boundary; no runtime or
default-arm change follows from the reference decode or this watch.

### M5 audio and guest gate

The stock `aspMain` contract is not the game's MusyX contract. The opt-in
Factor 5 image arm is isolated because its generated task function performs
real DMEM activity but does not yet satisfy the host task contract. The
phase-keyed source/consumer witness matches guest address, byte count, full
span hash, and nonzero-byte count at the sampled hangar stage.

The retail E50 envelope is written by named audio-region functions including
`acquireSampleStreamBlock`, `musyxSynthFrame`, and
`fillSampleStreamRange`. Retail exact-writer values are control,
metadata, or pointer-like values rather than the port's zero-only image
range. Retail display-gate writers are mixed; only named writer-specific
arms are authorized.

The generated image source/field audit maps `0x6F0..0x9F0` to transformed
`0x3F0`/`0x570` blocks and maps `0xCB0..0xE48` to a control/metadata block.
Their exact destinations come from task-local DMEM fields. Static code does
not prove the runtime ABI meaning of every field, and no output or task
contract change is authorized.

The s2115 image arm executed positive LLE/audio dispatch controls but died in
the pre-target `waitForAnyAudioSlot+1060` path; the stub arm reached both
target phases and produced the expected stub/PCM rows. The s2116 four-arm
contrast repaired target coverage for both image C88 values and C88=0 stub,
but not for C88=1 stub. Both image arms emitted target stage/contract rows;
the C88=0 pair was then compared against the matching stub control before
interpreting `output_buff=0`, canary failure, or task exit semantics.

The s2118 pair supplied the missing target coverage. The shared title phase
provided same-phase stub/image control rows, and the image hangar phase
supplied the nonzero stage-to-PCM join. The generated `break 0` edge at guest
PC `0x1328` therefore selects the task-exit mapping at this sampled boundary;
`output_buff=0` remains an ABI-semantics question and is not a routing fix.

The s2119 retail oracle supplied the independent gate line. Its whole-RDRAM
control fired, the run reached the hangar, and physical `0xA0F50` had both zero
and nonzero post-store values from multiple writer PCs. The s2120 paired port
arm then matched the named `0x8008EC88` writer to final gate 0 versus 1 and to
the C88=0-only nonzero stage/PCM result. Together these lines select
`H-C88-ReversedOrSuppressing` at the sampled route. No blanket gate flip or
task-contract change is authorized.

The s2110 route table was positive in both arms: B40 write/return and the first
two reapply pairs matched, while only B40=1 reached the later reapply entry in
that run. s2111's full-target paired run reached the same title/hangar route
in both arms. Its independent read census matched by guest PC, branch, value,
and route ordinal; host VI lines also matched phase order with a timing/origin
variation. The B40-dependent route-admission claim is superseded at the s2111
recipe scope; the remaining M5 question is the phase-7 state/origin producer,
not another B40 read-site census.
The s2112 caller/entry/route table matched at phase 7 in both arms, and both
arms later returned from `reapplyAudioConfig` with zero. The prior phase-7
origin split was not reproduced in this paired recipe; VI timing and later
phase count varied, selecting recipe variance at this scope without proving
the old divergence impossible in every recipe.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, dormant slot-dispatch census, and generated-symbol synchronization
sweep are closed at their stated scopes. s2130's static table confirmed the
`0x800AE3F0` mission mapping despite the old s407 runtime warning, s2131
confirmed the `0x800C41B0` mission mapping, s2141 confirmed the
`0x800BF790` mission mapping, s2142 confirmed the `0x800C64B0` mission
mapping, s2143 confirmed the `0x800E71D0` mission mapping, s2144
confirmed the `0x800EC110` mission mapping, s2145 confirmed the
`0x800EC6F0` mission mapping, s2146 confirmed the
`0x800ED150` mission mapping, and s2147 confirmed the
`0x800FEF10` mission mapping, each with unchanged
boundaries and callers. Those warnings remain reasons to validate future
relocations, not evidence of a static boundary conflict. M3 resumes only as an idiom-class audit or with a new
discriminator. M4 accumulator/beam evidence rules out the old shade-lane
theory but is not pixel ground truth. The remaining generated placeholders
are semantic holds or intentional non-sync entries.

## Superseded conclusions

Detailed history and exact reasons are in `PROJECT-OVERVIEW.md` §§26 and
35–40 and the ledger. The recent reversals that matter operationally are:

- “640 is a flaky crash,” missing-input, missing-wait-return, and unqualified
  PCM-null claims were believable because the relevant rows were absent.
  Same-run controls and the accepted LLE/spin recipe later reached both
  target phases.
- The old title/hangar callback split and global zero-payload image-DMA claim
  were believable because joins lacked guest address/full-span identity or
  had not sampled a nonzero hangar task. The corrected stage/PCM table and
  s2100 hangar sample supersede them at their earlier broad scopes.
- The old clean-stub, canary-poison, final-E50, and uniform-gate explanations
  were believable because the first image and retail runs lacked a complete
  task/consumer or writer-specific table. Those controls now show real image
  DMEM activity, a mixed retail gate, and a sampled nonzero hangar join, but
  they do not authorize a runtime change.
- The old retail voice-field interpretation was believable because a pointer
  entry was treated as a physical array base. Generated source and retail
  root observations show separate voice-array and command-list structures.
- The old “B40 was unreached” interpretation was believable because a shared
  logger saturated on raw-gate rows. The independent B40 witness fires in
  both arms; the remaining issue is route admission.
- The s2108 “no B40 downstream hypothesis is selected” conclusion and s2110's
  `H-B40-RouteRequired` result were believable because those reduced pairs
  lacked a control target-phase route. s2111's same-build pair reached title
  and hangar in both arms, and its complete generated read/branch table was
  identical with B40 values already 0 after reapply. Those earlier claims are
  superseded at the s2111 recipe scope; they remain historical results for
  their unqualified earlier scopes.
- The s2111 phase-7 origin difference was believable as a state-producer issue
  because the two arms had different host route origins. s2112's complete
  phase-7 rows matched, both arms reached title and hangar, and independent VI
  traces differed only in timing. This supersedes the producer selection at
  the s2112 paired-recipe scope, not as a universal claim about all recipes.
- The s2117 “no contract hypothesis selected” result was believable because
  its image arm stopped in the pre-target 640 phase and emitted no target
  rows. s2118 reached the shared title control and the image hangar rows,
  supplying the missing coverage and superseding that result at the current
  recipe scope.
- `0x8000B650` is a shared last-guest-PC breadcrumb, not evidence that retail
  executes the port's fill/wait function. The generated crosswalk and
  independent retail PC watch establish that scope only.
- The first s2128 drain pair's apparent no-split result was believable because
  the run recipe named an environment gate absent from the binary. Binary
  strings and generated-source inspection caught that stale-build condition;
  the regenerated fixed pair, not the first pair, is the evidence recorded
  above.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is in §36; the M5 archive through s2047 is in §§37–38; the
late route/fill boundary is in §39; the s2080–s2108 archive is in §40; and the
s2110–s2112 route/read/state results remain in the ledger and current front
matter.
The exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`. The current selected hypotheses are scoped above and
must not be widened from single-source or single-arm observations. s2115's
paired coverage result added no ABI selection; s2116's four-arm table added
coverage selection only; s2118 closed the sampled C88=0 contract boundary;
s2119 supplied retail mixed-writer evidence; s2120's paired port arm selected
the causal writer and reversed/suppressing gate polarity at the sampled
route; s2121 supplied single-source retail zero-hit evidence for the eight-site
key-on class; and s2122 supplied the independent port normal-path line without
changing any guard. s2123 supplied the independent retail completion-wait
line; s2124 supplied the first port pump A/B but failed target coverage, and
s2125 supplied the phase-repaired target comparison that selected
`H-PumpIrrelevant` at route scope. The pump, wait, task ABI, and guards remain
unchanged; s2127 and s2128 added coverage-only drain-tick pairs, with s2128's
repaired control reaching the target route while tick-off died in RT64 before
it. s2129 then selected the mission-overlay mapping for
`computeTrackedObjectWorldAnchor` with unchanged generated boundaries. s2130
selected the static mission mapping for
`func_800AE3F0`/`initPlayerCraftTrailBuffers`, with its prior relocation
warning retained as an explicit runtime-risk record. s2131 selected the
static mission mapping for `func_800C41B0`/`plotRadarBlipColumn`, with the
same start, size, end boundary, and caller table in the final ELF/generated
tree. s2132 supplied a retail-only PCM/AI ordering table: whole-RDRAM control,
title/hangar VI coverage, nonzero pointer-table state, aligned countdown and
worker writes, and `8,556` retail `osAiSetNextBuffer` executions co-occurred.
This selects `H-RetailAIQueued` at the covered retail route; it is not port
PCM or task-ABI evidence. s2133 supplied the port-side same-build comparison:
both arms reached title/hangar, and the image arm's two phase-10 nonzero
stage/source/consumer joins matched by address, byte count, FNV, and nonzero
count while the stub remained zero. This selects `H-PortAIQueueMatches` at
the sampled callback boundary; the task exit/output fields remain unchanged.
The s2134 retail oracle then supplied the independent voice-codec line:
whole-RDRAM control and title/hangar gates passed, all seven named decoder/
filter PCs executed, and `musyxSynthFrame` plus `osAiSetNextBuffer` executed
in the same run. This selects `H-RetailMORTDecoderLive` at the covered retail
route. The s2135 static source/data census selected
`H-ExistingFactor5ConfigMatches`: the existing `aspMainText`/`aspMainData`
pair is the retail audio RSP image, and MORT samples are a separate speech
asset consumed by CPU voice routines. The s2136 retail task-field census
selected `H-RetailTaskMatchesFactor5b`: the fixed image/data pair and
nonzero `data_ptr`/`data_size` co-occurred with zero output-buffer writes.
s2137's same-build port table then selected `H-PortTaskFieldsMatchRetail`:
both arms reached the target phases, the image had the expected fixed fields
and zero output buffer, its stage-3 destination matched `field348+0x100`, and
two nonzero stage/PCM joins matched by address, length, FNV, and nonzero count.
s2140's retail oracle then passed whole-RDRAM/task-block controls, reached
title/hangar, and wrote both exact `data_ptr+0x100` destinations, selecting
`H-RetailDataPtrOffset100` with the independent port relation. s2138's
independent decoder table produced four complete 8000-Hz/type-0 rows, and
s2139's table produced complete nonzero rows for types `1,2,3,5` at both rates
with byte-count and waveform checks. This single-source reference evidence
selects `H-MORTReferenceMatchesExtended` for those sampled classes. s2141
then selected the static mission mapping for
`func_800BF790`/`updateHudHealthIndicator`, with the same start, size, end
boundary, and caller table in the final ELF/generated tree. s2142 selected
the static mission mapping for
`func_800C64B0`/`initHangarDisplayItemTimers`, with the same start, size,
end boundary, and caller table in the final ELF/generated tree. s2143
selected the static mission mapping for
`func_800E71D0`/`transformCraftAnchorsApplySubFx3`, with the same start,
size `0x1C0`, end boundary `0x800E7390`, and caller table in the final
ELF/generated tree. s2144 selected the static mission mapping for
`func_800EC110`/`allocObjectPoolNode`, with the same start, size `0x278`,
end boundary `0x800EC388`, and caller table in the final ELF/generated
tree. s2145 selected the static mission mapping for
`func_800EC6F0`/`tickCraftMountedAnimationEffect`, with the same start,
size `0x538`, end boundary `0x800ECC28`, and caller table in the final
ELF/generated tree. s2146 selected the static mission mapping for
`func_800ED150`/`claimSongSlotForCurrentHandle`, with the same start,
size `0xB0`, end boundary `0x800ED200`, and caller table in the final
ELF/generated tree. s2147 selected the static mission mapping for
`func_800FEF10`/`stepObjectOrientationTowardTarget`, with the same start,
size `0xEF0`, end boundary `0x800FFE00`, and both callers in the final
ELF/generated tree. Mission-overlay human-versus-placeholder mismatches
are exhausted; the next work unit is the first remaining menu-overlay
instance of the same two-line pattern. No runtime or default-arm change
follows.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; use physical-address watches and
  phase-gated VI callbacks.
- A null is worthless without a same-run positive control. Batch all desired
  counters and every A/B arm in one build/run. Scope counters and log budgets
  to the relevant phase.
- Read `F5-UCODE-REFERENCE.md` before interpreting a Factor 5 display list.
  Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Do not run `git submodule update`, `git checkout -- lib/...`, `git clean`,
  or `git reset --hard`. If `lib/` changes, export submodule patches in the
  same iteration.
- A mitigation is not an explanation. Name the writer, state legitimacy,
  and add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a whole discriminating table and an
  outcome that selects among hypotheses. A repeated join key or counter is
  not a work unit.
