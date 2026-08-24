# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2227–s2262 is summarized in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) §45; the append-only ledger is
authoritative for exact commands, counts, and probe rows.

Maintained in Session 2293 (2026-08-24); behavioral and source evidence is
current through s2293. The corrected same-build M5 Step 2 driver explicitly
sent the eleven process-start Start events to each port window. Retail passed
the whole-RDRAM threshold at `10,000` callbacks and reached title
`1024 @ 0x00790400` and hangar `512 @ 0x006AB400`. The port stub and default
image arms both reached title and hangar; the default emitted the expected
image-stage/DMA rows, including nonzero phase-10 payloads. This selects
H-PortStubRouteRestored and H-DefaultSafe at the tested recipe scope. The
later arm crashes were post-target known failures, not route-gate failures.

s2291's final same-build M5 Step 3 capture passed independent retail
whole-RDRAM/title/hangar controls and the port's explicit-Start/title/hangar
controls. One sampled retail metadata writer published the same destination
pointer and `0x300` length as a nonzero port phase-10 image row, but the retail
writer class was CPU metadata construction while the port row was Factor 5
image DMA with its own payload and source/consumer ordering. This selects
H-RetailDifferentWriter at the measured contract scope, not an address-class
null or a mitigation target.

s2292's fixed all-ring-slot capture passed the independent retail
whole-RDRAM/title/hangar controls and the port's title/hangar plus explicit
keycode-36 Start control. All 16 `0x300` slots from `0x166450` through
`0x169150` recorded `768` retail writes, every slot's writer histogram was
guest PC `0x800078EC`, and every final slot snapshot was nonzero. The
qualified port produced two unique nonzero phase-10 rows at
`0x168850/FNV 0x2B9E9631/nz=621` and
`0x168B50/FNV 0x6ADD4218/nz=639`. Retail supplied no exact payload-FNV or
writer-order join to either row; its final slot snapshots differed and its
post-value sample counts were zero. This resolves ring rotation at the
address-class scope and selects H-RetailDifferentWriter/ContractGap, not
H-RingRotationUnresolved, H-CoverageInvalid, or a mitigation target.

s2293's corrected oracle-only target-phase capture passed the independent
whole-RDRAM threshold at `10,000`, title `1024 @ 0x00790400`, and hangar
`512 @ 0x006AB400`. Guest PC `0x800078EC` executed `1,359,560` times in the
target phase, with sampled tuples pointing into `0x8065E0A0`-class data and
lengths such as `0x1C`; the target-gated post-value summary was `0/16` and no
candidate slot had a target-phase writer join. All 16 slots still had `768`
lifetime writes from `0x800078EC` and nonzero final snapshots. This selects
H-RetailMetadataContract at the measured scope: it refutes
H-RetailWriterPreTarget as a claim that the watched PC is absent from the
target phase, but does not yet distinguish all candidate writes being
pre-target from a different target-phase writer. It rules out
H-RetailWriterTargetPhase for the sampled PC and H-CoverageInvalid; no
writer, writeback, consumer, slot, gate, guard, or address-remap change is
authorized.

The s2287 oracle used the corrected eleven-Start route and `--vi-trace`; its
positive control was reached before the whole-RDRAM watch was removed, and
the title/hangar rows continued through the run. The exact-PC null is valid
at this scope, but it does not claim that retail lacks a semantically
equivalent path at another guest address.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400` with `ROGUESQ_LLE_FORCE=1`,
  `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name the writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio now defaults to the Factor 5 image arm; `ROGUESQ_AUDIO_UCODE=0`
  selects the silent `M_AUDTASK` `Broke` stub for controls. The default flip
  is qualified at the tested route scope: s2290's explicit eleven-Start
  stub-first gate reached title/hangar and the default image arm reached the
  same phases. No further default-selection change is authorized by this
  result. C88=`1` remains a diagnostic behavior arm.
  Stock `aspMain` is not the game's MusyX / Factor 5 contract, and MORT is a
  separate CPU speech asset.
- s2287's independent retail route watch passed the whole-RDRAM, title, and
  hangar controls but recorded no execution of guest PCs `0x800547BC` or
  `0x80007904` in any phase. s2288's stub control then reproduced the latter
  port-side crash before the target route. s2289's slot-route discriminator
  then showed that retail does execute the equivalent route, so the Step 2
  pair remains port-route-invalid but is no longer blocked on whether retail
  enters slot dispatch.
