# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2329 is summarized in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§47; the append-only ledger remains authoritative for exact commands, counts,
and probe rows.

Maintained in Session 2349 (2026-08-24). The file was compacted in s2330
after exceeding the 60,000-byte threshold; durable s2304–s2329 history moved
to §47. The s2343 B40 provenance census passed fresh retail whole-RDRAM,
target-window, mode/status/title/hangar, named-PC, and both-arm port controls.
The retail post-store witness recorded `0x8008EC88` writing nonzero
`0x01000000` in width-1024 and width-512 target-like phases. Both port arms
recorded the same writer with requested `1` but stored `0`; 254 of 262
`0x80091468` rows joined through `writer_seq`, and the eight unmatched rows
were the explicit pre-writer prefix. Every joined branch had `lhs=0` and took
the bypass target. This selects H-PortWriterMismatch at capture scope; no
writer or consumer was changed.

The s2344 C88 treatment validation then passed fresh retail controls and all
four same-build port arms. With `ROGUESQ_M5_C88_VALUE=0`, all three target
writer rows stored zero and all 131 sampled `0x80091468` branches read zero
and took the bypass. With `=1`, two of three writer rows stored nonzero,
125/131 stub and 128/131 image branch rows read nonzero and fell through, and
target key-on normal-tail/slot-02/slot-00 plus real filter rows appeared.
PCM source/consumer counts remained `88/88` in every arm and voice-event rows
remained zero. This selects H-C88GateNotSufficient_PCMVoiceContractStillOpen
at capture scope; the treatment remains opt-in and no default writer change
was made.

The s2345 C88 downstream ordinal join passed the same fresh retail controls and
all four same-build port arms. C88=1 stored nonzero in `2/3` writer rows and
produced `125/126` writer-joined fall-through branches. Exact route-ordinal
rows in both C88=1 arms included key-on/slot and descriptor-init events, while
both had `0` exact PCM source joins, `0` exact PCM consumer joins, and `0`
completed image-task joins. Target-phase filter audit rows were `256` in each
C88=1 arm and `0` in each control, but that logger is phase-scoped rather than
ordinal-keyed. Image-task rows remained stage-only. This selects
H-TaskOutputGap at capture scope; it does not authorize a writer, consumer,
task-data, or default change.

The s2346 task-output provenance census passed the fresh retail whole-RDRAM,
target-window, status/queue, title/hangar, and named-PC controls, then all
four same-build C88/audio port arms. In both C88=1 arms, 99 completed task
rows had `output_buff=0` and `output_buff_size=0`; the image arm emitted 3,689
generated DMA ranges with zero output overlap and 200 stage rows classified
stage-only. C88=1 still stored nonzero in `2/3` writer rows, produced
125 fall-through branches in the image arm, and produced `256` filter rows;
PCM boundary controls remained positive. This selects
H-OutputMetadataWriterAbsent at capture scope. The direct sequence-keyed PCM
rows do not prove task publication because the independent image join has no
source/consumer match and all output overlap is zero. No writer, task-data,
consumer, default, or guard change was made.

The s2347 output-writer provenance census passed a fresh retail whole-RDRAM
watch (`29,920,648`), target-window watch (`29,910,488`), output-span watch
(`108`), B40/status/queue watches (`17/16/19`), both title/hangar phases, and
the named-PC controls. The retail output-span writer was `0x80094648`, with
`24` phase-bucketed writes at each target origin and `72` nonzero post-value
samples. The corrected same-build four-arm port table passed every title,
hangar, task/DMA, guest-receive, PCM, filter, render, key-on, and callback
control. C88=1 stored nonzero in `2/3` B40 control rows and increased
fall-through rows, while every arm's ABI output fields remained zero; image
C88=0/1 emitted `2,299/3,752` target-phase DMA ranges and both had `0`
output-overlap ranges. This selects H-RetailOutputWriterPortZero at capture
scope and refines H-OutputMetadataWriterAbsent. The retail writer's semantic
relation to the port output ABI and any port write-before-snapshot ordering
remain open; no writer, writeback, task-data, consumer, default, or guard
change was made.

