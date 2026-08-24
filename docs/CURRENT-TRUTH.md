# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the append-only
ledger remains authoritative for exact commands, counts, and probe rows.
Maintained in Session 2262 (2026-08-24); behavioral and source evidence is
current through s2262, with the M5 plan refresh recorded in s2231. The
s2198–s2226 archive is §44; s2227–s2262 remain in
the append-only ledger.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio is still defaulted to the silent `M_AUDTASK` `Broke` stub. The
  Factor 5 image arm is opt-in through `ROGUESQ_AUDIO_UCODE=1`; C88=`1` is
  also a diagnostic behavior arm. Stock `aspMain` is not the game's MusyX/
  Factor 5 contract, and MORT is a separate CPU speech asset.
- `docs/M5-AUDIO-PLAN.md` was refreshed in s2231. It inventories 20 active
  audio stubs/traps/gates/hatches, separates Factor 5 RSP audio from CPU-side
  MORT, and defines the phase-keyed task→DMA→service→slot→voice→PCM
  discriminator and rollback conditions. This refresh changed no runtime
  behavior or default.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. Its host canary is inside the generated mix-buffer span;
  `canary_ok=0` is probe data and does not gate completion, writeback, or DMA.
- s2253 failed the image arm before title while the silent arm qualified;
  s2254 reversed launch order and qualified both arms through hangar, with
  image joins still stage-only. Together they established route intermittency
  and left the image output edge open; later captures supersede their detailed
  route outcomes. The image arm remains opt-in and no default or guard change
  follows.
- s2255 repeated the silent-first/image-second pair with the same phase-keyed
  output traces. Both arms passed startup, one `[missing-func]`, and the 640
  origin, but neither reached title `1024` or hangar `512`: the silent arm
  died with SIGSEGV at guest PC `0x8000B650`, and the image arm died with
  SIGBUS at guest PC `0x8000834C`. There were no target-phase output rows.
  The distinct pre-target crashes select H-RouteInvalidAgain for this capture,
  not an image-output hypothesis; s2254's qualifying capture remains valid and
  shows the route failure is intermittent at this scope.
- s2256 duplicated the silent+C88=`0` control under the same full trace load.
  Arm A passed startup, one `[missing-func]`, 640, title `1024`, and hangar
  `512` twice before the known `updateHangarBayScene+76432` crash at guest PC
  `0x800AC8C0`; arm B passed startup, one `[missing-func]`, both 640 origins,
  and the B40/route-state controls but remained at 640 until the driver's
  600-second timeout/SIGKILL. This is single-source port evidence selecting
  H-IdenticalArmNondeterminism for this capture. It rules out a deterministic
  common silent-route failure under these controls, but does not qualify an
  image/output comparison. The next route discriminator pairs a fully traced
  silent arm with a route-only silent arm in the same run.
- s2257 paired those identical silent arms with different trace loads. Both
  passed startup, one `[missing-func]`, the 640 origins, and B40/route-state
  controls. The fully traced arm crashed before title at host
  `MetalFramebuffer` construction with last guest PC `0x8000B650`; the
  route-only arm reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` twice before the known post-hangar PI-ROM abort at guest
  PC `0x80001B08`. This same-run port table selects H-TraceLoad at route
  scope and supersedes H-IdenticalArmNondeterminism as the only explanation
  for that capture, but is single-source evidence and does not establish
  trace load as the sole cause or qualify image output. The next pair uses
  reduced tracing for image-versus-silent attribution.
- s2258 ran that reduced-trace image+C88=`0` / silent+C88=`0` pair. Both arms
  passed startup, one `[missing-func]`, the 640 origins, and B40/route-state
  controls, but neither reached title `1024` or hangar `512`. Both returned
  `4` after SIGBUS at `cutsceneDispatchSlotsByFlag+10804` with last guest PC
  `0x8000834C`; neither produced target image-stage rows. This selects
  H-ReducedRouteInstability at reduced-load scope, does not supersede s2257's
  trace-load result, and supplies no image/output attribution or runtime
  default change. It is single-source port evidence.
- s2259 ran the prescribed single reduced-trace silent+C88=`0` control with
  the same spin/LLE route. It passed startup, one `[missing-func]`, three 640
  route entries, title `1024 @ 0x00790400`, and two hangar
  `512 @ 0x006AB400` transitions; target B40 and route-state rows fired.
  The driver then stopped at the known aligned-ROM `do_rom_read` abort with
  last guest PC `0x80001B08`. This selects H-ConcurrentLoad at the
  single-arm route discriminator and restores a qualified control for a new
  paired output capture, but does not prove two-process load is the sole
  cause or attribute image output. It is single-source port evidence; no
  runtime behavior or default changed.
- s2260's first same-build image/silent pair reproduced the target route in
  both arms, but omitted `ROGUESQ_LOG_AUDIO_RETURN=1`; the audio route
  identity was therefore disabled and its zero stage-row result is
  measurement-invalid for output attribution. The fixed repeat added only
  that route-identity gate and kept task-contract/ABI/DMA/PCM tracing off.
  Both arms passed startup, one `[missing-func]`, title
  `1024 @ 0x00790400`, and two hangar `512 @ 0x006AB400` transitions. The
  image arm produced 3,448 title stage rows and 2,201 first-hangar stage
  rows; all were stage-only, with zero nonzero title rows and two nonzero
  hangar rows (`dest=0x168E50`/`0x169150`, `len=0x300`,
  `fnv=0x60F910DE`/`0x7B70923A`, `nz=621`/`639`). The silent arm produced
  zero target stage rows. The image arm ended at the known aligned-ROM
  abort and the silent arm at the known post-hangar
  `updateHangarBayScene+76432` crash, both after target qualification. This
  selects H-ImageStageIngressPresent at stage-presence scope, single-source
  port evidence; source/consumer attribution remains open. No runtime or
  default changed.
- s2261 repeated the image-first same-build C88=`0` pair with both route and
  PCM-boundary logging. The image arm qualified title and hangar, with phase
  8/10/12 stage rows `3222/1790/815`; phase 10 had two nonzero rows and one
  `dest=0x168B50`, `len=0x300`, `fnv=0x6ADD4218`, `nz=639` row that reached
  `stage-consumer-match` with equal source/consumer payloads and valid order.
  The silent arm passed startup, `[missing-func]`, and first 640, then died
  before title at `copyToRAM`/guest `0x8000B650` with no target rows. The A/B
  table selects H-PairRouteInvalid, while the image arm has a qualified
  single-arm phase-10 join. The preceding retail oracle passed whole-RDRAM,
  reached hangar, and recorded 12,288 exact PCM-ring and 705,759 task-span
  writes. No runtime or default change follows.
- s2262 ran the prescribed single reduced-trace silent+C88=`0` control with
  the same route and PCM logger. It passed startup, one `[missing-func]`, the
  two observed 640 transitions, title `1024 @ 0x00790400`, and hangar
  `512 @ 0x006AB400` twice before the known post-target aligned-ROM abort
  (`last-guest-pc=0x80001B08`). Source and consumer boundary rows both fired:
  phase 8 had 53/53 rows, phase 10 had 48/48, and phase 12 had 6/6; every
  payload was `fnv=0xF59C39C5`, `nz=0`. This selects H-SilentPcmAbsent at the
  measured boundary and qualifies the silent route for a paired output run;
  it remains single-source port evidence and changes no runtime behavior or
  default.
- s2246's two full field348-candidate captures both passed the 640 route and
  one `[missing-func]` control but crashed before title `1024` or hangar `512`:
  the first was `fillSampleStreamRange+8136` with last guest PC
  `0x800547BC`, and the retry was the same function with `0x8000B650`. A
  same-image arm with M5 census logging removed also passed 640 but crashed
  in `RT64::NativeTarget::copyToRAM` with last guest PC `0x8000B650`. These
  route-invalid captures select pre-phase nondeterminism as a measurement
  blocker only; they select no field348 writer hypothesis and change no
  runtime behavior or default.
- s2247's full five-store census and its fixed low-logging image control both
  passed the 640 route and one `[missing-func]` control, then crashed before
  title `1024` or hangar `512`. The census arm died in
  `fillSampleStreamRange+6736` with last guest PC `0x8000834C`; the control
  died in `RT64::NativeTarget::copyToRAM` with last guest PC `0x80001F88`.
  Both had zero target-phase field348/stage/DMA rows. The divergent crash
  sites do not support a census-logging-only explanation and select only a
  route-stability blocker; no field348 writer hypothesis or runtime default
  follows.
- s2248's same-build image/stub route comparison passed the common startup,
  640 origin `0x00696100`, and one `[missing-func]` control in both arms. The
  image arm again died before title in `fillSampleStreamRange+8136` with last
  guest PC `0x8000B650` and zero target rows; the silent stub reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400` before the known
  post-hangar aligned-ROM abort. This selects H-ImageArmSpecific at route
  scope and rejects shared pre-phase nondeterminism as the sole explanation,
  but it does not identify a field348 writer or output edge.
