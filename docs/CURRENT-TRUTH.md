# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2329 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§47; the append-only ledger remains authoritative for exact commands, counts,
and probe rows.

Maintained in Session 2341 (2026-08-24). The file was compacted in s2330
after exceeding the 60,000-byte threshold; durable s2304–s2329 history moved
to §47. The s2341 synth parent/gate census moves the qualified M5 boundary
inside `musyxSynthFrame`: retail whole-RDRAM/target/status/title/hangar and all
named PC controls are positive, both port arms reached target phases with all
host/task/DMA/guest-receive/PCM/filter/render/key-on/callback controls, and a
same-helper callback control fired `144/145` times. The parent entry
`0x8009123C` fired `268` times in each arm, while all three countdown/gate
edges and the three retained sequencer callsite rows were zero in both arms.
The next work unit is the pre-gate branch census in `scratch/agent/NEXT.md`.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- The qualified route is `ROGUESQ_LLE_FORCE=1`,
  `ROGUESQ_SPIN_YIELD=1`, `ROGUESQ_LLE_UNGATED=1`, and
  `ROGUESQ_LLE_SOLO=1`; spin yield is gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation needs a named writer, legitimacy
  judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub for controls. The image arm does real DMEM
  work and generated DMA, then returns `Broke`; its host canary is probe data
  only. Stock `aspMain` is not this game's Factor 5 contract. MORT is a
  separate CPU speech asset.
- Both silent and image arms qualify through title `1024 @ 0x00790400` and
  hangar `512 @ 0x006AB400` at the tested recipe scope. Image-stage payloads
  rotate between captures; exact PCM source/consumer joins can occur, but the
  port has no valid same-ordinal slot, descriptor, voice/filter, or key-on
  transition. The s2332 capture had zero `output_buff`/size and zero
  output-overlap on both nonzero target stages, with one exact PCM
  source/consumer join and no post-stage lifecycle row. Its host-positive
  filter/voice span control fired in both arms, while the real port audit had
  zero filter/voice rows; retail independently executed the filter caller and
  callee in hangar. No writeback, address remap, consumer, slot, guard, or
  default change is authorized.
- The s2333 upstream census is qualified by retail whole-RDRAM, target-window,
  title/hangar, task/gate/status, and retail render/decode/filter/service
  controls. The port target scope has four `site=render-stage` rows and sixty
  key-on rows across the arms, but zero descriptor rows and zero real
  `[filter-voice-audit]` rows. Two lifecycle rows are prior-ordinal events;
  there is no same-ordinal post-stage lifecycle row. The requested retail
  `0x8009C4E8` execution count is explicitly zero on this route, while the
  other requested retail PCs are positive.
- The s2335 descriptor census is qualified by retail whole-RDRAM `32439063`,
  target-window `32428737`, mode/gate/status `108/17/22`, title/hangar, and
  retail render `85891`, descriptor `688`, trigger `688`, key-on
  `83628/2231`, filter caller/callee `6384/6384`, and requested-zero
  `0x8009C4E8`. Both port arms reached hangar and had task/DMA,
  guest-receive, PCM source/consumer, and host-positive controls. Each had
  target render-stage `5` and key-on activity, but init-writer events,
  `init-voice-sample` entry rows, descriptor payload events, and real filter
  rows were all `0`; the image arm had `2314` DMA-range rows. This is two
  independent port-side lines (unconditional lifecycle event census and the
  entry/filter audit) plus the retail witness, not a behavior-change result.
- The s2336 clean-tag callsite census is independently qualified by retail
  whole-RDRAM `32280738`, physical target window `32270412`, mode/gate/status
  `108/17/22`, title/hangar, retail entry/store/trigger `681/681/681`, key-on
  `83450/2231`, decode `1942`, filter caller/callee `6384/6384`, service
  `3911`, and explicit-zero `0x8009C4E8`. Both arms reached hangar with
  target-phase host controls at title `1024 @ 0x00790400` and hangar
  `512 @ 0x006AB400`; each had task/DMA/guest-receive/PCM/filter controls,
  target render `5`, and key-on `33`. Both direct callsite hooks and both
  `musyxInitVoiceFromSample` entry/store rows were zero. This selects
  H-PortInitNeverCalled at capture scope; it changes no behavior.