The s2348 output-field semantic/order census first exposed a phase-gate
classifier issue: the requested retail origins produced no field rows because
the live `0x80094648` writer ran at `0x00790800`/`0x006AB800`. A single fixed
oracle run armed all four observed origin variants and passed whole-RDRAM
`10121`, output-span `82`, B40/status/queue `14/10/15`, both target phases,
and the named-PC controls. It produced 128 field rows, 24 writer rows per
target-equivalent phase, 48 nonzero post-value samples per port phase, and
only `0x00141AD8..0x00141AEC` destinations. The field rows had
`s0=0x801B4E40/0x801DDB90` and source words `0x0/0x9600`; no row identified
the writer as a `data_ptr+0x100` field.

The first same-build port attempt was rejected by its own arm predicate: the
silent stub has no DMA observer rows and one stub arm crashed during
retention. The fixed run added a task-field snapshot control and made the
generic DMA-observer control image-arm-specific. All four arms then passed
title/hangar, task/DMA/guest-receive/PCM, filter, render, and C88 fall-through
controls; each had zero `audtask-field-write` rows and zero pre/post changes
at its computed `data_ptr+0x100`. This selects
H-RetailWriterSentinelUnrelated at capture scope and closes the
`0x80094648` candidate-writer sub-boundary. The actual retail
`data_ptr+0x100` writer boundary remains open. No writer, writeback, task-data,
consumer, default, or guard changed.

The s2349 `data_ptr+0x100` writer census passed fresh retail whole-RDRAM
`56,453`, target-window `44,120`, named-PC `0x800078EC` `11,039,031`, exact
field-watch totals `490/1,735`, and title/hangar phase controls. Retail's
`0x80090CA4` produced `482` phase-matched writer executions and `256` exact
post-value rows at each of `0x00173C20` and `0x00171DE0` in the canonical
1024/title phase; the `0x00173C20` rows used the observed `+0x400` origin
variant. It produced no phase-matched `0x80090CA4` writer or exact post-value
row in the 512/hangar phase; that phase instead attributed `0x00171DE0` to
`0x800908D4`, `0x8009081C`, and `0x80090810`, with no phase writer row for
`0x00173C20`. All four same-build port arms passed title/hangar, task/ABI,
guest-receive, PCM, field-snapshot, image-DMA, filter, render, key-on, and
C88 controls. Both C88=1 arms had zero `audtask-field-write` events and zero
field changes. This selects H-RetailKnownDestNotAudioOutput at capture scope
and closes `0x80090CA4` as a universal writer candidate; the actual hangar
writer/task relation remains open. No writer, writeback, task-data, consumer,
default, or guard change is authorized.

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
- The s2343 B40 census adds a regeneration-safe target-phase `writer_seq`
  join from all seven `0x800A0F50` writer rows to the existing
  `0x80091468` branch rows. Retail's `0x8008EC88` store is independently
  positive and writes `0x01000000`; both port stub/image arms request `1` but
  store `0`, then read `lhs=0` and take the bypass. This selects
  H-PortWriterMismatch at capture scope. The pre-writer rows are not a
  classifier failure, and no behavior change is authorized by this result.
- The s2344 opt-in treatment is the first qualified C88 behavior arm. Retail
  independently confirms the legitimate nonzero C88 store; the port treatment
  restores the gate branch and unlocks intermediate key-on/slot/filter work,
  but does not add a same-run PCM or voice-event transition. This is progress
  at the gate boundary, not a complete audio contract or permission to promote
  the store.
- The s2345 table refines the C88 boundary. Both treatment arms have exact
  route-ordinal key-on/slot and descriptor-init rows, and the image arm has
  task-stage rows, but neither treatment has an exact PCM source/consumer or
  completed task join. Filter evidence is positive only at target-phase scope,
  because its existing audit row has no route ordinal. The remaining measured
  boundary is task output/publication, not C88 readback or a proven consumer
  mismatch; no writer, consumer, task-data, or default change is authorized.
- The s2346 table refines task output/publication to absent output metadata at
  capture scope. The image C88=1 treatment completed 99 joined tasks and
  emitted 3,689 generated DMA ranges, but every joined ABI row advertised
  zero output buffer and size, every range had zero output overlap, and all
  200 image-stage rows were stage-only. The sequence-keyed PCM rows remain
  non-authoritative without an output/destination match. This selects
  H-OutputMetadataWriterAbsent and authorizes no writer or task-data change.