- s2249's same-build three-arm split passed the common startup, 640 origin,
  and `[missing-func]` control in image+C88=`1`, image+C88=`0`, and stub+C88=`1`.
  The image+C88=`1` arm died before title with last guest PC `0x8000B650`;
  image+C88=`0` and the stub reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`. The qualified image arm's title summary had 3,457
  stage rows and zero nonzero rows; its hangar phase-10 summary had 2,032
  stage rows, two nonzero rows, and one stage/source/consumer match at
  `dest=0x167F50`, `len=0x300`, hash `0x60F910DE`, 621 nonzero bytes. This
  selects H-C88ImageInteraction at route scope and H-ImageQualifies only for
  C88=`0`; the join is single-source port evidence and does not authorize a
  default flip or writeback guard.
- s2250's route audit adds the next boundary. Both image arms reached the
  title and hangar in one same-build run, with identical target route-state
  rows. The only C88-keyed route differences were the intentional B40 store
  at `0x8008EC88` and the resulting B40 read values; the C88=`1` arm did not
  fail at the logged route boundary. The silent control still died pre-title,
  so it does not distinguish image-arm task/output behavior. The open
  question is now the first phase-keyed divergence in task contract,
  image-stage/DMA payload, or PCM source/consumer rows after the route
  boundary.
- s2250's same-build three-arm route audit passed the common 640 origin and
  `[missing-func]` control in all arms. Both image arms reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`; the silent arm crashed
  before title in `fillSampleStreamRange+8136` at guest PC `0x8000B650`.
  The normalized target-phase route-state rows were identical between the
  image arms. Their first keyed difference was the deliberate
  `reapply-success` B40 store at `pc=0x8008EC88`: C88=`1` stored `0x01` and
  C88=`0` stored `0x00`; target B40 reads reflected that byte, but neither
  route diverged. The image arms later ended in different post-hangar crash
  windows (`updateHangarBayScene+76432`/`0x800AC8C0` and the known
  `do_rom_read`/`0x80001B08`). This is single-source port evidence that
  closes the unexplained route-edge hypothesis at this scope; it does not
  explain the earlier intermittent C88 split or identify the later task/output
  edge.
- s2251's prescribed concurrent image+C88=`1`/image+C88=`0` audit was
  route-invalid in both arms: each passed startup, one `[missing-func]`, and
  the 640 origin, then died before title. C88=`1` bus-aborted in
  `cutsceneDispatchSlotsByFlag` with guest breadcrumb `0x8000834C`; C88=`0`
  hit RT64 `findTileCopyId`'s `height > 0` assertion with the same breadcrumb.
  The fixed retry with high-volume thread-resume logging disabled again lost
  C88=`1` in `fillSampleStreamRange+8320` / guest `0x8000B650`, while C88=`0`
  reached title and hangar and recorded 3,715 task joins, 67 host-boundary
  rows, and 3,522 PCM rows at title. These are route-stability observations,
  not a valid two-arm post-route comparison; no task, image-payload, or PCM
  hypothesis is selected and no default or runtime behavior changes.
- s2252's prescribed reversed-order concurrent image+C88=`0`/image+C88=`1`
  audit passed startup, one `[missing-func]`, and the 640 origin in both
  arms, but neither reached title `1024` or hangar `512`. The first-launched
  C88=`0` arm crashed in `slotDispatcherIter+3508` with last guest PC
  `0x80007904`; the second-launched C88=`1` arm crashed in
  `fillSampleStreamRange+8136` with last guest PC `0x8000B650`. The differing
  pre-target crashes select only a route-stability blocker at this scope:
  launch-order reversal did not qualify either arm, so it selects no C88,
  task-contract, image-payload, or PCM-consumer hypothesis and supplies no
  target-phase rows.
- s2233's fixed retail-oracle capture passed the whole-RDRAM positive control,
  reached the 640 target, title `1024`, and hangar `512`, and recorded
  `6,665,015` writes to physical `0x166000:0x17A000`. It sampled 503
  post-store words, 64 unique values, and a nonzero final span. The 640-only
  phase buckets had 202 rows at `0x00696100` and 213 at `0x00696600`; title
  and hangar writer rows remained lifetime-aggregate because the oracle's
  phase histogram is width-640-only. Retail therefore writes the broad port
  span, but this run does not join those writes to the port's image-stage/PCM
  events. H-NoTargetRoute is refuted; H-RetailImageWritesSame versus
  H-RetailUsesOtherOutput remains open, and no output edge or default change
  follows.