- s2289's independent retail slot-route watch passed the whole-RDRAM, title,
  and hangar controls. At initial `640 @ 0x00696100`, retail recorded 110
  phase-gated `slotDispatcherIter` hits, 2 `slotDispatcherInner` hits, and 5
  `cinematicSlotBatchDispatch` hits, with nonzero `exec-prev` attribution;
  `0x80007904` remained at zero. Combined with s2288's port-side
  `slotDispatcherIter+3508` / `[missing-func]` crash, this selects
  H-RetailEquivalentSlotRoute at recipe scope. It rules out the hypothesis
  that retail simply omits the slot route, but not the exact port-side writer,
  callback/list state, or overlay dispatch edge.
- s2290's corrected same-build route requalification passed the independent
  retail whole-RDRAM, title, and hangar controls. Explicit port keycode-36
  Start delivery produced SDL key and host Start controls in both arms. The
  stub reached title and hangar before the default arm was launched; the
  default then reached the same title/hangar phases. Stub/default totals were
  respectively `59/56` audio dispatch, `1273/1102` task ABI and DMA rows,
  `0/2227` DMA-range rows, `0/4470` image-stage rows, `519/518` audio-return
  rows, `2271/2241` audio-route rows, `1024/1024` gate rows, and `89/88`
  PCM source/consumer rows per side. The default target window included
  nonzero phase-10 image payloads with `nz=621` and `nz=639`; the stub had no
  image-stage rows. Both arms had one missing-function marker and later
  post-target crash markers, after route qualification. This selects
  H-PortStubRouteRestored and H-DefaultSafe at this recipe scope; it does not
  identify a new writer or authorize a mitigation.
- s2291's final writer-join capture passed the retail whole-RDRAM threshold at
  `10,000`, retail title/hangar, and port title/hangar controls with explicit
  process-start keycode-36 delivery. Retail recorded `882,417` writes in the
  candidate span `0x166000:0x16A000`, `293` post-target candidate samples, and
  `76` post-target writes to the independent task/output span
  `0x141AD0:0x141AF0`. The qualified port row recorded destination
  `0x166750`, length `0x300`, FNV `0x7B70923A`, `639` nonzero bytes, and a
  source-before-consumer match with no ordering violation. Retail's forced
  rows showed `0x80029E8C` publishing `0x80166750` and `0x80029E98`
  publishing length `0x300` in its metadata table; the payload-producing
  retail store was not the same writer class as the port's Factor 5 image DMA.
  This selects H-RetailDifferentWriter at the sampled tuple scope and rules
  out H-RetailDifferentAddressClass and H-CoverageInvalid. No runtime change,
  writeback, consumer, guard, or address remap is authorized.
- s2292's fixed all-ring table passed retail whole-RDRAM at `10,000`, retail
  title/hangar, and port title/hangar with four explicit keycode-36 deliveries
  before the known post-target port crash. The retail candidate span had
  `880,070` writes; each of the 16 exact `0x300` slots had `768` writes,
  all attributed to PC `0x800078EC`, with nonzero final snapshots. The port
  had two unique nonzero phase-10 rows: `(0x168850,0x300,0x2B9E9631,621)` and
  `(0x168B50,0x300,0x6ADD4218,639)`. No exact retail payload or ordering join
  was observed, so this closes the ring-rotation alternative but leaves the
  retail/port payload contract gap open. The first attempt was discarded
  because its new gate incorrectly required all eleven scheduled Start
  deliveries even though the port had already reached both target phases;
  the fixed rerun required one recorded keycode-36 delivery and retained all
  controls. No runtime, writer, consumer, slot, gate, guard, or address-remap
  behavior changed.
- s2293's corrected oracle-only target-phase writer capture passed retail
  whole-RDRAM at `10,000`, title, and hangar. The watched `0x800078EC`
  executed `1,359,560` times at `512 @ 0x006AB400`, but its sampled target
  tuples pointed into `0x8065E0A0`-class data rather than the candidate
  `0x166xxx` slots. The target post-value table was `0/16`; every slot had
  `768` lifetime writes from `0x800078EC` and a nonzero final snapshot. This
  selects H-RetailMetadataContract at the measured scope and leaves the
  target-phase writer-PC split open. No runtime or mitigation behavior
  changed.