- The s2347 table adds the independent retail writer witness. Retail writes
  the watched task/output span from `0x80094648` in both target phases, while
  all four qualified port arms expose zero ABI output fields; the image arms
  emit `2,299/3,752` target-phase DMA ranges with zero output overlap. The
  C88 writer sequence remains only a treatment control (`2/3` nonzero in each
  C88=1 arm), not an output-field writer. This selects
  H-RetailOutputWriterPortZero at capture scope, leaves the writer's semantic
  mapping and port ordering open, and authorizes no behavior change.
- The s2348 table closes the candidate-writer sub-boundary. The fixed
  four-origin retail oracle passed whole-RDRAM `10121`, output-span `82`,
  B40/status/queue `14/10/15`, named PCs, and produced 128 field rows plus
  24 `0x80094648` rows in each observed title/hangar-equivalent origin. The
  post-value writer addresses were only `0x00141AD8..0x00141AEC`, while the
  field rows exposed `s0=0x801B4E40/0x801DDB90` and source words `0x0/0x9600`,
  not a `data_ptr+0x100` relation. The corrected same-build four-arm port
  table passed all existing controls plus task-field snapshot/observer
  controls; every computed `data_ptr+0x100` pre/post pair was unchanged,
  every field-write event was absent, and no DMA range overlapped the field.
  This selects H-RetailWriterSentinelUnrelated at capture scope. The
  `0x80094648` writer is not a proven output-field writer; the actual retail
  `data_ptr+0x100` writer remains the next M5 contract boundary. No writer,
  writeback, task-data, consumer, default, or guard change is authorized.
- The s2349 table tested the already observed `0x80090CA4` writer against the
  two exact task-field destinations. Retail positively joined that writer to
  both fields only in the 1024/title phase; at 512/hangar, `0x80090CA4` was
  absent and `0x800908D4/0x8009081C/0x80090810` wrote only the `0x171DE0`
  watch. The four port arms remained unchanged at every computed
  `data_ptr+0x100`. This selects H-RetailKnownDestNotAudioOutput at capture
  scope, closes the `0x80090CA4` candidate as a universal writer, and leaves
  the actual hangar writer boundary open. No behavior change is authorized.
- Both silent and image arms qualify through title `1024 @ 0x00790400` and
  hangar `512 @ 0x006AB400` at the tested recipe scope. Image-stage payloads
  rotate between captures; exact PCM source/consumer joins can occur. In the
  C88=0 controls the older no-slot/descriptor/key-on null remains; in the
  opt-in C88=1 treatment, s2345 found same-ordinal key-on/slot and
  descriptor-init rows but no same-ordinal PCM source/consumer or completed
  task join. The s2332 capture had zero `output_buff`/size and zero
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
- The s2342 pre-gate census is independently qualified by a fresh retail
  oracle: whole-RDRAM `32459193`, target-window `32448848`, mode/gate/status
  `108/17/22`, callback registration `19`, both target origins, and positive
  retail execution counts for `0x8009123C/0x8009142C/0x80091454/0x80091468`
  of `4427/4421/7423/7423`; requested-zero `0x8009C4E8` stayed zero. Both
  same-build arms passed retained task/DMA/guest-receive/PCM/filter/render/
  key-on controls plus the `0x80019B74` helper control (`144` each). Parent
  entry was `268/268`; sampled pre-gate rows were stub/image `131/131/131`
  per site, with taken outcomes at `0x8009142C` of `10/5`, `0x80091454` of
  `2/1`, and `0x80091468` of `131/131`. The three retained gate edges and
  sequencer callsites were `0` in both arms. This selects
  H-PortPreGateB40Reject at capture scope and changes no behavior.
- The independent retail oracle is the witness for game-side memory claims.
  Whole-RDRAM, title/hangar, gate/task/status, target-window, and named-PC
  controls must pass before a retail null is interpreted. It reaches attract,
  title, and hangar, not a mission.