- s2234's narrower retail-oracle capture again passed the whole-RDRAM control,
  reached both 640 target origins, title `1024 @ 0x00790400`, and hangar
  `512 @ 0x006AB400`. The exact PCM ring `0x166450:0x169450` had `12,288`
  writes and a nonzero final snapshot (`12025` nonzero bytes), but zero
  post-target samples. The task-output span `0x171F70:0x173DB4` had `303`
  post-target samples, `62` values, and target-phase rows from the selected
  `0x80091078`/`0x800910EC`/`0x800910F8`/`0x8009114C`/`0x80091168`/
  `0x80091170`/`0x80091204` writer set. This selects H-RetailTaskOutput and
  rejects a target-phase direct-PCM write at this scope; it is single-source
  retail evidence and still needs a port-side image-stage join.
- s2235's first port image-arm capture crashed in `fillSampleStreamRange+932`
  before the 1024 phase. A fresh retry reached title `1024 @ 0x00790400`
  and hangar `512 @ 0x006AB400`, with 2,753 ABI rows, 2,753 DMA rows, and
  6,057 image-stage rows. Every ABI/DMA row changed DMEM and broke at
  `0x1328`; both target summaries had zero nonzero stage rows, zero exact
  source/consumer joins, and zero stage-destination overlap with retail's
  `0x171F70:0x173DB4` task-output span. Sampled PCM source/consumer controls
  were nonzero at title, but no image ordinal/hash joined them. This selects
  H-PortContractGap at the measured scope; the image arm remains opt-in.
- s2236's batched image-ingress audit reached both target phases with 3,531
  ABI rows, all with nonzero DMEM changes and `break_pc=0x1328`, 3,531 DMA
  rows, 12,505 target-stage rows, and 204 PCM-boundary controls. The two
  observed `field348` source addresses (`0x80178C80` and `0x801797B0`) were
  valid but their masked `0x180`-byte RDRAM spans were all zero
  (`field348_fnv=25E26BC5`, `field348_nz=0`); stage-0/1 DMEM and stage-2/3
  generated DMA payloads were also all zero. This selects H-ImageInputZero at
  the measured port boundary, single-source evidence; no runtime default or
  contract behavior changes.