- `docs/M5-AUDIO-PLAN.md` inventories the active audio stubs/traps/gates and
  defines the phase-keyed task→DMA→service→slot→voice→PCM discriminator and
  rollback conditions. The plan refresh in s2231 defined the incremental
  contract; s2288 changed the runtime selection but did not qualify the
  promotion.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. Its host canary is probe data only; it does not gate
  completion, writeback, or DMA.
- The image arm has qualified target-stage rows. s2268 observed one exact
  phase-10 stage/source/consumer match, and s2272 observed two more exact
  phase-10 matches in a phase-gated staggered pair. The silent arm qualified
  through title and hangar in s2272; its phase-8/10/12 source and consumer
  rows were present but all zero. The measured output contract is complete
  for the observed nonzero rows. s2290 requalified the image arm as the
  default after the stub reached the same title/hangar route; no default
  polarity change is still pending.
- The port-side `field348` source spans are cleared by the legitimate
  `rs_memset` setup call at static callsite `0x8008F2CC`; retail independently
  writes both corresponding spans with nonzero values. The missing nonzero
  producer/order boundary remains diagnostic-only and does not authorize a
  writer guard or task rewrite.
- The M5 key-on comparison is open: exact `(origin,width,PC)` tuple buckets
  show both port-only and retail-only values in every common cell. s2278's
  qualified port witness fired once at all eight transfer PCs with
  `raw_ptr=0x801772F0`, `source_word=0x00C0053F`, selector `0`, and state
  `0x6F5F`. s2279's oracle field dump independently fired at all eight PCs
  with whole-RDRAM, title, and hangar controls, but its bounded unique-field
  buckets saturated (`hits=17,987`, overflow `14,718`–`15,911` in the fixed
  100-second run) while the port arm missed the required hangar and crashed
  at off-target `512 @ 0x00690400`. s2280 raised the cap to 32,768 and the
  retail buckets completed with `hits=16,852` per PC, `1,636`–`3,843` unique
  rows, and zero overflow; the port reached title but stalled at off-target
  `640 @ 0x00696100` and never reached `512 @ 0x006AB400`. The source/state
  join is therefore still H-CoverageInvalid; no pointer-versus-branch verdict
  follows. s2281's same-build C88 pair independently passed the port B40 and
  route-state controls in both arms. C88=0 reached title, then crashed during
  off-target `640 @ 0x00696100` at guest PC `0x8000B650`; C88=1 crashed in
  the same off-target phase before title, also at `0x8000B650`. Neither arm
  reached the hangar or emitted target key-on rows. s2282's staggered C88=0
  control passed neither B40 nor route-state controls and remained at the
  off-target `640 @ 0x00696100` until its 220-second watchdog; C88=1 was not
  launched. The three consecutive route-invalid attempts s2280–s2282 leave
  H-C88-route versus H-RouteLoad unresolved but park this discriminator under
  the no-fourth-attempt rule.
- The VI second-origin publisher/cadence is open but route-parked. Field,
  current-register, timing, and total-`VI` arms recover the split, but none is
  default-on. s2283's corrected four-arm matrix supplied `8` all-width
  `[vi-context-port-control]` and `8` `[vi-parity-scheduler-control]` rows per
  arm, then all four arms crashed at guest PC `0x80001F88`. s2284 split the
  arms into two concurrent waves: wave 1 (control and alternate-field) and
  wave 2 (current-register-screen and retrace-parity) each supplied `8` rows
  of both controls per arm, then all four reproduced the same initial-640
  crash before `0x00696100` or `0x00696600`. Retail independently passed the
  whole-RDRAM, title, and hangar controls. Two independent waves select
  H-RouteIntrinsic at this recipe scope, not H-NoPublisher; no publisher arm
  is interpretable until a new route discriminator restores target coverage.