- Generated-symbol renaming is closed at the useful boundary. Do not recensus
  or invent names for `func_8000040C`, `func_800927B0`, `func_80092A54`,
  `func_80092CF0`, or `func_800E9AE0`.

## Latest evidence

- **s2349 — `0x80090CA4` is title-only, not the universal task-field writer.**
  The fresh retail oracle passed whole-RDRAM `56,453`, target-window `44,120`,
  named-PC `0x800078EC` `11,039,031`, exact field-watch totals `490/1,735`,
  and both target phases. In the canonical 1024/title bucket, including its
  observed `+0x400` origin variant, `0x80090CA4` had `482` phase-matched
  executions and `256` exact post-value rows for each field
  (`0x00173C20` and `0x00171DE0`). In the 512/hangar bucket it had no
  phase-matched row; `0x00171DE0` instead attributed to
  `0x800908D4/0x8009081C/0x80090810`, and `0x00173C20` had no phase writer
  attribution. All four same-build port arms passed the full task, PCM,
  field-snapshot, image-DMA, filter, render, key-on, and C88 controls. Both
  C88=1 arms had zero field-write events and zero pre/post changes. This
  selects H-RetailKnownDestNotAudioOutput at capture scope and closes
  `0x80090CA4` as a universal writer candidate; the actual hangar writer
  remains open. The table is in
  `scratch/agent/s2349_m5_dataptr100_writer/`; no behavior changed.

- **s2348 — the retail output-span writer is unrelated to the port task field.**
  The first oracle field gate missed the live origins and was rejected as a
  classifier failure. The fixed four-origin run passed whole-RDRAM `10121`,
  output-span `82`, B40/status/queue `14/10/15`, both target-equivalent
  phases, and all named-PC controls. It recorded 128 `pc-field` rows, 24
  `0x80094648` writer rows per observed title/hangar-equivalent origin, 48
  nonzero post-value samples per port phase, and only
  `0x00141AD8..0x00141AEC` destinations; the field rows exposed
  `s0=0x801B4E40/0x801DDB90` and source words `0x0/0x9600`.
  The first same-build port attempt was rejected because its silent-arm
  observer predicate required impossible DMA rows and one stub arm crashed
  during retention. After adding a task-field snapshot control and making the
  generic DMA-observer control image-only, the fixed four-arm run passed all
  title/hangar, task/DMA/guest-receive/PCM, filter, render, and C88 controls.
  Every arm had zero `audtask-field-write` rows, zero pre/post changes at its
  computed `data_ptr+0x100`, and zero DMA overlap. This selects
  H-RetailWriterSentinelUnrelated at capture scope. The table is in
  `scratch/agent/s2348_m5_output_field_semantics/`; no behavior changed.

- **s2347 — retail output-span writer is positive while port ABI output stays zero.**
  The fresh retail oracle passed whole-RDRAM `29,920,648`, target-window
  `29,910,488`, output-span `108`, B40/status/queue `17/16/19`, both
  title/hangar phases, and the requested named PCs. The output-span writer
  histogram identified `0x80094648` with `24` writes in each target phase;
  its post-value witness had `72` nonzero samples. The first port parser was
  corrected because individual DMA-range rows inherit phase from their
  preceding `audtask-dma-row`; the fixed same-build sequential run qualified
  all four arms with the full title/hangar, task/DMA, guest-receive, PCM,
  filter, render, key-on, and callback-helper controls. Every arm was
  SIGKILLed with rc `137`, with no crash or abort marker. C88=1 stored nonzero
  in `2/3` B40 writer rows and had fall-through rows `382` stub and `373`
  image, versus `256/255` in their controls. All four arms had zero nonzero
  ABI output fields; image C88=0/1 emitted `2,299/3,752` target-phase DMA
  ranges with zero output-overlap ranges. This selects
  H-RetailOutputWriterPortZero at capture scope. The corrected table is in
  `scratch/agent/s2347_m5_output_writer_provenance_fixed/`, and no behavior
  change was made.