- s2237's retail-oracle writer audit passed the whole-RDRAM positive control
  (`10000` callbacks), reached title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`, and showed writes to both exact source spans: `13,824`
  writes at `0x178C80:0x178E00` and `1,058` at `0x1797B0:0x179930`.
  Post-store samples were nonzero in both spans, with snapshots of 71 and 82
  nonzero bytes (`fnv=0x56048946` and `0xBD529643`) and writer-PC
  histograms. This selects H-RetailField348Writer over the no-writer and
  one-origin hypotheses at this scope; it is independent retail evidence and
  does not yet identify the port-side writer or ordering edge.
- s2238's qualified image-arm port capture reached title `1024 @
  0x00790400` and hangar `512 @ 0x006AB400` before the known post-hangar
  crash window. The same run had 3,308 ABI rows, 3,308 DMA rows, 13,677
  image-stage rows, 105 source and 105 consumer PCM controls, and two
  non-target writer-hook controls at `0x1496F4`. At active title source
  `field348=0x80178C80`, 384 byte stores from `rs_memset` PC `0x800078EC`
  wrote zero. At the later active source `field348=0x801797B0`, 512 bounded
  exact-span rows across phases 10/12 were also zero stores from that writer.
  All target-stage rows had zero field348, DMEM, and generated-DMA payload
  summaries. Nonzero phase-12 stores to the other span were not the active
  field348 source. This selects H-PortWriterPayloadZero at the exact active
  source scope, with origin-keyed behavior retained; H-PortNoField348Writer,
  H-PortWriterThenZero, and H-PortWriterInstrumentGap are not selected.
- s2239's phase-gated `rs_memset` entry attestation passed two explicit
  outside-span controls and reached title and hangar. The title source
  `0x178C80` and hangar source `0x1797B0` each received one zero-fill
  `len=0x298` clear before the first image-stage row using that same source;
  no second overlapping bulk clear was observed. The earlier hangar stage
  row used the previous origin's span, so it is not a same-source
  post-producer clear. This selects H-ExpectedField348Init at the matched
  source/order scope and keeps the analysis origin-keyed. Generated direct
  calls expose `$ra=0` and stale `guest_pc=0x80001C94`, so the caller identity
  split remains unevaluable until callsites are annotated.
- s2240 annotated all 88 generated direct `rs_memset` calls across 25 files;
  the fixup refused partial coverage and the Debug build passed. Its qualified
  retry reached title and hangar with 1,024 bounded memset rows, 17,095 image
  stages, 3,844 image DMA rows, and 105 source/105 consumer PCM controls. Both
  active source spans were cleared once, with fill `0` and length `0x298`, by
  static callsite `0x8008F2CC` before the first matching stage; the two
  outside-span controls fired from `0x800052C4`. All target rows carried a
  nonzero static callsite, so H-CallsiteInstrumentGap is refuted. The existing
  scalar writer rows still show only zero stores from `rs_memset` before the
  image stage. This selects H-InitCallsite plus H-MissedProducer at the
  measured source/order scope: the clear is a stable setup operation, while
  the expected nonzero producer edge is still absent. The first s2240 attempt
  died before the phase gate in the known intermittent
  `fillSampleStreamRange+8136` window and is not evidence. The retry later hit
  the known post-hangar PI-alignment abort; no runtime behavior or default
  changed.
- s2241's retail oracle passed the whole-RDRAM positive control, reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, wrote both exact source
  spans, and executed the known producer range. The incremental fixup
  enumerated and annotated all 5 scalar stores in `0x80090F8C`–`0x80091000`,
  and the Debug build passed. Two unchanged qualified port attempts died
  before the 1024 phase (one missing-function/abort run at 640, one
  `fillSampleStreamRange+932` bus error), so they produced zero target
  candidate, stage, DMA, or PCM rows. The port writer hypotheses remain
  unevaluable; no writer, guard, or default conclusion follows.
- s2242's planned field348 producer census was attempted twice with the
  unchanged image arm and full instrumentation. Both runs reached only the
  640 route at `0x00696100`, emitted one missing-function stub, and crashed
  before the 1024 phase at `fillSampleStreamRange+8136` with
  `last-guest-pc=0x8000b650`. Both therefore had zero target candidate,
  image-stage, DMA, and PCM rows. These are invalid captures for all four
  field348 writer hypotheses; the next unit must first discriminate whether
  the logging load amplifies this pre-phase image-arm crash. No runtime
  behavior or default changed.
- s2243's same-build concurrent A/B kept the qualified image arm and common
  startup/640 route controls, but neither arm reached 1024. The full-M5-log
  arm crashed in RT64 `findTileCopyId` with `last-guest-pc=0x8000834c`, while
  the no-M5-log arm crashed in `fillSampleStreamRange+8136` with
  `last-guest-pc=0x8000b650`. The divergent pre-phase PCs select
  H-RunNondeterminism at this scope: the result does not support a clean
  logging-only split or same-PC intrinsic-crash claim, and supplies no
  field348 writer evidence. No runtime behavior or default changed.
- s2244's same-build concurrent no-M5-log A/B passed the common startup/640
  controls and each emitted one missing-function marker. Arm A crashed before
  1024 in `fillSampleStreamRange+8136` with `last-guest-pc=0x8000b650`; arm B
  reached title `1024 @ 0x00790400` and was SIGKILLed before the driver could
  reach hangar. The divergent no-log outcomes select
  H-BaselineNondeterminism at this scope and provide no field348 writer
  evidence; driver completion is not a comparison because arm B was
  terminated after title qualification. No runtime behavior or default
  changed.
- s2245 repeated the same-build no-log A/B and both arms passed startup, the
  640 route, title `1024 @ 0x00790400`, and hangar `512 @ 0x006AB400` twice.
  Each then hit the same known aligned-ROM assertion in `recomp::do_rom_read`
  with `last-guest-pc=0x80001b08`. This selects H-NoLogTargetQualification
  and removes the route-qualification blocker for the five-store field348
  producer census; the post-hangar PI-DMA abort remains a separate open
  defect. No runtime behavior or default changed.
- s2232's same-build port A/B reached the target route, title, and hangar in
  both arms. The stub produced 3,366 ABI rows with zero DMEM changes, zero
  DMA rows, and `break_pc=0`; the image produced 3,302 ABI rows, all with
  DMEM changes, 3,302 nonzero-DMA rows, and `break_pc=0x1328`, plus SP
  completion. The image summary still had zero stage/source or stage/consumer
  matches: title had 3,582 stage rows and 13 consumer-only observations; the
  19 nonzero PCM source rows and 19 nonzero consumer rows were not joined to
  an image stage. This is a provisional, single-source port selection of
  H-ContractGap, not proof that the image output is correct.
- s2220 matched the retail payload/polarity of `reapplyDisplayMode` at
  `0x8008EC88`: C88=`1` reaches service, slot completion, and nonzero PCM
  controls; forced zero does not. Keep this opt-in pending the remaining M5
  contract work.
- Retail key-on ground truth reaches the boundary and hangar, skips the eight
  watched divide PCs, and executes the alternate post-guard transfer path.
  The phase-keyed `$v0/$s1/$a0/$a2` tuple sets differ across both target
  origins and hangar. The port has positive normal-tail/slot behavior at four
  sites. s2229's 8192 detail arm reached first-target, title, and hangar with
  zero tuple overflow at every site.
  s2230's exact common-bucket comparison found both port-only and retail-only
  tuple values at all eight transfer PCs in both `640 @ 0x00696100` and
  `512 @ 0x006AB400`; both phase rows and all controls were present, so this is
  a bidirectional operand-set mismatch, not a join/coverage null. No key-on
  behavior change follows.
- The port's `ViState::field` is fixed at zero by default. Opt-in field,
  current-register, timing, and total-`VI` arms recover the two-origin target
  split, but the natural host publisher/cadence is unidentified. No such
  knob is default-on.

## Active backlog

Closed investigations are not active work items. The sequence is monotonic.

1. **M5 image-output contract attribution.** s2232 selected H-ContractGap at
  single-source port A/B scope, and s2234 independently selected
  H-RetailTaskOutput at the exact retail watch boundary. s2235's successful
  retry selected H-PortContractGap, and s2236 selected H-ImageInputZero: the
  image arm changed DMEM and completed, but the valid `field348` source span,
  stage-0/1 DMEM inputs, and stage-2/3 generated DMA payloads were all zero.
  s2237 independently selected H-RetailField348Writer; s2238–s2240
  established the legitimate port init clear and the missing nonzero
  producer boundary. s2245 qualified both no-log arms through title and
  hangar, s2248 selected an image-arm-specific pre-title failure, and s2249
  selected H-C88ImageInteraction: image+C88=`1` failed before title, while
  image+C88=`0` and stub+C88=`1` reached both targets. The C88=`0` image arm
  also supplied a hangar-only nonzero stage/source/consumer join, but title
  remained all-zero and the join is single-source. s2250 found only the
  expected forced B40 byte difference and identical target route-state rows.
  s2251 did not qualify that comparison: both original arms died before
  title, and a reduced-logging retry qualified only C88=`0`. s2252 reversed
  the launch order, but both image arms again died before title with distinct
  pre-target crash identities. s2253 paired image+C88=`0` with a silent
  C88=`0` control: the silent arm qualified title/hangar, while the image arm
  again failed before stable title, with all target image joins still
  `stage-only` and zero payload summaries. s2254 reversed that image/stub
  launch order and both arms qualified through title and hangar, so the blocker
  is intermittent at this scope rather than a selected intrinsic image-arm
  failure. s2255 then failed both arms before title with distinct pre-target
  crash identities and no target rows. s2256's identical silent/silent pair
  split: arm A reached title and hangar, while arm B timed out at 640 after
  the same early controls. This selects H-IdenticalArmNondeterminism for the
  capture but does not qualify the image/output table. s2257 paired a fully
  traced silent arm with a route-only silent arm: both passed the same
  startup/640/B40 controls, but only the route-only arm reached title and
  hangar. This selects H-TraceLoad at route scope for that same-run capture,
  supersedes the identical-arm hypothesis as its only explanation, and is
  single-source port evidence. Reduce trace load before returning to the
  image/output table. s2258 then ran the reduced image/silent pair and both
  arms failed at the same pre-title `cutsceneDispatchSlotsByFlag+10804` SIGBUS
  after the controls, so reduced tracing alone did not qualify the output
  table. s2259 qualified the single reduced silent control through title and
  two hangar transitions, separating pair-load instability from an intrinsic
  single-arm reduced-route failure. s2260's first pair omitted the
  `ROGUESQ_LOG_AUDIO_RETURN=1` route-identity gate, so its zero stage rows are
  measurement-invalid. The fixed pair added only that gate: both arms
  qualified title and two hangar transitions; the image arm emitted 3,448
  title and 2,201 first-hangar stage rows, all stage-only, with two nonzero
  hangar rows, while the silent arm emitted none. This selects
  H-ImageStageIngressPresent at stage-presence scope, single-source port
  evidence, and leaves source/consumer attribution open. s2261's image arm
  then produced one exact phase-10 stage/source/consumer match, but its
  same-run silent control failed before title, so the A/B result is
  H-PairRouteInvalid rather than a complete image-versus-silent selection.
  s2262 qualified that silent control: phase-8/10/12 source and consumer rows
  were present but all-zero, so the silent boundary is a valid route control
  rather than a route null. The next discriminator is a same-build
  image+C88=`0` / silent+C88=`0` pair with silent launched first, using only
  the route identity, B40/route-state, and PCM-boundary logs. Do not promote
  `ROGUESQ_AUDIO_UCODE=1` or add a writeback/consumer guard.
2. **M5 key-on tuple contract.** s2230's valid common-bucket table rejects
   exact tuple parity in both directions: port-only and retail-only sets occur
   at every transfer PC in both buckets. The next useful question is whether
   pointer/dynamic operands or a true branch contract accounts for the two-way
   difference; no key-on return, guard, task-field rewrite, default flip, or
   mitigation follows automatically.
3. **M5 A1: identify the missing second-origin transition.** Retail's
  `__osViNext` context uses `framep` plus the selected current field to make
  both target origins. The port has the candidates but its natural field
  publisher is still unknown; all recovery knobs remain diagnostic-only.
4. **M5 drain in-loop tick A/B; parked.** s2125 selected `H-PumpIrrelevant`
  only at route scope, while s2126–s2128 failed to place both drain arms in
  the target comparison. Resume only with a new renderer-recovery or
  ground-truth discriminator.
5. **M3 crash work.** Resume only as a systematic idiom-class audit with a
  named discriminator. The dormant `slotDispatcherIter+872` class has 7,659
  clean hangar calls in its guarded run; no mitigation is authorized.
6. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
  attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
  because the oracle cannot screenshot the LLE path; do not repeat the
  `0xD60` scan.

Generated-symbol renaming is closed at the useful boundary: the remaining
names are the five parked/intentional holds
`func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, and
`func_800E9AE0`. Do not re-census or invent names for them.