- s2273's first Step 1 pair was route-invalid: the heavy trace reached title
  and the first 640 target before `findOrCreateMaterial` crashed at guest PC
  `0x8000E29C` with one `[missing-func]`, 11 B40 rows, and 20 route-state
  rows; the corrected reduced trace stalled after the 640 target
  `0x00696100` with one `[missing-func]`, six B40 rows, and ten route-state
  rows, then was SIGKILLed. Neither pair arm reached the required hangar
  control. No audio contract null is interpretable.
- s2274 rebuilt the unchanged target and repeated the Step 1 pair. The first
  arm reached title `1024 @ 0x00790400`, then returned to 640 at
  `0x00696100` and crashed in `MetalCommandList::barriers` at guest PC
  `0x80001F88`; the image arm was not launched. After removing the extra
  thread-resume, OST-writeback, and runner-all logs, the silent arm reached
  title and an off-target `512 @ 0x00690400`, then crashed in
  `allocAndInitGridCellArray+1276` at guest PC `0x80001C94`, still without
  `512 @ 0x006AB400`. The reduced arm had one `[missing-func]`, 13
  `[m5-b40-route]` rows, 25 `[m5-route-state]` rows, 67 audio-dispatch rows,
  263 stub returns, and 51/51 phase-8 PCM source/consumer rows; these are
  route controls only. Both captures are H-RouteInvalid, so no audio/output
  null is interpretable and no image arm ran.
- s2275's single silent control reached title `1024 @ 0x00790400` at 49.5s,
  then remained alive through an off-target `640 @ 0x00696100` transition at
  74.4s and missed `512 @ 0x006AB400` until the 180-second watchdog SIGKILL.
  It produced one `[missing-func]`, 11 B40 rows, 20 route-state rows, 64
  audio-dispatch rows, and 51/51 phase-8 PCM source/consumer rows, with no
  `[CRASH]` or `[ABORT]` marker. This selects H-RouteStall at the tested
  scope; audio/output nulls remain uninterpretable and the image arm remains
  unlaunched.
- s2276's retail oracle passed its whole-RDRAM control with 10,125 writes and
  repeatedly reached the retail hangar origin `0x006AB400`. The silent port
  arm reached title `1024 @ 0x00790400`, then crashed in
  `slotDispatcherIter+3508` at guest PC `0x80007904` after an off-target
  `640 @ 0x00696100`; it had 72 dispatches, 266 audio-return rows, and 51/51
  phase-8 PCM source/consumer controls. The image arm emitted 48 dispatches
  and one `[missing-func]` but stalled in the initial 640 route before title,
  with no target-phase audio rows. Both arms missed `512 @ 0x006AB400`, so
  the pair selects H-RouteInvalid and leaves audio/output nulls unevaluable.
- s2277's M5 Step 0 oracle passed its whole-RDRAM positive control with 21,519
  writes, 17 writes to `0x800A0F50`, 108 task-field writes at physical
  `0x141AD0..0x141AEF`, and repeated retail hangar origins. The unchanged
  silent port control emitted 47 `[audtask-dispatch]` rows but crashed at
  guest PC `0x8000B650` after off-target `640 @ 0x00696100`; it emitted no
  SP-completion/audio-return/PCM rows and reached neither title nor hangar.
  This selects H-PortControlMissing for the Step 0 comparison. Audio and
  output nulls remain unevaluable; the silent default and image opt-in are
  unchanged.

## Latest evidence

- s2290's corrected same-build Step 2 driver passed the independent retail
  whole-RDRAM positive control at 10,000 callbacks, title, and hangar. The
  port driver explicitly delivered Start keycode 36 at process-relative
  offsets 6, 11, 16, 21, 26, 31, 36, 41, 46, 51, and 56 seconds; SDL key and
  host Start controls fired in both arms. The stub arm reached title and
  hangar, so the default arm was launched; the default image arm also reached
  title and hangar. Stub/default totals were `59/56` dispatch,
  `1273/1102` task-ABI and DMA rows, `0/2227` DMA-range rows, `0/4470`
  image-stage rows, `519/518` audio-return rows, `2271/2241` audio-route
  rows, `1024/1024` gate rows, and `89/88` PCM source/consumer rows per side.
  The default target window included nonzero phase-10 image payloads with
  `nz=621` and `nz=639`; the stub had no image-stage rows. Each arm had one
  missing-function marker and later crash markers after target qualification.
  This selects H-PortStubRouteRestored and H-DefaultSafe at the tested recipe
  scope. No runtime behavior, writer, guard, or default polarity changed.