- **s2346 — C88 treatment reaches task completion, but output metadata is absent.**
  The fresh retail oracle passed whole-RDRAM `32,515,250`, target-window
  `32,505,084`, B40/status/queue `17/22/19`, both title/hangar phases, and the
  requested named PCs. The post-value witness saw `0x8008EC88` store
  `0x01000000` twice and the neighboring writers store zero. The first driver
  attempt stopped on a shell nounset bug; the first parsed run was rejected
  because its control predicate incorrectly required stub DMA-range rows; a
  second parsed run was rejected because route ordinal was used as the task
  `n`. The fixed same-build sequential run qualified all four arms with
  title/hangar, task/DMA, guest-receive, PCM, filter, render, key-on, and
  callback-helper controls; all arms were SIGKILLed with rc `137` and no
  crash/abort marker. Its table is in
  `scratch/agent/s2346_m5_task_output_provenance_joinfixed/`.
  C88=1 stored nonzero in `2/3` writer rows and had fall-through branch rows
  `121` stub and `125` image. The image C88=1 arm had `99` completed tasks,
  `990` task rows, `3,689` DMA ranges, zero output-overlap ranges, `200`
  image-stage rows, zero image-join source/consumer rows, and `99/99`
  sequence-keyed PCM rows (30 nonzero); the ABI output buffer and size were
  zero in all 99 completed joined rows. This selects
  H-OutputMetadataWriterAbsent at capture scope and leaves the writer's
  retail/port provenance open. No behavior change was made.

- **s2345 — C88 opens same-ordinal voice work, but task output/publication remains open.**
  The fresh retail oracle passed whole-RDRAM `32,359,524`, target-window
  `32,349,358`, B40/status/queue `17/22/19`, both title/hangar phases, and the
  requested named PCs. Retail's post-value watch saw `0x8008EC88` write
  `0x01000000` twice, while `0x8008EB7C` and `0x8008ED48` wrote zero in the
  target-like rows. The new launcher was initially absent; after repairing it,
  the Debug build passed and all four sequential port arms passed the same-run
  title/hangar, task/DMA, guest-receive, PCM, filter, render, key-on, and
  callback-helper controls. Every arm was intentionally SIGKILLed after the
  hangar retention window with rc `137` and no crash/abort marker.
  The phase/ordinal table recorded C88=1 writer nonzero `2/3`, fall-through
  branches `126` stub and `125` image, same-ordinal key-on/slot joins `122/118`,
  descriptor-init joins `16/11`, and target-phase filter rows `256/256` versus
  `0/0` controls. Both C88=1 arms had zero exact PCM source joins, zero exact
  PCM consumer joins, zero completed image-task joins, and stage-only image
  rows; PCM boundary counts stayed `88/88` in the stub pair and `87/87` in the
  image treatment. Filter rows are phase-scoped because that existing logger
  does not carry route ordinal. This selects H-TaskOutputGap at capture scope,
  refutes H-SameOrdinalVoicePath and H-StaleOrdinalReuse for the observed
  key-on/descriptor rows, and leaves H-ConsumerGap unevaluable because no
  same-ordinal source exists. No behavior change was made.

- **s2344 — C88 treatment restores the gate branch but not the complete audio contract.**
  The fresh retail preflight passed whole-RDRAM `32,419,426`, target-window
  `32,409,260`, gate/status/queue `17/22/19`, both title/hangar phases, and all
  requested named PCs; `0x8009C4E8` remained explicitly zero. The post-value
  witness recorded `0x8008EC88 -> 0x01000000` in the width-1024 and width-512
  target-like rows, while `0x8008EB7C` and `0x8008ED48` were zero. The first
  port run was rejected because the launcher omitted `ROGUESQ_LOG_AUDIOTICK_TRACE`
  and emitted zero branch rows; the fixed same-build sequential run qualified
  all four arms with title/hangar and all host/task/DMA/guest-receive/PCM/
  filter/render/key-on controls. C88=0 stored nonzero `0/3` rows and had
  `0/131` nonzero branch reads in both audio arms. C88=1 stored nonzero `2/3`
  rows and had nonzero/fall-through branch reads `125/131` stub and `128/131`
  image. Its target key-on tables showed normal-tail plus slot `02` and `00`,
  and real filter rows rose from `0` to `256`; PCM source/consumer stayed
  `88/88` and voice-event rows stayed zero. This selects
  `H-C88GateNotSufficient_PCMVoiceContractStillOpen` and authorizes no default
  writer or consumer change.