## Durable boundaries

### Route and rendering

Factor 5 command mappings and independent-ground-truth requirements are in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

The accepted four-arm route table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11`
reaches title and hangar, `01` reaches title only, and `10`/`00` reach neither.
This is recipe-level port evidence, not an explanation of audio or PCM. Menu
spin yield is a diagnostic route aid, not a default behavior change.

### M5 audio, status, service, wait, AI, and MORT

The generated tree reaches both target phases. Direct service entry/exit and
the service gate/loop are live. The port observes the legitimate slot-0
sequence through the service store at `0x8009B7EC`, guest address
`0x80154620`, including `0x03 -> 0x00`; retail independently observes the
same status-table cycle. Retail not executing port crash labels
`0x8000B650`/`0x80095D54` is a PC-scope boundary, not permission to alter the
port wait or guard.

s2132–s2133 and s2152–s2153 close the sampled AI-status/queue boundary:
retail queues through `osAiSetNextBuffer`; the only status poll is the
in-function `__osAiDeviceBusy`, which does not return FIFO-full on the covered
title/hangar route, and the generated caller ignores v0. Do not change
`osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`.

s2135–s2140 close the sampled RSP-image/task/output edge:
`factor5b_rsp.toml` is the retail audio image, MORT speech is separate, task
fields match, and both retail and port write `data_ptr+0x100`. The image arm
is nontrivial but its sampled host output, PCM, and validated slot completion
were absent in s2219; s2220's C88 result supplies the current downstream
discriminator. s2232's same-build A/B adds real image completion and DMA, but
  no image-stage to PCM join; the nonzero PCM rows are therefore not yet
  attributable to the image. s2234's independent retail capture adds
  exact-span attribution: the task-output watch had 303 post-target samples
  and 62 values, while the exact PCM-ring watch had zero post-target samples
  and a nonzero final snapshot. s2235's port join adds 2,753 completed image
  tasks and 6,057 stage rows, all with zero output payload bytes in the two
  target summaries; the stage destinations never overlap the selected retail
  task-output span, and no exact stage/PCM join occurs. The arm remains
  opt-in pending the source-writer audit.

s2248's same-build route gate separates that output question from a new
pre-target blocker: the image arm (`ROGUESQ_AUDIO_UCODE=1`, C88=`1`) passed
the 640 controls but crashed in `fillSampleStreamRange+8136` at guest PC
`0x8000B650`, while the silent stub with the same C88 and logging reached both
title and hangar. The image arm therefore remains opt-in, and its field348
writer/output table is still unevaluable. The next discriminator is whether
C88 changes the image arm's pre-target fate; no image writeback, slot, gate,
or default change follows.

s2252's reversed-order image-only pair did not reach the target boundary in
either arm: C88=`0` first failed in `slotDispatcherIter+3508` and C88=`1`
second failed in `fillSampleStreamRange+8136`, after both passed the 640
control. Because the two arm-specific pre-phase crashes differ and neither
has target rows, this is not evidence about task fields, image payload, or
PCM consumption. The next discriminator uses the known-qualified C88=`0`
image arm against a silent C88=`0` control under the same output traces.

s2253's same-build image+C88=`0`/silent-C88=`0` comparison passed the common
startup, `[missing-func]`, 640, and 1024 controls in both arms. The silent
arm reached stable title and two 512 hangar transitions before the known
aligned-ROM abort at guest PC `0x80001B08`; the image arm failed before stable
title in `recomp::do_rom_read+608` at guest PC `0x80001C94`. The image arm's
1024 rows had 1,369 DMA rows, 6,214 image-stage rows, and 2,984 joins, all
`stage-only` with zero source, DMEM, generated-DMA, and destination payload
bytes. This selects H-ImageArmRouteInstability at route scope and leaves the
image output contract unevaluable; it does not authorize a default, output,
slot, gate, guard, or writeback change. The next unit reverses the arm launch
order to test whether the split is launch-order/shared rather than image-arm
specific. This is single-source port evidence, not an independent retail
writer or output-contract line.

s2254 reversed that launch order: silent+C88=`0` first, image+C88=`0` second.
Both arms passed the startup, `[missing-func]`, 640, title `1024`, and hangar
`512` controls, then hit the known aligned-ROM abort. The target B40 and route-
state rows matched. Image target joins numbered 3,282 at title and 837 at
hangar, all `stage-only`; field348, stage DMEM, generated-DMA, and destination
payload summaries were zero. The image task joins nevertheless showed changed
DMEM and PCM source/consumer matches, while the stub task joins had zero DMEM
change and no image rows. This selects H-BothQualify for this reversed-order
capture and supersedes the s2253 route blocker at this scope, but it is still
single-source port evidence and does not identify the output edge.

s2255 repeated that launch order and did not qualify either arm. The silent
arm reached the 640 origin and then crashed at guest PC `0x8000B650`; the
image arm reached the same 640 route and then crashed at `0x8000834C`. Both
had the startup and `[missing-func]` controls but zero title, hangar, and
target-output rows. This is a route-validity result only; it does not
supersede s2254's qualified output table or identify a writer, consumer, or
ordering edge.

s2256 duplicated the silent arm rather than changing image behavior. Arm A
qualified title and hangar; arm B stopped at the second 640 origin after the
same startup, missing-function, and B40/route-state controls and was killed by
the driver's explicit 600-second timeout. The split between identical silent
arms selects H-IdenticalArmNondeterminism at this scope and rejects a
deterministic common silent-route explanation for this capture. It remains
single-source port evidence: the route split does not authorize an image
writeback, consumer, slot, gate, task, guard, or default change. The next
unit tests full trace load against route-only tracing with identical silent
arms.

s2257 ran that route-load discriminator. Both arms passed startup, one
`[missing-func]`, 640, and B40/route-state controls. The fully traced arm
crashed before title during `MetalFramebuffer` construction with last guest PC
`0x8000B650`; the route-only arm reached title and two hangar transitions
before the known post-hangar PI-ROM abort at `0x80001B08`. This selects
H-TraceLoad at route scope for the same-run port capture and supersedes
H-IdenticalArmNondeterminism as the sole explanation of s2256's split, but it
does not prove trace load is sufficient or necessary in general. The next
unit reduces tracing before repeating image-versus-silent output attribution;
no runtime behavior or default changes follow.

s2259 then supplied the missing single-arm reduced-trace control. The silent
arm passed the same startup/640/B40/route-state controls, reached title and
two hangar transitions, and ended only at the known post-hangar PI-ROM
alignment abort. This selects H-ConcurrentLoad at the single-arm recipe
scope and removes an intrinsic single-arm reduced-route failure as the
explanation for s2258; it does not establish pair-load causality or close
the image output contract. The next comparison returns to the same-build
image-versus-silent table.

s2260's first image-versus-silent pair reached the target route but omitted
`ROGUESQ_LOG_AUDIO_RETURN=1`. The route identity was therefore disabled, so
its zero image-stage rows were a gate failure in the measurement, not output
evidence. The fixed repeat added that gate without task-contract/ABI/DMA/PCM
tracing. Both arms reached title and two hangar transitions with the positive
controls. The image arm emitted 3,448 title and 2,201 first-hangar stage rows;
all were stage-only, title had zero nonzero rows, and hangar had two nonzero
rows (`dest=0x168E50`/`0x169150`, `len=0x300`, `nz=621`/`639`). The silent arm
emitted no target stage rows. This selects H-ImageStageIngressPresent at
stage-presence scope, single-source port evidence; it does not identify a
PCM source/consumer join or authorize a default, writeback, consumer, slot,
gate, guard, or task change. The next unit adds only phase-scoped PCM-boundary
logging to the same audio-return pair.

s2261's image-first pair added the PCM logger and found one phase-10
stage/source/consumer match with equal destination payload and valid order.
The silent arm failed before title after the startup, missing-function, and
first-640 controls, so the A/B discriminator selects H-PairRouteInvalid; the
image match is single-arm evidence only. Qualify the silent route next. The
retail oracle independently passed whole-RDRAM and observed both watched
spans, but did not join its writes to this port row.

s2262's single reduced-trace silent control passed the startup,
missing-function, two-640-transition, title, and hangar controls. Its PCM
source and consumer hooks both fired at phase 8/10/12, with 53/48/6 rows on
each side and zero payloads throughout (`fnv=0xF59C39C5`, `nz=0`). The run
ended at the known post-target aligned-ROM abort, so this is a qualified
silent route and H-SilentPcmAbsent at the measured boundary, still
single-source port evidence. The next paired run launches silent first and
image second with the same phase-scoped route and PCM logs.

s2236's port source audit passed the target-route, ABI, DMA, and PCM controls.
At both target origins, `field348 & 0x007FFFFF` was valid but the exact
`0x180`-byte source span was all zero, and the stage-0/1 DMEM input spans and
stage-2/3 generated DMA payloads were all zero. This selects H-ImageInputZero
over H-ImageIngressMissing and H-ImageTransformLoss at the measured port
boundary; it is one-source port evidence and does not identify the writer.

s2237's retail oracle independently passed its whole-RDRAM control and both
target route transitions. The exact physical spans corresponding to the two
port `field348` values were both written: `0x178C80:0x178E00` had `13,824`
writes and `0x1797B0:0x179930` had `1,058`; their post-value samples and final
snapshots were nonzero. Writer-PC histograms were present for both spans,
including `0x800078EC` in each and the `0x80090F8C`–`0x80091000` task/output
family in the first. This selects H-RetailField348Writer over
H-RetailNoField348Writer and H-RetailField348OriginSplit at the exact-watch
scope.
It remains single-source retail evidence until joined to a port-side writer
and ordering table.

s2238's port-side scalar-store hook had a positive control outside both exact
spans in each target-width route. The title source span was cleared by
`rs_memset` (`0x800078EC`) with 384 zero byte stores; the hangar source span
was cleared by the same writer with 512 zero byte stores across the two
observed 512-origin phases. The image-stage table remained zero for
field348/DMEM/generated-DMA payloads, while nonzero stores to the inactive
other span occurred only in hangar. This is a two-source boundary with the
retail writer audit, but the port-side attribution itself is single-source;
the next discriminator is the `rs_memset` callsite arguments and ordering.

s2239's bulk-entry hook supplied that second view. It passed two explicit
outside-span controls and logged 1,024 bounded target rows, with one exact
title call at `0x80178C80`, fill `0`, length `0x298`, and one exact hangar call
at `0x801797B0`, fill `0`, length `0x298`. The title exact call preceded the
first matching stage row. At hangar, the first stage row still used the
previous span `0x80178C80`; the first row using `0x801797B0` followed the
bulk clear. Existing controls in that run included 3,555 audio ABI rows,
15,754 image-stage rows, 6,553 PCM rows, and two scalar-writer controls.
The entry hook and scalar writer independently identify the legitimate
`rs_memset` zero writer at this scope; the prior s2237 retail-oracle writer
audit is the independent ground-truth line. Because generated direct C calls
leave `ctx->r31` at zero and the last-guest-PC breadcrumb at `0x80001C94`,
caller identity was not selected. No runtime behavior or default changes
follow.

s2240 supplied the missing static caller view without changing the generated
function contract. The fixup enumerated 88 direct calls and inserted a
thread-local static `jal` PC before each call; its complete-coverage check
reported 88/88 across 25 files. The retry's exact title row was
`phase=8,width=1024,origin=0x790400,span=1,static_callsite=0x8008F2CC,
dst=0x80178C80,fill=0,len=0x298`; the exact hangar row was
`phase=10,width=512,origin=0x6AB400,span=2,static_callsite=0x8008F2CC,
dst=0x801797B0,fill=0,len=0x298`. Each preceded its first matching stage
row. Outside-span controls used `0x800052C4` in both phases. The port-side
static caller and the independent s2237 retail writer audit together move the
open boundary from caller identity to the missing nonzero producer; this
remains diagnostic-only evidence.

s2245's same-build no-log A/B independently qualified both arms through title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400` twice, with the common
startup/640/missing-function controls present. Each then hit the same known
post-hangar aligned-ROM assertion with `last-guest-pc=0x80001b08`. This removes
the pre-phase route blocker for the five-store producer census, while leaving
the PI-DMA abort outside the image writer attribution question.