- s2288's same-build Step 2 driver passed the independent retail controls:
  whole-RDRAM threshold `10,000`, title `1024 @ 0x00790400`, and hangar
  `512 @ 0x006AB400`. The explicit stub arm emitted 48 `[audtask-dispatch]`
  rows, one `[missing-func]`, and 36 crash-marker lines, terminating at
  `slotDispatcherIter+3508` / guest PC `0x80007904` before any title or
  hangar phase. It emitted zero task ABI, DMA, image-stage, audio-return,
  service/gate/slot/voice, or PCM source/consumer rows. The driver therefore
  withheld the default arm. This selects H-RouteInvalid for the recipe and
  leaves H-DefaultSafe, H-ImageContractGap, and H-DefaultRouteRegression
  untested; no default or mitigation conclusion follows.
- s2289's retail-only route discriminator passed its positive whole-RDRAM
  control at 10,000 callbacks, title, and hangar. The phase-gated initial-640
  rows were 110 for `slotDispatcherIter`, 2 for `slotDispatcherInner`, and 5
  for `cinematicSlotBatchDispatch`; the final oracle counts were 3,244,
  314, and 177 respectively, with 17 slot-dispatch `exec-prev` pairs and zero
  hits at `0x80007904`. This is independent retail evidence for
  H-RetailEquivalentSlotRoute; it does not identify a port writer or justify
  changing the callback/list state.
- s2287's retail-only route-boundary run passed the whole-RDRAM positive
  threshold at 10,000 callbacks, reached title `1024 @ 0x00790400` at about
  17.3s, and reached hangar `512 @ 0x006AB400` at about 38.4s. The full
  180-second VI trace included three initial `640 @ 0x00696100` rows and
  recorded zero hits for both watched PCs `0x800547BC` and `0x80007904`; no
  `exec-prev` attribution was therefore emitted. The timed oracle teardown
  returned 139 after the controls had passed. This selects H-PortOnlyBadPath
  when combined with the prior port-side crash witness and closes this exact
  PC boundary; it does not identify an audio writer or justify a mitigation.
- s2284's fixed two-wave driver first gated on one retail oracle's
  whole-RDRAM threshold (`10,000` callbacks), title, and hangar origins. The
  wave-1 control and alternate-field arms then each passed `8`
  `[vi-context-port-control]` and `8` `[vi-parity-scheduler-control]` rows,
  recorded no `0x00696100` or `0x00696600` target rows, and aborted at guest PC
  `0x80001F88`. After both exited, wave 2 launched current-register-screen
  and retrace-parity; each again passed `8` rows of both controls, recorded no
  target rows, and aborted at the same guest PC. The first driver attempt was
  measurement-invalid because it killed the oracle before its title/hangar
  controls; the gated rerun is the only result used here. This selects
  H-RouteIntrinsic for the two-wave recipe and supplies no VI publisher
  verdict.
- s2285's gated M5 Step 1 driver passed the independent retail whole-RDRAM,
  title, and hangar controls. The corrected silent port arm reached title
  `1024 @ 0x00790400`, with `64` dispatch rows, `1,020` task ABI and DMA rows,
  `262` audio-return rows, `512` gate rows, and `52/52` PCM source/consumer
  rows, then crashed in the off-target `640 @ 0x00696100` return at
  `slotDispatcherIter+3508` / guest PC `0x80007904`. It had no hangar phase,
  so the image arm was correctly withheld. This is H-RouteInvalid and does
  not interpret any downstream audio null or promote the image arm.
- s2286's trace-light rerun passed the independent retail whole-RDRAM,
  title, and hangar controls. With `ROGUESQ_LOG_VI_CALLERS` removed, the
  silent port reached the initial off-target `640 @ 0x00696100` phase and
  then bus-crashed at guest PC `0x800547BC`, symbolized as
  `mat34CrossRowsAndCopyPos+60`, around 26.2s. It emitted 48
  `[audtask-dispatch]` rows and one `[missing-func]`, but zero B40/route-state
  or target-phase rows; the image arm was not launched. The logger-removal
  hypothesis is therefore not supported, and this remains H-RouteInvalid
  rather than an audio-contract null.