- **s2343 — B40 provenance selects H-PortWriterMismatch.** The fresh retail
  preflight passed whole-RDRAM `32,432,296`, target-window `32,422,130`,
  B40 `17`, mode/gate/status `108/17/22`, callback registration `19`, both
  title/hangar origins, and the requested named PCs; `0x8009C4E8` remained
  explicitly zero. A second positive-control oracle run used the physical
  `0xA0F50` post-value watch: `0x8008EC88` produced `0x01000000` in the
  width-1024 and width-512 target-like rows, while `0x8008EB7C` and
  `0x8008ED48` produced zero. In the same-build sequential port arms, all
  task/DMA/guest-receive/PCM/filter/render/key-on and callback-helper controls
  passed. Each arm had three target writer rows, all at `0x8008EC88`, with
  `requested=1 stored=0`; 131 branch rows per arm were positive, 254/262
  joined through `writer_seq`, and the eight `writer_seq=0` rows were the
  pre-writer prefix. All joined `0x80091468` rows had `lhs=0`,
  `taken=1`. This selects H-PortWriterMismatch, with no writer or consumer
  change.

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
2. **M5 `data_ptr+0x100` writer contract — next.** s2348 closes the
   `0x80094648` candidate and s2349 closes `0x80090CA4` as a universal writer:
   its exact field writes are title-only, while hangar attributes
   `0x171DE0` to `0x800908D4/0x8009081C/0x80090810` and leaves `0x173C20`
   unattributed in the phase census. Run one fresh retail exact-destination
   attribution for those hangar candidates and the two fields, then join the
   actual writer scope to the existing four-arm field snapshot/DMA ordering
   table. Require whole-RDRAM, task-block, exact-destination,
   title/hangar, named-PC, and all four port controls before interpreting a
   null. Do not write back the field, alter task data, change a consumer or
   default, or add a guard.
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
  The s2342 census then observed both fall-through and taken outcomes at the
  first two pre-gate branches, but only taken outcomes at `0x80091468`; the
  downstream gate/callsite rows stayed zero under the same controls. The
  measured boundary is therefore the `0x800A0F50` gate-byte test, not a
  wholly inactive `musyxSynthFrame` or an uncalled sequencer edge. No gate,
  writer, store, or consumer change is authorized.
  The s2343 census then joined target-phase writer/value rows to the
  `0x80091468` rows with `writer_seq`. Retail's `0x8008EC88` store wrote
  nonzero `0x01000000`, while both port control arms stored zero after a
  requested `1`; all joined branches read zero and bypassed. This refines the
  boundary to a port writer mismatch at the C88 site. The treatment remains
  opt-in pending a same-build downstream A/B; no default writer or consumer
  change is authorized.
  The s2344 treatment A/B then showed that nonzero C88 is read back and lets
  the gate fall through, with normal-tail key-on, slot `02/00`, and filter
  activity appearing in both audio arms. PCM source/consumer counts stayed
  unchanged and voice-event rows stayed absent, so the measured boundary is
  now the downstream voice/PCM contract rather than C88 readback. No default
  writer or consumer change is authorized.
  The s2345 ordinal table refined that boundary: C88=1 treatment rows joined
  same-ordinal key-on/slot and descriptor-init events, while image-task joins
  remained stage-only and exact PCM source/consumer joins were absent in both
  treatment arms. Filter audit rows were positive at target-phase scope only;
  they carry no route ordinal. The active boundary is task output/publication,
  not a proven PCM consumer mismatch. No writer, task-data, consumer, or
  default change is authorized.
  The s2346 task-output table then joined image-stage events to their
  `audtask-join` intervals rather than assuming route ordinal equals task
  number. In the image C88=1 treatment, 99 completed task joins advertised
  zero `output_buff` and `output_buff_size`; 3,689 generated DMA ranges had
  zero output overlap and 200 stage rows were stage-only. Sequence-keyed PCM
  rows were present, but no image-join source/consumer match restored task
  publication. This selects H-OutputMetadataWriterAbsent at capture scope;
  retail/port writer provenance is the next boundary. No output-field,
  writeback, task-data, consumer, or default change is authorized.
  The s2347 provenance table then paired that port evidence with an
  independent retail output-span witness. Retail's `0x80094648` writer was
  positive in both target phases (`24` rows each; nonzero post-value samples),
  while all four port arms had zero ABI output fields. Image control/treatment
  arms emitted `2,299/3,752` target-phase DMA ranges, with no range overlapping
  the ABI output destination. This selects H-RetailOutputWriterPortZero at
  capture scope, but does not yet prove the writer's semantic field mapping or
  a port ordering loss. No output-field, writeback, task-data, consumer, or
  default change is authorized.
  The s2348 field/order table then used a corrected four-origin retail gate
  and a regeneration-safe port snapshot of each computed `data_ptr+0x100`.
  Retail's `0x80094648` rows exposed only `0x00141AD8..0x00141AEC` writes and
  field rows with `s0=0x801B4E40/0x801DDB90`, not a proven task-field relation.
  All four port arms had unchanged pre/post values, no field-write event, and
  no DMA overlap at their computed `data_ptr+0x100`, under positive task,
  image-DMA, and C88 controls. This selects
  H-RetailWriterSentinelUnrelated at capture scope and closes the
  candidate-writer sub-boundary. The actual retail `data_ptr+0x100` writer
  remains open. No writer, writeback, task-data, consumer, or default change
  is authorized.

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
- s2341's H-PortSynthGateBypassed label is refined by s2342: it was believable
  because all three gate edges and callsites were zero under live controls,
  but the new branch census showed `musyxSynthFrame` executing its outer and
  per-iteration tests, with the `0x80091468` zero-gate branch taken in both
  arms. The qualified boundary is the gate-byte test; its writer and
  legitimacy remain open, and no bypass is authorized.