s2233's retail oracle passed its whole-RDRAM control, reached the driven 640,
title, and hangar phases, and wrote the broad `0x166000:0x17A000` span
`6,665,015` times in the fixed run. Its sampled post-store span was nonzero,
and the 640-only phase buckets contained 202/213 VI rows for origins
`0x00696100`/`0x00696600`. Because the oracle's phase histogram does not
bucket 1024/512 widths, the aggregate writer list cannot distinguish the
port's image-stage output from other writers in that broad span. This is
independent retail evidence against H-NoTargetRoute and a clean no-write
result, not yet evidence for the image output contract.

s2234's narrower retail oracle passed the same whole-RDRAM control and route
phases. It recorded 12,288 writes to `0x166450:0x169450`, with no post-target
samples but a nonzero final snapshot, and 303 post-target samples / 62 values
in `0x171F70:0x173DB4`. The selected post-target writer set included the
`0x80091078` through `0x80091204` task/output PCs. This is a single-source
retail selection of H-RetailTaskOutput over H-RetailPCMDirect at the measured
target boundary; it does not yet identify the port image-stage consumer.

s2218's Rice oracle passed its whole-RDRAM control, reached both target 640
origins, and found 17 writes from five PCs to the watched retail gate; its
capture did not expose every payload or the active writer for the other status
word. It also saw zero writes to `0x0014998A`, 13,319 writes to
`0x0014974C`, and all three watched task/AI callsites. This is ground-truth
capture, not authorization for a gate or task change.