- The s2337 parent-caller census is independently qualified by retail
  whole-RDRAM `32431451`, physical target-window `32421125`, mode/gate/status
  `108/17/22`, title/hangar, retail caller/callsite `686/2` and `686/2`,
  descriptor/trigger `688/688`, key-on `83596/2231`, decode `1940`, filter
  caller/callee `6376/6376`, service `3914`, and requested-zero
  `0x8009C4E8`. Both same-build port arms reached hangar; each had host-positive
  controls at title and hangar, target render/key-on `5/33`, and positive
  task/DMA/guest-receive/PCM/filter controls. Both new caller-entry and
  pre-call marker pairs were `0/0`; retained direct-callsite and callee-entry
  rows were also `0/0`. This selects H-PortCallerInactive at capture scope;
  it changes no behavior.
- The s2338 parent-edge census is independently qualified by retail
  whole-RDRAM `32311011`, physical target-window `32300685`, mode/gate/status
  `108/17/22`, title/hangar, parent PCs
  `0x8008BC10/0x8008C454 = 43284/665` and
  `0x8009B5A8/0x8009B784 = 3905/2`, child/descriptor/trigger controls,
  key-on `83215/2231`, decode `1944`, filter caller/callee `6389/6388`, and
  requested-zero `0x8009C4E8`. Both same-build sequential port arms reached
  hangar. Each had target-phase host, task, DMA, guest-receive, PCM, filter,
  render, and key-on controls; both new parent entry/pre-call pairs, retained
  child entry/pre-call pairs, direct callsites, and callee-entry rows were
  zero. Two earlier captures were rejected as classifier-only coverage
  failures: one cleared width/origin on metadata-only phase lines, and one
  used prefixed retail keys; the fixed run selected H-PortParentInactive.
- The s2339 scheduler/callback census is independently qualified by a fresh
  retail oracle: whole-RDRAM `32662007`, target-window `32651783`, mode/gate/
  status `108/17/22`, callback registration `19`, and positive retail PCs
  `0x8008C9AC/0x8008CA14/0x80019B74/0x8009B5A8 = 4221/43383/12796/3912`,
  with requested-zero `0x8009C4E8`. In the fixed same-build sequential arms,
  all positive controls qualified (`port_controls=1`); scheduler entry and
  pre-call rows were `0/0` in both arms, while callback dispatch rows were
  `8` stub and `48` image. Those dispatches targeted `0x80003250` and
  `0x8009123C`, never `0x8009B5A8`. This selects H-PortSchedulerParentInactive
  at capture scope and moves the active boundary above `tickAllAudioChannels`.
- The s2340 scheduler-caller census is independently qualified by a fresh
  retail oracle: whole-RDRAM `32449224`, target-window `32438879`,
  mode/gate/status `108/17/22`, callback registration `19`, title/hangar, and
  positive retail PCs `0x8008D960/0x800914A4/0x80091564/0x80091618 =
  4224/3717/334/173`, retained scheduler `0x8008C9AC/0x8008CA14 =
  4224/43504`, callback/service `0x80019B74/0x8009B5A8 = 12806/3916`, with
  requested-zero `0x8009C4E8`. Both same-build sequential arms reached
  hangar and passed the retained task/DMA/guest-receive/PCM/filter/render/
  key-on controls. The new helper positive control at `0x80019B74` fired
  `144` stub and `145` image rows. New `tickAudioSequencerFrame` entry and
  callsite rows were `0/0` for entry and each of
  `0x800914A4/0x80091564/0x80091618` in both arms; retained scheduler
  entry/pre-call rows were also `0/0`. This selects H-PortSeqCallerInactive
  at capture scope and changes no behavior.
- The s2341 synth parent/gate census is independently qualified by a fresh
  retail oracle: whole-RDRAM `32450863`, target-window `32440518`, mode/gate/
  status `108/17/22`, callback registration `19`, both target origins, and
  positive retail PCs for `0x8009123C`, all three gate PCs, all three
  callsites, retained scheduler/callback/service sources, and descriptor/
  filter controls; requested-zero `0x8009C4E8` stayed zero. Both same-build
  arms reached hangar with `port_controls=1`; task/DMA/guest-receive/PCM/
  filter/render/key-on controls were positive, and the callback helper
  control fired `144/145` times. The port parent entry fired `268/268`, but
  gate 1/2/3 and callsite 1/2/3 were `0/0` in both arms. This selects
  H-PortSynthGateBypassed at capture scope and changes no behavior.