- s2283's corrected same-build four-arm A1 matrix ran one independent retail
  oracle plus control, alternate-field, current-reg-screen, and retrace-parity
  port arms. Retail passed the whole-RDRAM positive control with `10,000`
  writes and reached title `0x00790400`/1024 and hangar `0x006AB400`/512. Each
  port arm passed `8` VI-context and `8` parity-scheduler all-width controls
  and recorded roughly `50` initial 640 rows, but recorded zero
  `0x00696100`/`0x00696600` target rows and crashed at guest PC
  `0x80001F88` before title or hangar. This selects H-RouteInvalid for the
  four-way concurrent recipe and supplies no publisher/cadence verdict. The
  first run of the driver was invalid because its zsh associative-array PID
  assignment stored the literal `$!`; the corrected rerun is the only result
  used here.
- s2282's phase-gated control-first driver ran one independent retail oracle
  and launched C88=1 only after a C88=0 hangar gate. Retail passed the
  whole-RDRAM positive control with 1,000,128 writes, title and hangar
  origins, all eight transfer-PC controls with 123,766 hits each, and eight
  field buckets with 27,755 hits each, 1,734–4,960 unique rows, and
  `overflow=0`. The port C88=0 arm reached only the off-target
  `640 @ 0x00696100` phase and was SIGKILLed at the 220-second deadline; it
  had no title/hangar, B40, route-state, or key-on rows. The required launch
  gate was absent, so C88=1 was not launched. This independently confirms
  H-CoverageInvalid and supplies no C88-route, key-on pointer/data, or
  branch-state verdict.
- s2281's same-build C88=0/C88=1 route pair ran with one independent retail
  oracle. Retail passed the whole-RDRAM control with 998,960 writes, title
  and hangar origins, all eight transfer-PC controls, and eight field buckets
  with `overflow=0` (`27,256` hits each, `1,729`–`4,958` rows). Both port
  arms passed positive B40/route-state controls and one `[missing-func]`.
  C88=0 reached title but returned to off-target `640 @ 0x00696100` and
  crashed at guest PC `0x8000B650`; C88=1 crashed in that off-target phase
  before title, also at `0x8000B650`. Neither reached
  `512 @ 0x006AB400`, so this selects H-CoverageInvalid and supplies no
  pointer/data or branch-state verdict. No runtime behavior or default
  changed.
- s2276's fresh oracle-plus-pair run passed the retail whole-RDRAM and hangar
  controls. The silent port arm reached title and then crashed in
  `slotDispatcherIter+3508` after an off-target 640 transition; the image arm
  failed in the initial 640 route. Neither arm reached the required hangar
  origin, so this is H-RouteInvalid and supplies no audio/output null.
- s2277's Step 0 oracle-plus-port control passed independent retail controls,
  but the unchanged port arm crashed before title and hangar. Its dispatch
  count is a positive instrument control only; the missing SP/audio/PCM rows
  are route-invalid nulls and do not identify an audio writer.