### VI state and the second origin

s2198–s2204 moved the boundary from the guest swap caller to VI state.
Retail repeatedly reaches `0x00696100` and `0x00696600`; its target context
has field 0/1 respectively, and `framep` plus the selected field origin
produces the next origin. The port has matching framebuffer/mode candidates,
but its default selector chooses field 0, so it commits only the first target
origin. Same-built opt-in field-alternation and current-register arms recover
both origins.

s2200–s2216 rule out the obvious retail/port alternatives at their measured
scopes: retail's watched `osViGetCurrentField` returns zero on sampled target
rows; the port guest `comRegs.vCurrent` and `VI_V_CURRENT_LINE_REG` are also
fixed at zero; before-screen versus post-commit placement gives the same
target split; and `delta_total_vis` is one in all scheduler arms. The
legitimate natural host-register publisher and callback-versus-total-`VI`
cadence remain open. No VI recovery arm is default-on.

### Key-on branch state

s2221's port census is a positive normal-tail/slot result at sampled hangar
scope: four sites divide by `0xC0` with no guard hits and show `0x02 -> 0x00`
slot transitions; four sites have no entries. Retail independently reaches
the boundary and hangar. s2222's range witness proves that retail executes
the alternate interior path rather than simply missing instrumentation.
s2223's explicit width buckets show all eight transfer PCs in both target
origins and hangar, all eight divide PCs at zero, and phase-specific disjoint
tuple sets. s2225 showed the detail logger itself fires and reaches first
target, title, and hangar. s2226 expanded the port rings to 2048: hangar and
title had zero overflow, but six first-target rings remained capped and the
second target origin was absent. s2228's 8192 detail arm passed positive
controls (599 LLE tasks, 49 audio dispatches, 128 key-on events/slot rows, and
10,331 transfer rows) and reached the first target with zero overflow, then
crashed before title or hangar at `fillSampleStreamRange+8136`. s2229 reran
three arms: 8192 detail reached all three sampled port phases with 22 table
rows, 24,655 transfer rows, and zero overflow; 2048 detail independently did
the same, while 8192 quiet reached only 640 and 1024. The expanded detail
crash is therefore intermittent rather than a demonstrated cap or trace
boundary, and the complete 8192 table is ready for the retail-set comparison.
This remains single-source port evidence; s2223 is the independent retail
baseline. s2230 joined those sources by exact `(origin,width,PC)` bucket and
compared normalized `$v0/$s1/$a0/$a2` sets. The retail control was 10,000
whole-RDRAM writes; both common retail rows were present. The port had
nonzero LLE, audio-dispatch, key-on/slot, and transfer controls, 22 table
rows, and zero overflow. At all 16 bucket/PC cells the intersection was
smaller than both side-specific sets: first-target retail/port unique counts
were `842/3997`, `842/3996`, `858/4170`, `858/4170`, `178/246`, `178/246`,
`564/2635`, `564/2635`; hangar counts were `1347/142`, `1347/142`,
`1251/142`, `1251/142`, `484/142`, `484/142`, `926/142`, `926/142`.
Thus both directional mismatch hypotheses fire, while exact-bucket coverage
failure and parity do not. This is a two-source comparison, not permission
to rewrite the key-on path.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, dormant slot-dispatch census, two-line overlay-move class, and leftover
`fake_func_*` size-`> 0xC` class are closed at their stated scopes. M3 resumes
only as an idiom-class audit or with a new discriminator. M4
accumulator/beam evidence rules out the old shade-lane theory but is not pixel
ground truth. Remaining `func_*` placeholders are semantic holds or
intentional non-sync entries.

## Superseded conclusions

Detailed reversals are archived in `PROJECT-OVERVIEW.md` §§26 and 35–44 and
remain in the append-only ledger. Operationally:

- “640 is a flaky crash,” missing-input, missing-wait-return, and unqualified
  PCM-null claims were believable while target rows were absent; same-run
  controls and the qualified LLE/spin recipe later reached both phases.
- The old title/hangar callback split and global zero-payload image-DMA claim
  were believable before joins carried guest-address/full-span identity and
  before a nonzero hangar task was sampled.
- Clean-stub, canary-poison, final-E50, uniform-gate, and host-isolator
  explanations were believable before complete task/consumer and
  writer-specific tables. Current controls show real image DMEM activity, a
  mixed retail gate, and sampled nonzero PCM joins; none authorizes a runtime
  change.
- The s2160 wait-slot crash was initially believable as a guest wait/slot
  defect. s2161 named retail's count-byte writers and matched it to an
  unsigned PATCH address; s2162 fixed the PATCH and reached title/hangar.
- The s2163 cinematic regression is not explained by NULL pointers, guessed
  KSEG0 addressing, missing `+0x50` or heap0 stores, a deterministic keyword
  hang, or retail absence from the transform/vec3 path. s2164–s2182 refuted
  each at its stated scope; the failure remains intermittent.
- s2190–s2197's missing second-origin cells and early caller mismatch were
  coverage/scope artifacts at their earlier boundaries. The later VI-context
  table moved the open question to the port's missing field publisher; do not
  add a writer guard or task rewrite.
- s2206's quiet `0x0066AA00` route was initially plausible as damage, but
  s2208's independent Rice trace observed the same legitimate origin.
- s2215's cadence selection is superseded by s2216: all measured
  `delta_total_vis` values were one, so callback versus total-`VI` cadence is
  unresolved.