- The independent retail oracle is the witness for game-side memory claims.
  Whole-RDRAM, title/hangar, gate/task/status, target-window, and named-PC
  controls must pass before a retail null is interpreted. It reaches attract,
  title, and hangar, not a mission.
- Generated-symbol renaming is closed at the useful boundary. Do not recensus
  or invent names for `func_8000040C`, `func_800927B0`, `func_80092A54`,
  `func_80092CF0`, or `func_800E9AE0`.

## Latest evidence

- **s2340 — sequencer caller census selects H-PortSeqCallerInactive.** The
  fresh retail preflight passed whole-RDRAM `32449224`, target-window
  `32438879`, mode/gate/status `108/17/22`, callback registration `19`,
  title/hangar, and positive PCs
  `0x8008D960/0x800914A4/0x80091564/0x80091618 = 4224/3717/334/173`,
  retained scheduler `0x8008C9AC/0x8008CA14 = 4224/43504`, and
  callback/service `0x80019B74/0x8009B5A8 = 12806/3916`; `0x8009C4E8`
  remained explicitly zero. Both same-build sequential arms reached hangar
  with task/DMA/guest-receive/PCM/filter/render/key-on controls positive.
  The new helper’s live callback control fired `144` stub and `145` image
  rows. The new sequencer entry and all three static callsite rows were zero
  in both arms, while retained scheduler entry/pre-call rows stayed zero.
  This selects H-PortSeqCallerInactive at capture scope and authorizes no
  behavior change.

- **s2337 — enclosing caller reachability selects H-PortCallerInactive.** The
  retail preflight passed whole-RDRAM `32431451`, target-window `32421125`,
  mode/gate/status `108/17/22`, title/hangar, caller/callsite `686/2` and
  `686/2`, descriptor/trigger `688/688`, key-on `83596/2231`, decode `1940`,
  filter caller/callee `6376/6376`, service `3914`, and explicit-zero
  `0x8009C4E8`. Both same-build sequential port arms reached hangar; target
  host controls fired at title and hangar, with render/key-on `5/33` and
  task/DMA/guest-receive/PCM/filter controls in each arm. New entry/pre-call
  rows were `0/0` for both callers in both arms; retained direct-callsite and
  callee-entry rows were also `0/0`. This selects H-PortCallerInactive at
  capture scope and authorizes no behavior change.

- **s2336 — explicit callsite provenance selects H-PortInitNeverCalled.** The
  clean-tag ground-truth-first oracle passed whole-RDRAM `32280738`, physical
  target-window writes `32270412`, mode/gate/status `108/17/22`, title/hangar,
  and retail execution counts entry/store/trigger `681/681/681`, key-on
  `83450/2231`, decode `1942`, filter caller/callee `6384/6384`, and service
  `3911`; `0x8009C4E8` was explicitly zero. Both same-build sequential port
  arms reached the target title and hangar phases. The host-positive control
  fired in each arm at both `1024 @ 0x00790400` and `512 @ 0x006AB400`.
  Each arm had target render `5`, key-on `33`, task/DMA/guest-receive/PCM,
  and filter controls; both explicit callsite hooks (`0/0`) and both
  `musyxInitVoiceFromSample` entry/store rows (`0/0`) were zero. This selects
  H-PortInitNeverCalled at capture scope and rules out an unqualified logger
  or phase-control failure; it authorizes no behavior change.

- **s2333 — upstream voice census leaves descriptor-to-filter boundary open.**
  The corrected ground-truth-first oracle passed whole-RDRAM `32475857`,
  physical target-window `32465531`, mode/gate/status controls, title/hangar,
  and retail execution counts render `85808`, decode `1930`, filter `6336`,
  and service `3915`; the requested `0x8009C4E8` PC was explicitly zero.
  Both sequential port arms passed hangar, task ABI/DMA/guest-receive, and the
  host-positive filter audit. The phase-10 image table had two nonzero rows.
  Across both arms, target render-stage was `4`, key-on was `60`, descriptor
  was `0`, real filter audit was `0`, same-ordinal post lifecycle was `0`,
  and prior-ordinal lifecycle was `2`. This **refutes** H-UpstreamVoiceAbsent
  at capture scope, but does not select H-FilterPathGated because its required
  descriptor control is absent; H-PriorOrdinalReuse is not selected because
  no real filter row exists. The next boundary is render/key-on to descriptor
  entry/writer to filter call.

