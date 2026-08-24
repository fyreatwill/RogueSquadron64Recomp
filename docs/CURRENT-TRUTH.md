# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the append-only
ledger remains authoritative for exact commands, counts, and probe rows.
Maintained in Session 2245 (2026-08-24); behavioral and source evidence is
current through s2245, with the M5 plan refresh recorded in s2231. The
s2198–s2226 archive is §44; s2227–s2245 remain in
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
  producer boundary. s2245 now qualifies both no-log arms through title and
  hangar, selecting H-NoLogTargetQualification and allowing the five-store
  candidate table to resume. The next unit is the full field348 producer
  census with the existing image arm and all writer/callsite/stage controls;
  do not promote `ROGUESQ_AUDIO_UCODE=1` or add a writeback/consumer guard.
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
§43; and s2198–s2226 is §44. Sessions s2227–s2245 remain in the ledger.
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