- s2221's narrow retail nulls were a coverage-only observation. s2222–s2223
  show the alternate path and its phase-specific tuples; no key-on return
  change follows. s2224's coverage selection is superseded by s2225–s2226;
  the remaining cap artifact is a measurement limit, not a runtime defect.
- s2228's early `fillSampleStreamRange+8136` crash was initially consistent
  with the enlarged census footprint. s2229's same-built 8192 detail arm
  reached first target, title, and hangar with zero overflow, while a quiet
  8192 arm stopped at title and a 2048 detail arm reached hangar. The crash is
  thus intermittent at this scope; the cap/trace explanations are not
  selected, and no runtime change follows.
- s2229's `H-TupleParityReady` was only readiness for the comparison. s2230's
  valid exact-bucket table supersedes any expectation of equal raw tuple sets:
  both port-only and retail-only values remain in every common cell. Because
  the tuples include dynamic pointer-shaped operands, this is a contract
  boundary to explain, not authorization for a key-on mitigation.
- s2242's two same-PC `fillSampleStreamRange+8136` failures made an intrinsic
  pre-phase image-arm crash plausible because they used the same unchanged
  logging arm and route. s2243's concurrent A/B instead produced different
  crash PCs (`findTileCopyId` versus `fillSampleStreamRange+8136`) before the
  target phase, so that same-PC result is not a general explanation; the
  logging/nondeterminism boundary remains open.
- s2243's divergent logging-on/logging-off pre-phase crashes left open whether
  logging contributed to the split. s2244 repeated the concurrent design with
  logging disabled in both arms: one arm reproduced `fillSampleStreamRange`
  while the other reached title 1024. This rules out a logging-only
  explanation at this scope, but the forced termination before hangar leaves
  route completion open.
- s2245 supersedes s2244's incomplete route qualification: both no-log arms
  reached title and hangar before independently hitting the same known
  post-hangar PI-DMA alignment abort. The shared abort does not explain the
  earlier pre-phase split and does not authorize a PI or image mitigation.
- s2257 refines and supersedes s2256's H-IdenticalArmNondeterminism as the
  only explanation for that capture: under the same startup/640/B40 controls,
  the full-trace silent arm failed before title while the route-only silent arm
  reached title and hangar. This is a single-source same-run route-load result,
  not proof that logging alone caused the crash or authorization for a runtime
  mitigation.
- s2259 supersedes H-ReducedRouteInstability as an intrinsic explanation for
  the reduced recipe at single-arm scope: the silent control reached title and
  hangar with the same positive controls before the known post-hangar abort.
  The result was believable after s2258 because both reduced-trace arms had
  failed before target, but the single-arm run shows that pair load or another
  same-run interaction remains open; it does not authorize an image default,
  output writeback, consumer, slot, gate, or guard change.
- s2260's first pair appeared to reproduce the prior image-stage null, but the
  source gate showed that `ROGUESQ_LOG_AUDIO_RETURN` was absent and the route
  identity never armed; the null was therefore a measurement defect. The
  fixed repeat qualified both arms and produced image-stage rows in the image
  arm but none in the silent arm, superseding the invalid null only at
  stage-presence scope. The stage rows were still stage-only, so no
  source/consumer, writeback, or default conclusion follows.
- s2246–s2247 treated repeated instrumented image-arm failures as a route-
  stability blocker because no same-run target control qualified. s2248's
  concurrent silent-stub arm reached title and hangar while the image arm
  reproduced the pre-title failure, so shared nondeterminism is no longer the
  sole explanation at this scope. This refines the blocker to the image route
  without identifying its writer or authorizing a mitigation.
- s2249 refines s2248's image-route blocker: the same-build C88=`0` image arm
  reached both target phases while C88=`1` failed before title, so the route
  split selects a C88/image interaction rather than an image-arm-only
  blanket failure. Its single hangar output join does not overturn the
  title/all-zero result or identify a writer; those earlier nulls remain
  valid at their measured phase/task scopes.
- s2250 supersedes the deterministic route interpretation of s2249's C88
  split: both image arms passed the 640, title, and hangar route controls, and
  their normalized target route-state rows matched. The prior split was
  believable because s2249 had the same startup/640 controls and a clean
  C88=`1` pre-title failure while both controls reached the targets; s2250
  shows that the failure is intermittent at route scope. The B40 store/read
  difference is the intended C88 behavior, not an unexplained downstream
  route edge, and no runtime change follows.
- s2253's image-arm route blocker was believable because the image arm failed
  before stable title while the silent control reached title and hangar under
  the same startup/640 controls. s2254 reversed their launch order and both
  arms qualified through title and hangar with matched target route-state/B40
  rows. This supersedes the blocker as a deterministic image-arm explanation
  at that scope; the target image joins remain a separate output-contract
  question, and no runtime change follows.
- s2232's image-arm PCM activity is not evidence of image-output correctness:
  the same-run image summary recorded zero stage/source and stage/consumer
  matches, while the nonzero PCM rows were consumer-only at the image-join
  boundary. The arm remains useful evidence of DMEM/DMA and completion, but
  no output writeback, gate, or default flip follows.
- s2234 supersedes the unresolved broad-span retail attribution only at the
  exact-watch scope: the task-output span has target-phase writes, while the
  exact PCM ring does not. The final PCM snapshot and lifetime write count do
  not establish its target-phase writer, and the result remains single-source
  until joined to the port image-stage rows.
- s2235's first capture was a pre-target `fillSampleStreamRange+932` crash;
  the fresh retry reached both target phases and supplied the positive controls
  and joins. The first attempt is therefore a failed run, not a selected null;
  the retry rules out H-PortNoTargetRoute for its covered scope and selects
  H-PortContractGap instead.
- s2237 supersedes the exact-span retail no-writer and one-origin hypotheses:
  both `field348`-derived physical spans had writes, nonzero post-store
  samples, and writer-PC rows under the same whole-RDRAM and route controls.
  This does not supersede s2236's port-side zero-source observation; it moves
  the open boundary to a port writer/order comparison.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35; s1880–s1949 is
§36; M5 archives through s2047 are §§37–38; the late route/fill boundary is
§39; s2080–s2108 is §40; B40 is §41; s2113–s2158 is §42; s2164–s2197 is
§43; and s2198–s2226 is §44. Sessions s2227–s2262 remain in the ledger.
Exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`.

Selected hypotheses must not be widened from single-source or single-arm
observations. Do not re-flip the image default, guess S32 addressing, NULL-
skip, skip/allow `matchKeywordWithPriority` or its loads, disable
`NAN_CHECK`, add a wait/slot guard, or land a copyToRAM/CIMG writeback guard.
Do not treat last-guest-PC `0x8000834c` as the abort site.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical addresses and
  should be phase-gated by VI callbacks.
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
- A mitigation is not an explanation. Name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a whole discriminating table and an
  outcome that selects among hypotheses. Repeated counters are not a work
  unit.