- **s2332 — output metadata remains absent; filter/voice consumer is rejected
  at capture scope.** The corrected ground-truth-first oracle passed
  whole-RDRAM `32376430`, physical destination-window `32366283`,
  task/output/gate/status/wait `108/17/22/0`, title/hangar, named writer PCs,
  and the filter-path control: retail executed `0x8009D740` `6360` times and
  `filterVoiceSampleBlock` `0x8009D7D0` `6351` times. Both sequential port arms
  passed route, VI, ABI/DMA, guest-receive, PCM, and image controls. The phase-10
  image table had `872` rows and two nonzero rows; both had
  `output_buff=0`, `output_buff_size=0`, and zero output overlap. One had an
  exact PCM source/consumer join (`6447 -> 6448`), neither had a post-stage
  lifecycle row, and both retained the six-row prior signature. The new
  host-positive span control fired `1/1`, but the real port filter/voice audit
  emitted `0/0` rows. This selects `H-OutputBuffZero` and rejects
  `H-FilterVoiceConsumer` at capture scope; it does not identify the missing
  same-ordinal consumer or authorize a behavior change.

- **s2331 — output metadata is absent at capture scope.** The corrected
  ground-truth-first oracle passed whole-RDRAM `32387920`, physical
  destination-window `32377773`, task/output/gate/status/wait `108/17/22/0`,
  title/hangar, and the named writer-PC controls. The sequential same-build
  stub/image arms both reached hangar and retained task/DMA/guest-receive/PCM
  controls. The phase-10 image table had `895` stage rows and two nonzero
  rows: both advertised `output_buff=0`, `output_buff_size=0`, and all five
  generated DMA ranges had `output_overlap=0`; one row had an exact PCM
  source/consumer join, neither had a post-stage lifecycle row, and both had
  the prior six-row lifecycle signature. This selects `H-OutputBuffZero` at
  capture scope and leaves the destination-to-slot/key-on boundary open.
  The filter/voice positive control remained absent and unevaluable. The
  initial concurrent launcher was invalid because its two arms did not both
  reach hangar; the final sequential driver is the qualified result.

- **s2329 — metadata boundary remains open.** The corrected same-run oracle
  passed whole-RDRAM `32351889`, physical destination-window writes
  `32341742`, task/output/gate/status/wait `108/17/22/0`, title/hangar, and all
  named writer-PC controls. Both port arms had route, VI, ABI/DMA,
  guest-receive, and PCM controls. The image arm had `2323` image-stage and
  `2327` image-join rows. Two nonzero target destinations both had exact PCM
  source/consumer joins, while six lifecycle rows belonged to the prior route
  and no same-ordinal post-stage slot, descriptor, or key-on row existed. This
  selects `H-EarlierTickOnly` at capture scope and makes destination polarity
  capture-dependent. The next boundary is task metadata/output overlap.
- **s2328 — drain A/B qualified.** After fixing the launcher gate, both image
  arms qualified through title/hangar with task/DMA/image/PCM and guest-receive
  controls; normalized target lifecycle tables matched and retained the same
  prior-route signature. The drain toggle did not select the missing consumer.
- **s2327 — ordinal ownership.** The target image task and PCM contract were
  live, while the observed five slot stores and sentinel key-on row were
  stamped to the prior audio ordinal. This rules out same-task ownership of
  those pre-events at capture scope; filter/voice absence remained
  unevaluable because its positive control did not fire.
- **s2324–s2326 — image arm is live.** Same-build stub/image controls showed
  real image DMEM changes, generated DMA, nonzero stage payloads, and
  occasional exact PCM publication in the image arm; the stub remained the
  silent control. Neither arm supplied a valid downstream slot/key-on
  transition. The stage-only/PCM destination split is not route-wide stable.
- **s2320–s2323 — retail status lifecycle.** Ground truth independently found
  target writes at `0x00154620`, owned by the named writer pairs, and repeated
  `01 -> 02 -> 03 -> 00` cycles. This closes retail status semantics but not
  the port contract.
- **s2310–s2319 — retail and route controls.** The fifteen-origin retail
  writer census had positive lifetime/final-ring controls but no phase-attributed
  writer row in configured buckets. The repaired route then qualified both
  port arms with positive task/DMA/PCM controls while slot allocation,
  descriptor, and valid key-on rows stayed absent.

## Active backlog

Closed investigations are not active work items. This is one monotonic
sequence; #1 is the next work unit.