- s2342's H-PortPreGateB40Reject label is refined by s2343: it was believable
  because the branch read zero and took its bypass under positive port
  controls, but the new writer-sequence join and independent retail post-store
  watch showed `0x8008EC88` legitimately writing nonzero on retail while the
  port's control arm force-stored zero. The measured boundary is now the C88
  writer mismatch, not an unexplained consumer or phase classifier failure.
- s2344's H-C88GateNotSufficient_PCMVoiceContractStillOpen label is refined by
  s2345: it was believable because aggregate PCM and voice-event counts stayed
  unchanged after the gate treatment, but the ordinal table now shows exact
  treatment-side key-on/slot and descriptor-init rows. Neither treatment has
  an exact PCM source/consumer or completed task join; the filter rows are only
  phase-attributed. The measured boundary is task output/publication, not C88
  readback, stale ordinal reuse, or a proven consumer mismatch.
- s2345's H-TaskOutputGap label is refined by s2346: it was believable because
  treatment-side route ordinals had key-on/descriptor work but no exact PCM
  join, yet the new task-interval join shows 99 completed image C88=1 tasks.
  Their ABI output fields remain zero, all 3,689 generated ranges have zero
  output overlap, and all 200 image-stage rows are stage-only. The active
  boundary is now output-metadata writer provenance, not a proven consumer
  mismatch or an ordinal-join failure.
- s2346's H-OutputMetadataWriterAbsent label is refined by s2347: it was
  believable because the image treatment completed tasks while its ABI output
  fields and overlap rows were zero, but the fresh retail oracle independently
  observed phase-matched nonzero writes to the same output-span watch from
  `0x80094648`. The port result is therefore H-RetailOutputWriterPortZero at
  capture scope; the writer's semantic role and any port ordering loss remain
  unproven, so no contract change is authorized.
- s2347's H-RetailOutputWriterPortZero label is refined by s2348: it was
  believable because retail wrote the watched output span while every port
  ABI row exposed zero output fields, but the corrected four-origin field dump
  showed the retail writes at `0x00141AD8..0x00141AEC` with unrelated `s0`
  and source-word fields. The same-build port snapshot then found no change,
  DMA overlap, or write event at any computed `data_ptr+0x100` under positive
  controls. The writer is therefore H-RetailWriterSentinelUnrelated at the
  measured scope; no output-field or ordering change is authorized.

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