- s2278's first paired driver was route-invalid: retail passed the whole-RDRAM
  control and title/hangar gates, while the port reached title but crashed at
  an off-target `512 @ 0x00690400` before the hangar. The fixed established
  eleven-Start route then reached port title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`; B40/route-state/input controls fired, all eight new
  pointer/branch rows fired, and the later known aligned-ROM abort occurred
  only after target qualification. A corrected retail detail run again passed
  the whole-RDRAM control, title/hangar gates, and all eight transfer PCs.
  The target rows agree on the `0xC0` denominator and zero caller selector,
  while raw pointers and the port pointed-to word differ; full retail
  source-word/state joining remains open.
- s2279's new oracle-side `--pc-field-dump` passed the positive-control,
  title, hangar, and all-eight-PC controls in the requested retail run. Its
  256-row per-PC unique tuple cap saturated every bucket, so the printed
  pointed words and branch fields cannot be treated as a complete table. The
  requested port driver died before title; the fixed established-route driver
  reached title but stopped at off-target `512 @ 0x00690400` with
  `port_rc=138` and no `512 @ 0x006AB400`. This pair is H-CoverageInvalid and
  does not select H-PointerData, H-BranchState, or H-Mixed.
- s2280 rebuilt the oracle with a 32,768-row per-PC cap. Retail passed the
  whole-RDRAM, title, hangar, and all-eight-PC controls; each bucket had
  `16,852` hits, `1,636`–`3,843` rows, and `overflow=0`. The port reached
  title `1024 @ 0x00790400`, then stalled in off-target `640 @ 0x00696100`
  until the driver SIGKILLed it, with no target key-on rows. This pair remains
  H-CoverageInvalid and does not select H-PointerData, H-BranchState, or
  H-Mixed.
- s2274's two same-build route attempts failed before the expected hangar
  origin despite positive dispatch/audio/route probes. Removing the three
  high-volume host trace categories changed the failure from a renderer
  barrier crash after title to an off-target 512 phase followed by
  `allocAndInitGridCellArray`; it did not produce a qualified comparison.
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
  retail task/output writer family. s2291 joined one retail destination
  pointer/length metadata tuple to a nonzero port image-stage/DMA tuple; the
  writer class and payload-production edge differ at that measured scope.

## Active backlog

Closed investigations are not active work items. The sequence is monotonic.

1. **M5 Step 3 target-phase slot-writer split.** s2293 established that
   `0x800078EC` executes `1,359,560` times in the hangar target phase, while
   its 16 candidate slots have only lifetime writer counts and zero
   target-gated post-value rows. Run one new oracle-only 16-slot table with
   `--pc-hist-phase 0x006AB400` in addition to the existing whole-RDRAM,
   task/output, title, hangar, exact-slot, watched-PC, and post-value
   controls. Classify each slot's target-phase writer count and PC histogram
   as all-pre-target, `0x800078EC` target writes, or a different target
   writer. Do not implement writeback, consumer, slot, gate, guard, or
   address-remap behavior.
2. **M5 key-on tuple contract.** Requalify the C88 route with a
   phase-gated control-first stagger: launch C88=1 only after a C88=0 control
   reaches `512 @ 0x006AB400`, then compare retail fields only if both arms
   reach the hangar. s2281's concurrent pair and s2282's control-first stagger
   both remained coverage-invalid; s2282 never launched C88=1. After the
   three consecutive no-discriminator attempts s2280–s2282, do not repeat
   this route pair without a new route discriminator. No pointer/data or
   branch-state verdict, key-on return, or mitigation change follows. The
   Step 1 task/output pair remains parked.
3. **M5 A1 second-origin transition.** Parked after s2283's four-way and
   s2284's two-wave matrices. Each wave supplied both positive controls in both
   arms but reproduced the initial-640 crash at guest PC `0x80001F88`, so the
   two independent wave results select H-RouteIntrinsic at this recipe scope.
   Do not repeat the four A1 arms without a new route discriminator that can
   restore `0x00696100`/`0x00696600` coverage; no publisher or default follows.
4. **M5 drain in-loop tick A/B.** Parked after s2125–s2128 failed to place
   both arms in a target comparison. Resume only with a new renderer or
   ground-truth discriminator.
5. **M3 crash work.** Resume only as a systematic idiom-class audit with a
   named discriminator; the dormant `slotDispatcherIter+872` class has
   thousands of clean guarded hangar calls and no authorized mitigation.
6. **Hangar visual artifact.** Malformed-triangle H2 and consumer-mode H1 are
   refuted. H3 is unavailable because the oracle cannot screenshot the LLE
   path; do not repeat the capped `0xD60` scan.

The s2287 exact-PC retail route-boundary discriminator and s2289 equivalent
slot-route discriminator are complete. Both passed independent controls;
s2287 recorded no exact hit for either port crash PC, while s2289 recorded
retail slot-dispatch execution in the initial-640 phase. s2290's corrected
port route then passed the stub gate and qualified the default comparison. The
s2288 stub-first crash remains a route-load sensitivity observation, not a
route guard, audio-null, or writer conclusion.

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
This closes output-contract completeness at the measured scope, and s2290's
stub-first/default-second run qualifies the default image arm through the same
title/hangar route. This still does not authorize a writeback, consumer, slot,
gate, or guard change.

s2291 adds a retail/port writer-class boundary: retail metadata writes can
publish the same output pointer and `0x300` length as a port nonzero image
row, while the port payload is produced by Factor 5 image DMA and joined to a
PCM source/consumer path. s2292 additionally identifies retail PC
`0x800078EC` as the writer for all 16 candidate slots, but finds no exact
target-phase payload/order join. s2293 shows that the same PC executes
`1,359,560` times in the hangar target phase with tuples pointing into
`0x8065E0A0`-class data, while its candidate-slot target post-value table is
`0/16`; its lifetime slot writes remain `768` per slot. The retail writer
contract remains open pending a target-phase writer-PC histogram; this is a
contract discriminator, not permission to add a writeback or guard.

Do not flip the image default again, force C88, skip or allow
`matchKeywordWithPriority`, add a wait/slot guard, or land a copyToRAM/CIMG
writeback guard. Do not treat last-guest-PC `0x8000834c` as the abort site.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-`VI` arms recover the
split; the natural host publisher and cadence are unidentified. s2283's
four-way arm matrix did not reach either target origin after positive controls,
so it adds a route-contended null only. The A1 matrix remains parked until a
new route discriminator restores target coverage.

### Key-on, M3, and M4

Retail executes the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with no guard
hits. The exact phase-keyed tuple table is complete and bidirectionally
different at all common cells. s2278 adds a qualified port pointer/source/
  state witness and retail transfer/selector/denominator controls; the raw
  pointer is not yet a valid cross-runtime identity because retail voice-list
  addresses vary within the phase. The useful next boundary is the oracle-side
  full-word/state join, but only after a new route discriminator restores a
  common target window. s2280's enlarged retail census is complete at the
  measured scope; s2281's C88=0 and C88=1 port arms both supplied no target
  window, and s2282's control-first C88=0 arm stalled before title/hangar.

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
- s2283's four-arm A1 matrix is a route-invalid observation: all four port
  processes reached the same initial 640 region and aborted before the target
  origins, while retail independently reached title and hangar. It does not
  make any VI publisher arm intrinsically defective or support H-NoPublisher;
  the next two-wave run tests the contention explanation.
- s2271's order-swapped pair made arm-specific paired-route sensitivity look
  plausible because the image arm qualified when second while the silent arm
  failed to reach hangar when first. s2272's phase-gated stagger kept the
  silent arm qualified after the image launch and closed both image joins, so
  the earlier result is superseded as an intrinsic arm defect; initial
  pre-target paired contention remains the selected route explanation at this
  recipe scope.
- s2273–s2275's Step 1 captures were route-invalid before a paired audio/output
  window. The final single-arm capture stayed alive after title in the
  off-target 640 phase and was killed by the route watcher, so its PCM and
  audio nulls do not overturn the qualified s2268/s2272 output evidence or
  identify an audio writer.
- s2276's Step 1 pair is the same route-invalid class with an independent
  oracle control: the silent arm supplied target-adjacent audio/PCM controls
  before a route crash, while the image arm failed earlier. It does not make
  the image arm intrinsically defective or explain any audio null.
- s2277's Step 0 oracle-plus-port control passed independent retail controls,
  but the unchanged port arm crashed before title and hangar. Its dispatch
  count is a positive instrument control only; the missing SP/audio/PCM rows
  are route-invalid nulls and do not overturn qualified output evidence or
  identify an audio writer.
- s2288's Step 2 stub-first crash was believable as a port callback/list gap
  because it occurred before title/hangar and withheld the default arm. The
  corrected s2290 route supplied explicit Start input, passed the same route
  gate, and qualified both arms through title/hangar; s2288 is therefore
  superseded as a route-invalid conclusion, while its crash remains evidence
  of recipe sensitivity at the original no-input scope.
- s2286's trace-light Step 1 capture is a separate route-invalid observation:
  removing the VI-caller logger moved the port failure earlier, to
  `mat34CrossRowsAndCopyPos+60` / guest PC `0x800547BC` in the initial 640
  route. It does not establish a logger-induced crash, an audio-contract gap,
  or an image-arm defect. s2287's qualified retail oracle then recorded no
  execution of either exact crash PC, closing that boundary as port-only at
  the tested recipe scope.
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