1. **M5 audio de-stubbing — active.** `docs/M5-AUDIO-PLAN.md` is the design
   gate and inventories live stubs, traps, gates, and the incremental
   task→DMA→service→slot→voice→PCM validation sequence. Continue only with a
   ground-truth-first, positive-control-qualified step.
2. **M5 scheduler/callback source reachability — next.** s2341 selected
   H-PortSynthGateBypassed: `musyxSynthFrame` entry `0x8009123C` is positive
   in both port arms, but its three countdown/gate edges and all three
   sequencer callsites are zero under the same positive controls. Census the
   pre-gate branches at `0x8009142C`, `0x80091454`, and `0x80091468` in one
   table to distinguish outer-loop rejection, per-iteration guard bypass, and
   a gate-reached probe mismatch. Keep retail source-PC controls, callback
   registration, all s2338–s2341 rows, target route/task/DMA/guest-receive/
   PCM/filter/render/key-on controls, and both arms; do not add behavior.
3. **M5 A1 second-origin transition — parked.** Resume only with a new
   discriminator restoring `0x00696100`/`0x00696600` coverage; do not repeat
   the failed four-arm/two-wave matrix.
4. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator; do not chase a single recurring crash.
5. **Hangar visual artifact — parked.** Malformed-triangle H2 and consumer
   mode H1 are refuted. H3 is unavailable because the oracle cannot screenshot
   the LLE path; do not repeat the capped `0xD60` scan.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route table selects `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches
title and hangar, `01` reaches title only, and `10`/`00` reach neither. Menu
spin yield is a diagnostic route aid, not a default behavior change. Factor 5
command mappings and independent-ground-truth requirements live in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). Read those before
reasoning about a DL/RDP anomaly; the runtime cannot witness its own null.

### M5 audio and image output

Direct service entry/exit, the service gate/loop, and task/AI boundary are live
on the port. Retail independently matches a complete slot-0 status cycle at
`0x00154620`; this does not establish the port key-on contract. The image arm
changes DMEM, completes, emits generated DMA, and can publish a nonzero PCM
join. Its target destinations and stage/consumer polarity rotate by capture.
The s2331 metadata table found zero `output_buff`/size and zero output overlap
on every generated range for both nonzero target stages; one stage had an exact
PCM source/consumer join. The six lifecycle rows observed before target output
are assigned to the prior audio ordinal, and no post-stage lifecycle row was
present. The s2332 host-positive span control fired in both arms, but the real
port filter/voice audit emitted zero rows while retail independently executed
the caller/callee in hangar. The s2333 census then found target render-stage
and key-on rows but zero descriptor and real filter rows; s2335 added an
unconditional init-writer event and an independent function-entry probe, both
zero in both arms, while the same-run host-positive filter controls fired.
Retail independently executed the descriptor, trigger, key-on, and filter PCs.
The s2336 callsite census then added explicit hooks immediately before both
static `jal` sites and retained phase-qualified host controls; both callsites
and both entry/store probes remained zero in both arms. The s2337 census added
target-phase entry and pre-call markers to both enclosing callers; all four
remained zero while the same-run host controls, target render/key-on rows, and
retained callsite/callee controls were positive. The s2338 parent census then
added entry and pre-call markers for both parent edges; those four were also
zero in both arms under the same qualified controls. This selects
H-PortParentInactive at capture scope and moves the active boundary above both
  parent functions; no store, guard, or consumer change is authorized. The
  s2339 scheduler/callback census then found zero `tickAllAudioChannels`
  entry/pre-call rows in both arms despite positive task/DMA/PCM and callback
  controls; the VI dispatcher fired only to `0x80003250`/`0x8009123C`, not the
  registered service target. This refines the active boundary above the
  scheduler and leaves callback target selection unresolved; no store, guard,
  or consumer change is authorized.
  The s2340 sequencer census then found the entry and all three static caller
  edges also zero under a same-helper positive control; the active boundary is
  now above `tickAudioSequencerFrame`, with the `musyxSynthFrame` parent/gates
  as the next measured edge. The s2341 census found
  `musyxSynthFrame` entry `0x8009123C` positive `268/268`, but its three
  countdown/gate edges and all three sequencer callsites zero in both arms
  under the same qualified controls. This selects H-PortSynthGateBypassed and
  moves the active boundary inside `musyxSynthFrame`, before the first
  observed countdown branch; no gate, state, store, or consumer change is
  authorized.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-VI arms recover the
split, but the natural host publisher and cadence are unidentified. The A1
matrices were route-invalid and do not select a VI arm.

### Key-on, M3, and M4

Retail reaches the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with divisor
`0xC0` and no guard hits. Exact `(origin,width,PC)` tuple buckets differ in
both directions; the common cross-runtime pointer/source/state witness is not
restored. The `-0x25A4` pointer-chase, six-site PIC, ten-site audio-slot,
slot-dispatch, two-line overlay-move, and leftover `fake_func_*` size-class
audits are closed at their stated scopes.

## Superseded conclusions

These were believable before qualified route and independent controls, but
are superseded at their measured scopes:

- The old overlay/menu explanation, intrinsic 640 flakiness, missing
  input/wait-return claims, and unqualified PCM-null claims.
- Clean-stub, canary-poison, final-E50, uniform-gate, host-isolator, and
  global-zero image-DMA explanations.
- s2190–s2197 second-origin/caller explanations and s2283/s2284 A1 matrices;
  both were coverage artifacts and do not identify a VI publisher.
- s2228 and s2242–s2259 image/pair crash splits; they were intermittent route
  loads, not intrinsic image or writer defects.
- s2288's stub-first route conclusion and s2286's logger-removal explanation;
  explicit input qualified both arms, while logger removal changed timing but
  did not restore the route.
- s2320's broad retail zero-only result and s2321's target-absence result;
  later requested-writer/status tables found target `01/02` stores and
  complete `01 -> 02 -> 03 -> 00` cycles.
- s2304's route-wide same-ordinal PCM gap, s2307's fixed target addresses,
  s2308's retail-normal zero-fill interpretation, and s2325's destination-role
  split; later captures showed temporal joins, rotating destinations, an
  independent retail nonzero ring, and two exact PCM joins.
- s2331's statement that the filter/voice null was unevaluable; s2332 added a
  labeled host-positive span control and showed the real port audit still had
  zero rows, while an independent retail run executed the caller and callee.
- s2335's H-DescriptorWriterAbsent label is refined by s2336: it was believable
  because the unconditional writer and downstream entry probes were both zero,
  but explicit hooks at both static callsites also stayed zero under fresh
  target-phase controls. The measured boundary is therefore caller reachability,
  not yet a missing descriptor writer inside the callee.
- s2336's H-PortInitNeverCalled label is refined by s2337: it was believable
  because the direct callsite and callee-entry probes were zero under live
  target controls, but the new enclosing-caller entry and pre-call probes also
  stayed zero in both arms. The measured boundary is now above both child
  callers, not a callsite instrumentation fault or a callee branch.
- s2337's H-PortCallerInactive label is refined by s2338: it was believable
  because both child caller entries and pre-call edges were zero under live
  target controls, but the new enclosing parent entries and pre-call markers
  were also zero in both arms. The measured boundary is now above both parent
  functions, not a child callsite, callee, or descriptor-store issue.
- s2338's H-PortParentInactive label is refined by s2339: it was believable
  because both parent entries and pre-call edges were zero under live controls,
  but the next `tickAllAudioChannels` entry and edge were also zero in both
  arms. The VI dispatcher was independently active, yet selected only
  `0x80003250`/`0x8009123C`; the measured boundary is now above the scheduler,
  while the registered service-target path remains unproven.
- s2339's H-PortSchedulerParentInactive label is refined by s2340: it was
  believable because the scheduler entry and edge were zero under live
  callback controls, but the next `tickAudioSequencerFrame` entry and all
  three static callsites were also zero under a same-helper positive control.
  The measured boundary is now above the sequencer, not a generated direct
  call mismatch or an internal sequencer branch.
- s2340's H-PortSeqCallerInactive label is refined by s2341: it was believable
  because the sequencer entry and all three callsites were zero under live
  controls, but the next `musyxSynthFrame` entry fired `268/268` in the same
  arms while all three internal gate edges remained zero. The measured
  boundary is now inside `musyxSynthFrame`, before its first observed gate,
  not an inactive parent or generated sequencer dispatch.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical and phase-gated by
  VI callbacks.
- A null requires a same-run positive control. Batch all counters and A/B arms
  in one build/run, scope budgets to the phase, and use VI gates rather than
  elapsed time for animated scenes.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM present.
  Capture paths must not start with `.` in the final component.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
