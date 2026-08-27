# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history belongs in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact commands
and probe rows remain in the ledger.

Current maintenance marker: Session 2671 (2026-08-27).

## Session 2671 result

The qualified same-build Step 1 driver passed the independent oracle whole-RDRAM
control (`10000`) and title/hangar transitions, then reached both target phases
in both arms. The silent `musyx_stub` control produced 1,290 task rows with no
DMA ranges or image-stage rows and later recorded 36 crash markers; the image
arm produced 987 task rows, 2,132 DMA-range rows, and 4,399 image-stage rows
with no crash or abort markers. Both arms retained zero task output fields and
zero PCM source/consumer payloads in this run. This selects
`H-contract-separated`: the image/silent work separation is measurable, so the
next missing edge is the output/publication contract. No runtime, audio, gate,
writeback, remap, or guard behavior changed.

## Session 2670 result

The Step 0 wrapper was changed to invoke the established `s2285` phase
driver, which retains the oracle gate and probes while using `winctl` and the
scheduled input delivery. The oracle passed its whole-RDRAM positive control
(`10000`) and title/hangar transitions. The silent arm reached title and
hangar, with 1,307 task/DMA rows and no crash or abort markers; the image arm
also reached title and hangar, with 942 task/DMA rows, 4,417 image-stage rows,
and no crash or abort markers. This selects `H-stable-driver-qualifies` and
rules out the prior wrapper's missing-input/isolated-launch explanation for
the pre-hangar loss. It qualifies the Step 1 contract comparison; no runtime,
audio, gate, writeback, remap, wait, or guard behavior changed.

## Session 2669 result

The repaired Step 0 driver ran the silent and default image arms in isolated
launches after the qualified oracle gate. The oracle passed its whole-RDRAM
positive control (`10000`) and title/hangar transitions. Both port arms
reached title but exited before hangar, each with 36 crash markers. Silent
ended at `slotDispatcherIter+3508` / guest PC `0x80022160`; default ended at
`allocAndInitGridCellArray+1276` / guest PC `0x80001C94`. Silent emitted
1,404 ABI/DMA rows and no image-stage rows; default emitted 1,386 ABI/DMA and
6,192 image-stage rows. Isolation refutes paired-process interference, but
the differing pre-hangar crashes leave the Step 0 contract control-invalid
and do not identify an audio writer or authorize audio behavior changes.

## Session 2668 result

The repaired Step 0 wrapper now launches silent and default image arms
concurrently after the oracle gate. The oracle independently passed the
whole-RDRAM positive control (`10000`) and title/hangar phases. Both port arms
reached title and emitted task/DMEM controls, but neither reached hangar:
both recorded 36 crash markers with the same `slotDispatcherIter+3508` host
path and guest PC `0x80022160`. The stub produced 1,050 ABI/DMA rows and no
image-stage rows; the default produced 977 ABI/DMA rows and 6,395 image-stage
rows. This selects `H-Step0-port-control-invalid`; the concurrent launch is
qualified, but the shared pre-hangar crash makes the M5 contract table
unevaluable. No audio behavior, gate, writeback, remap, or runtime guard
changed.

## Session 2667 result

The generated tree had seven exact stale placeholder definitions whose
addresses and human names agree in both `syms/rogue_squadron.syms.toml` and
the companion symbol files: `0x80082268`, `0x800825C8`, `0x800AD378`,
`0x800D2C98`, `0x800D4EC4`, `0x800DD2C4`, and `0x800DFB8C`. A checked-in
`tools/rename_generated_symbols.py` now applies this bounded map to generated
C, header, and overlay-table outputs. It renamed 21 references in the
external generated tree; the post-edit census found no old names and one
definition/declaration/table identity for each replacement. This advances the
symbol sweep but changes no runtime behavior. The next step remains the next
address-keyed exact-match batch; ambiguous placeholders stay generic.

## Session 2666 result

The required M5 Step 0 reconciliation initially used a stale entry-point
recipe that launched only the silent arm. Its same-run control reached only
320/640-width phases, emitted 52 audio-task dispatch rows, and emitted no
task-ABI, DMA, SP, audio-return, or PCM rows; its title/hangar controls were
therefore unevaluable. The entry point was repaired to use the existing
oracle-plus-stub/image driver, and the repaired run passed the independent
oracle whole-RDRAM positive control (`10000` callbacks), title phase, and
hangar phase. The port stub arm reached title but not hangar, then recorded
36 crash markers; it produced 65 dispatch, 265 audio-return, 795 SP-route,
52 PCM-source, 52 PCM-consumer, and 512 gate rows, with no task-ABI, DMA, or
SP rows. The image arm was never launched because the sequential driver gates
it on stub-hangar success. This selects `H-Step0-control-invalid`: the oracle
control is valid, but the port route/paired-arm control is not. It does not
select `H-Step0-closes-contract` or `H-Step0-still-unmapped`, and it does not
authorize an audio contract change. The next action is to repair the driver
so both port arms run independently/concurrently after the oracle gate.

## Session 2665 result

The M5 design gate was refreshed in [`M5-AUDIO-PLAN.md`](M5-AUDIO-PLAN.md)
after surveying `src/`, `patches/`, the checked-in runtime, the available
generated anchors, and `tools/fixup_factor5_ucode.py`. The inventory covers the
live `M_AUDTASK` image/stub selector, stock `aspMain` stub, RSP completion and
yield shims, MusyX gate/tick paths, key-on and pointer guard classes,
wait/pump/drain/reaping hatches, AI/SDL bridges, DMEM serialization, unknown
task handling, and the CPU-side MORT boundary. No audio override or host stub
exists under `patches/`, and no additional active audio behavior was found in
the fixup/runtime survey. The plan's completeness table selects
`H-Plan-covers-all-gates`; MORT and Factor 5 remain separate contracts. No
runtime code, generated function, gate, writeback, or remap changed, and no
soak was run because this was the required design-only unit.

## Decision-relevant evidence

- **s2669 — isolated Step 0 arms remain control-invalid.** After the oracle
  passed the whole-RDRAM positive control (`10000`) and title/hangar phases,
  the driver ran silent and default sequentially in separate processes. Both
  reached title but not hangar and each emitted 36 crash markers. Silent ended
  at `slotDispatcherIter+3508` / guest PC `0x80022160`; default ended at
  `allocAndInitGridCellArray+1276` / guest PC `0x80001C94`. Silent had 1,404
  ABI/DMA rows and zero image-stage rows; default had 1,386 ABI/DMA and 6,192
  image-stage rows. This refutes `H-shared-process-interference`, but the
  differing paths do not establish a common crash explanation. The control
  remains invalid because neither arm reached hangar. No runtime, audio,
  gate, writeback, remap, wait, or guard behavior changed.

- **s2668 — concurrent Step 0 arms remain control-invalid.** The oracle passed
  its whole-RDRAM positive control (`10000`) and title/hangar phases. The
  repaired wrapper launched both port arms concurrently after that gate. Stub
  and default each reached title but not hangar and each recorded 36 crash
  markers at `slotDispatcherIter+3508`, guest PC `0x80022160`. Stub counts
  were 63 dispatch, 1,050 ABI/DMA, 263 audio-return, 789 SP-route, 53 PCM
  source/consumer, and zero image-stage rows; default counts were 60
  dispatch, 977 ABI/DMA, 6,395 image-stage, 262 audio-return, 786 SP-route,
  and 54 PCM source/consumer rows. This rules out the prior sequential-driver
  omission and selects `H-Step0-port-control-invalid`; it does not identify
  an audio writer or authorize a contract change. The first repair attempt
  also exposed and was fixed for a one-shot retention-deadline reset.

- **s2666 — the first Step 0 recipe was stale and the repaired pair was
  control-invalid.** The original `run_s2277...` entry point launched only
  `ROGUESQ_AUDIO_UCODE=0`; its run reached no title/hangar phase and had no
  ABI/DMA/SP/PCM evidence beyond dispatch. After delegation to the existing
  oracle-plus-pair driver, the oracle passed whole-RDRAM (`10000` callbacks),
  title, and hangar controls. The port stub reached title but not hangar,
  crashed 36 times, and the sequential driver consequently never launched
  the image arm. The captured stub counts were 65 dispatch, 265 audio-return,
  795 SP-route, 52 PCM-source, 52 PCM-consumer, and 512 gate rows, with zero
  task-ABI, DMA, and SP rows. This selects `H-Step0-control-invalid`; the
  missing image arm makes contract closure and port-side unmapped conclusions
  unevaluable. The recipe repair is a diagnostic harness change only; no
  runtime behavior, writeback, remap, gate, wait, or generated code changed.

- **s2664 — the named retail writer call-sites are utility/texture paths, not
  a closed MORT edge.** The companion symbol file and active generated tree
  identify `0x800078EC` as the generic `rs_memset` byte-fill loop. The other
  named PCs (`0x8001E2C0` and `0x8001FACC–0x8001FD2C`) are stores inside
  `initTextureLUTAndAllocBuffers` and `loadTextureToMemory`, which initialize
  or populate 36-byte texture-LUT/image records and call `parseImageFile`.
  Their caller chains contain no MORT header, PCM buffer, or audio completion
  handoff. This selects `H-800078EC-utility` and classifies the secondary
  writers as texture/image metadata; it refutes `H-800078EC-MORT` and leaves
  `H-Secondary-writer-edge` without a legitimate payload/order join to the
  s2662 port rows. Static evidence only; no writeback, remap, gate, wait, or
  generated-code behavior changed. Full table:
  `scratch/agent/s2664_m5_retail_writer_callsite_audit.md`.

- **s2658 — retail keeps the dispatched task output fields zero.** The fixed
  oracle run passed the whole-RDRAM control with 10,000 writes, reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and recorded 983
  phase-gated type-2 executions at `0x80033FCC` for task `0x80149470`.
  Physical watches on `0x149498:0x14949C` (`output_buff`) and
  `0x14949C:0x1494A0` (`output_buff_size`) recorded zero writes; sampled task
  rows retained both fields at zero. The same-build port image/silent pair
  retained zero fields while image showed DMEM/DMA/SP completion and silent
  showed the zero-work control. This selects `H-RetailKeepsFieldsZero` for
  the fixed-object writer hypothesis and rules out a retail writer on that
  object/route. It does not rule out another task object or another output
  contract. Two recipe attempts were discarded: one had no video plugin and
  the next omitted the execution watch, so their nulls are not evidence. No
  writeback, remap, gate, or defensive behavior changed. Artifact:
  `scratch/agent/s2658_m5_task_output_fields_retry/`.

- **s2656 — producer/dispatch snapshots keep the retail audio contract zero.**
  The retail oracle passed the whole-RDRAM control with 1,030 hits, reached
  title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and retained 477
  phase-gated type-2 task rows at task pointer `0x80149470`; all sampled retail
  `output_buff` and `output_buff_size` fields were zero. The rebuilt port
  image/silent pair independently reached both target phases. In each arm,
  existing producer-side `osSpTaskLoad` snapshots for task `0x80149470`
  remained `output_buff=0` and `output_size=0` across title and hangar, while
  image tasks supplied a nonzero output contract, proving the snapshot path is
  live. The generated tree has no direct `M_AUDTASK`, `output_buff`, or
  `output_buff_size` references and no fixed task-field stores; the scheduler
  passes the received task pointer through unchanged. This selects
  `H-ProducerNeverSetsOutput` for the direct-store class and refutes
  `H-TaskPointerMismatch` at dispatch. It does not distinguish missing
  producer initialization from a generic structure copy, so that case remains
  open. No writeback, remap, gate, or defensive behavior changed. Oracle and
  port captures are independent sources; the static store census is a separate
  single-source qualification.

- **s2657 — the task-initialization boundary remains unresolved after a
  same-build pair.** The unchanged retail oracle control recorded 10,000
  whole-RDRAM writes, reached title and hangar, and retained 845 phase-gated
  type-2 rows for task `0x80149470`; sampled output fields remained zero. The
  port image/silent pair reached both target phases. Image produced 765 ABI
  rows with DMEM changes, `break_pc=0x1328`, and DMA/SP completion; silent
  produced 835 ABI rows and the expected zero-work positive control. Every
  observed task snapshot in both arms retained `0x80149470`,
  `output_buff=0`, and `output_buff_size=0`; no observed field writes fired.
  This independently refutes dispatch-time pointer mismatch and host-only
  clearing for the observed object, but does not distinguish a zero-valued
  generic copy from an overwritten producer because the hooks do not
  attribute pre-handoff guest stores. No writeback, remap, gate, or defensive
  behavior changed. Artifact:
  `scratch/agent/s2657_m5_task_init_boundary/`.

- **s2616 — same-build Step 1 rebaseline selects the image output contract
  gap.** The retail oracle passed the whole-RDRAM control at 10,000 writes and
  reached title `1024 @ 0x00790400` plus hangar `512 @ 0x006AB400`. Both port
  arms reached title and hangar. The silent arm produced no image-stage or DMA
  rows; the image arm produced 1,014 task/DMA rows, 2,189 DMA-range rows, and
  4,496 image-stage rows, with `break_pc=0x1328` and `exit=1` (`Broke`). Image
  DMA payloads and PCM source/consumer spans were still zero. The silent arm
  ended with `rc=139` in hangar; the image arm had no crash, abort, or missing
  function marker. The independent oracle route controls and the same-build
  silent/image separation select `H-ContractGap` over `H-AudioDegeneracy`;
  the crash is recorded as a failure signal, not its cause. Artifact:
  `scratch/agent/s2616_m5_step1_contract_pair/`.

- **s2614 — retail names the PCM-span writers; the port does not.** The
  debugger-enabled retail oracle passed the whole-RDRAM control with 23,413
  writes, reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and
  recorded 12,288 writes in `0x166450:0x169450`, dominated by PC `0x800078EC`.
  The secondary `0x1798B0:0x179A48` span had 1,125 writes from
  `0x800078EC`, `0x8001E2C0`, `0x80007670`, and `0x8001FAxx–0x8001FD2C`.
  The same-build port reached both phases with image completion, audio
  returns, and task joins live, but its host writer witness saw only 893
  zero-valued `kind=2, pc=0` rows. This selects `H-PortPublicationGap` over an
  absent retail writer; it does not map a legitimate port store or authorize
  writeback. Artifact: `scratch/agent/s2614_m5_pcm_writer/`.

- **s2613–s2611 — the image task contract is live but output remains open.**
  Qualified same-build runs reached title and hangar with no crash, abort, or
  missing-function markers. The image arm produced DMEM changes, generated
  DMA, image completion at `break_pc=0x1328`, and SP/task returns; the silent
  arm produced none of that work. Image payload samples and port PCM samples
  were nevertheless zero in the evaluated reruns. This selects
  `H-ContractGap` at the output edge and refutes `H-SilentPathNotIndependent`.

- **s2671 — the qualified Step 1 pair separates image work from the silent
  control.** The oracle passed its whole-RDRAM positive control (`10000`) and
  title/hangar transitions. Both port arms reached title and hangar. Silent
  produced 1,290 ABI/task rows, zero DMA-range rows, zero image-stage rows,
  and 36 post-hangar crash markers. Image produced 987 ABI/task rows, 2,132
  DMA-range rows, 4,399 image-stage rows, and no crash or abort markers. Both
  arms retained zero `output_buff`/`output_buff_size` fields and zero PCM
  source/consumer payloads. This selects `H-contract-separated` and makes the
  output/publication edge the next work unit; it does not authorize writeback
  from destination overlap or explain the silent arm's later crash.

- **s2608–s2609 — the C88 gate promotion is shipped and the indexed writer is
  legitimate.** Unset `0x8008EC88` now stores guest `$v0`; setting
  `ROGUESQ_M5_C88_VALUE=0` is the rollback. C88=`1` opens the gate and reaches
  `startSongSequence` in title and hangar. The indexed store at `0x80094648`
  writes `0x7F` to `0x80141AD8..0x80141B08`, with matching post-store reads.
  Title PCM was positive in the promotion run; hangar PCM remains zero.
  ORIGIN: these are guest writers, and the observed values are legitimate;
  no output remap or mitigation is authorized without a named publication
  edge.

- **s2605 — the known 640 abort was a broken host return.** The continuation
  `0x800155EC` was incorrectly passed to `get_function` by the lowered
  `jr-$t9` path. The regeneration-safe fixup restores the writer-parity line
  and rejects that lookup. The qualified run then reached title and hangar.

- **s2617 — the port-side PCM publication census found no complete candidate.**
  The generated tree contains no direct static references to either retail
  destination span. The named retail-PC matches are unrelated: port
  `0x8001E2C0` clears 0x24-byte texture-table records, and
  `0x8001FAxx–0x8001FD2C` parses image/texture metadata and calls the image
  parser. Existing `rs64_m5_pcm_writer_store` coverage is a generic dynamic
  destination witness, not a source/destination edge. This selects
  `H-PortPublicationGap`; no build or runtime arm was warranted.

- **s2618 — hangar PCM is image-arm output, but the indexed-writer test was
  unevaluable.** The rebuilt same-build image/silent pair reached title
  `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`; image produced 4,047
  image-stage rows and silent produced none, with 512 task handoffs in each
  arm and no crash/abort markers. Both arms had zero PCM rows in title. In
  hangar, image produced matched nonzero source/consumer rows at
  `0x80168850` and `0x80168B50` (621 and 639 nonzero bytes), while silent
  remained zero. The `0x80094648` channel-writer tag emitted no rows in
  either arm. This is a two-line result for image-arm output separation, but
  the required title positive control failed, so it does not select
  `H-HangarWriterLegitimate`, `H-HangarWriterNonPCM`, or
  `H-HangarPublicationGap`.

- **s2619 — title PCM remains absent after an oracle-grounded same-build
  recheck.** The retail oracle passed the whole-RDRAM control with 23,005
  writes, including all 12,288 writes to `0x166450:0x169450`; title was live
  for 635 VI callbacks and the dominant writer was again PC `0x800078EC`.
  The rebuilt port image/silent pair both reached title `1024 @ 0x00790400`.
  The image positive control emitted 6,627 image-stage rows and 1,027 title
  image-DMA joins; the silent arm emitted no image-stage or image-DMA rows.
  Despite that separation, title PCM joins were all zero: image had 110
  source/consumer rows and silent had 106, with `nz=0` in every row. This
  selects `H-TitlePublicationMissing` over a missing phase join and requires
  pivoting to the M5 de-stubbing sequence; it does not authorize writeback or
  identify a legitimate port writer. The image arm later hit a host bus-error
  during capture; that is a failure signal, not the title discriminator.
  Artifact: `scratch/agent/s2619_title_pcm_boundary/`.

- **s2620 — Step 3 contract-edge audit found no promotable edge.** The retail
  whole-RDRAM control and title/hangar transitions are present. Retail names
  PC `0x800078EC` as the dominant writer of `0x166450:0x169450`; the secondary
  `0x1798B0:0x179A48` span also has named retail writers. Port image rows show
  task ordering and DMA destinations, but every sampled image DMA payload is
  zero, and the host writer witness is `kind=2`, `pc=0`, with no guest
  publication PC. The generated tree has no direct static reference to the
  retail PCM spans. Thus `H-ImageOutputEdge` and `H-CPU-MORT-Edge` remain
  incomplete mappings; `H-Unproven` is selected. No writeback, remap, gate,
  or de-stub behavior change is authorized until an independent mapping names
  the port writer, destination, legitimate value, and ordering.

- **s2654 — static OSTask output audit found no guest construction site.** The
  runtime ABI defines `output_buff` at task offset `0x28` and
  `output_buff_size` at `0x2C`. The current generated tree contains no
  `M_AUDTASK`, `output_buff`, or `output_buff_size` references and only five
  `osSpTaskStartGo` callsites, all in `spTaskSchedulerThread` dispatching task
  pointers received from queues. The audit therefore cannot distinguish a
  null field from a valid field statically; it rules out a direct generated
  OSTask-construction expression as the next edge and selects a dispatch-time
  runtime capture of the two fields plus DMA destination/payload. This is a
  single-source static result; it does not identify the writer or authorize
  writeback.

- **s2655 — dispatch-time output metadata is absent on every qualified task.**
  The same-build four-arm capture passed title and hangar controls in all arms.
  Image arms produced 224/159 phase-filtered image-stage rows, 2,127/4,562
  DMA ranges, and 2,098/2,527 render rows; silent arms produced no image-stage
  rows. Yet every joined `audtask-abi` row in all arms had
  `output_buff=0x00000000` and `output_buff_size=0x00000000`, yielding zero
  output-buffer/DMA overlaps. PCM source and consumer rows were present as
  controls but all sequence payload nonzero counts were zero in `image_c0`;
  `image_c1` had 21 nonzero sequence rows. This selects
  `H-OutputMetadataWriterAbsent`: the image task route is live, but no valid
  output contract reaches dispatch. It does not identify the guest producer or
  authorize writeback; the next edge is task construction/allocation before
  `osSpTaskStartGo`.

- **s2659 — the observed retail and port output spans do not yet map to one
  legitimate publication edge.** The retail oracle reached title and hangar
  and attributed `0x166450:0x169450` primarily to guest PC `0x800078EC`, with
  mixed writers in `0x1798B0:0x179A48`. The same-build port image arm emitted
  live stage-2 DMA across the `0x166xxx` ring and stage-3 DMA to
  `0x1798B0:0x179A48`, but every sampled payload was zero and the host writer
  witness had `kind=2`, `pc=0`. Port source/consumer rows did not supply a
  stable nonzero producer or runtime MORT descriptor class. This selects
  `H-Unmapped`: destination overlap alone is insufficient to authorize
  writeback or remap. Artifact:
  `scratch/agent/s2659_m5_output_boundary/audit.md`.

- **s2662 — the fixed output-boundary pair still does not close the writer
  mapping.** The retail oracle passed the whole-RDRAM control, reached title
  and hangar, and recorded 32.1M whole-RDRAM writes, 32.1M writes in
  `0x165000:0x16B000`, and 1,125 writes in `0x1798B0:0x179A48`. Both port
  arms reached hangar with task/DMA/SP/PCM controls live. The image arm had
  two nonzero hangar stage-2 rows at `0x166450`/`0x166750` (`nz=621/639`),
  but the corresponding task joins were `stage-only`; the `0x1798B0` stage
  rows and title rows were zero. The first driver classifier was invalid
  because it required an un-emitted descriptor probe; the fixed rerun
  corrected only that predicate and added the second retail watch. This
  selects `H-DifferentContract`: destination overlap and nonzero payload are
  not enough without same-event retail writer PC/value attribution and closed
  completion-to-consumer ordering. No output writeback, remap, gate, wait, or
  generated-code behavior changed. Artifact:
  `scratch/agent/s2662_m5_output_publication_boundary_fixed/`.

- **s2663 — retail phase attribution still does not close the output edge.**
  The oracle passed the whole-RDRAM control with 59.05M writes, reached title
  `633 VI @ 0x00790400` and hangar `1,589 VI @ 0x006AB400`, and recorded
  59.04M writes in `0x165000:0x16B000` plus 1,125 in
  `0x1798B0:0x179A48`. The primary span had many phase-gated retail writer
  PCs, but neither target phase attributed a row to the known `0x800078EC`
  writer; the secondary span had no phase-gated writer rows. Lifetime
  attribution still included `0x800078EC` on the secondary span (816 hits),
  alongside `0x8001E2C0` and `0x8001FAxx–0x8001FD2C`. Phase-gated post-store
  samples were mixed: primary span 677 samples (116 zero), secondary 256
  samples (150 zero, 106 nonzero); the selected `0x800078EC` post-store
  sample was zero for the primary span and mixed for the secondary span.
  This selects `H-RetailWriterUnresolved`: no writer, legitimate payload,
  destination class, and ordering can be tied to the s2662 port rows. No
  writeback, remap, gate, wait, or generated-code behavior changed. Artifact:
  `scratch/agent/s2663_m5_retail_output_writer_attribution/`.

## s2621 unblock audit

The local oracle route passed the whole-RDRAM control with 9,107,853 writes,
reached title `1024 @ 0x00790400` and hangar `512 @ 0x006AB400`, and its
phase-gated `--watch-pc 0x800078EC` rows confirmed the companion `rs_memset`
body and zero-fill arguments. The result did not identify a legitimate
port-side PCM publication destination or producer ordering. The companion
source also has no complete body for retail `0x8002BEEC` or CPU-MORT
publication boundary. The M5 mapping remains an open dependency; the next
action is a phase-gated dispatch-time capture of task fields and DMA output.
Artifact:
`scratch/agent/unblock_s2621/oracle.log`.

## s2622 symbol-sweep result

The `0x800BF790` lead is already resolved: the companion symbol and generated
overlay table agree on `updateHudHealthIndicator` at `0x800BF790`, size
`0x634`, and `handleHUD` contains an in-tree caller. The neighboring
`0x800BF784` and `0x800BF498` entries are 12-byte and 8-byte generated
fragments; `0x800BF4A0` is the previously documented duplicate-symbol
boundary. No new defensible rename exists in this region. The next sweep lead
is `0x800C41AC/0x800C41B0`.

## s2623 symbol-sweep result

The `0x800C41B0` lead is resolved. The companion mission symbol file names it
`plotRadarBlipColumn`; the generated body spans `0x1AC` bytes from
`0x800C41B0` through `0x800C4358`, with `plotRadarBlipRow` beginning at the
exact next boundary `0x800C435C`. The generated radar path has three callers
at `0x800C4540`, `0x800C60C8`, and `0x800C60E8`, and the generated overlay
table carries the same name and `0x1AC` ROM size. The repository TOML had
remained address-coded, so it was synchronized to `plotRadarBlipColumn`; the
regenerated rename table contains `func_`, `D_`, and `fake_func_` mappings for
the address. This is an exact companion/span/caller result, not a boundary-only
rename. The next lead is `0x800C63C0`.

## s2624 symbol-sweep result

The bounded `0x800C63C0/0x800C64A4/0x800C64B0` census found one exact rename.
The mission companion file names `0x800C64B0` `initHangarDisplayItemTimers`;
the generated body spans `0x11C` bytes through `0x800C65CC`, and the generated
hangar caller at `0x800C69C4` invokes that name. The repository TOML still had
an address-coded `func_800C64B0` row, so it was synchronized to the companion
name and `build_redefs.py` emitted the `func_`, `D_`, and `fake_func_` mappings.
The `0x800C63C0` row remains an intentional overlay collision: mission
`getAvailableShipsForLevel` and menu `getAvailablePlayerCraftFlagsIgnoreUnlocks`
have distinct bodies and overlay-table entries at the same VRAM address. The
`0x800C64A4` fragment remains `fake_func_800C64A4`. No runtime behavior changed.

## s2625 symbol-sweep result

The bounded region immediately after `0x800C64B0` produced no new rename.
`0x800C64C8` is already emitted as `unlockLevelsAndCraftsBasedOnMedalsEarned`:
the menu companion names it exactly, the generated body has the matching
`0x198` span, and generated caller `0x800C09F0` invokes that name. The
mission-overlay body beginning at `0x800C64B0` overlaps this menu-overlay
address, so the two context-specific identities must not be collapsed.
`0x800C65CC` (`tickHangarDisplayItemAnimations`) and `0x800C68A0`
(`hangarVehicleDisplayNpcHandler`) are already named with matching companion
entries. `0x800C64A4` remains a 12-byte collision fragment with no defensible
semantic identity. No runtime behavior changed.

## s2626 symbol-sweep result

The bounded `0x800C68A0` census found no new rename because the region is
already exact in every required source. The mission companion names
`hangarVehicleDisplayNpcHandler`; its generated body starts at `0x800C68A0`
and spans `0x75C` bytes to the exact next boundary `0x800C6FFC`, while the
generated overlay table carries the same name and ROM size. Generated callers
use the resolved symbol. The menu-overlay `0x800C6900` entry is a distinct
overlay identity inside the mission body and must not be collapsed. The next
bounded lead is the adjacent `0x800C6FFC` boundary.

- **s2629 — the `0x800C722C` sweep lead was already exact.** The repository
  TOML maps `0x800C722C` to `getConfigFloatValue` with size `0x10`; the
  generated body is the matching 16-byte load-and-return fragment. Adjacent
  generated bodies and TOML entries match `findNamedEntryInCurrentObject`
  (`0x800C723C`, `0x2C`), `copyCurrentObjectMatrix` (`0x800C7268`, `0x48`),
  `initializeObjectiveTracking` (`0x800C72B0`, `0x38`),
  `dispatchObjectiveSlot1` (`0x800C72E8`, `0x38`),
  `calculateFriendliesSaved` (`0x800C7320`, `0x38`), and
  `checkComplexObjectives` (`0x800C7358`, `0x38`). Generated callers invoke
  the placeholder forms for `0x800C722C`, `0x800C723C`, and `0x800C7268`, while
  no unresolved symbol exists at the lead. No rename or runtime change was
  warranted; the next bounded lead is `0x800C7358`.

- **s2633 — the `0x800C7718` sweep neighborhood was already exact.** The
  bounded census through `0x800C7864` found companion names, exact generated
  spans, matching TOML/mission-overlay entries, and generated references for
  `getGlobalFloatGameState`, `getObjectiveGlobalFloat`, `setHudEnableBit4`,
  `setHudEnableBit8`, `isLevelStateByteZero`, `setFriendliesSaved`, `randMod`,
  `addBooleanCountHandleWrapper`, and `addTimerHandleWrapper`. No unresolved
  placeholder or cross-overlay collision was present, so no rename or build was
  warranted. The next bounded sweep lead is `0x800C7884`.

- **s2634 — the `0x800C7884` sweep lead was already exact.** The companion
  mission symbols name `0x800C7884` `setHudFlagBit40AndStoreArg` and describe
  its two stores; the generated body spans exactly `0x1C` bytes through the
  next boundary at `0x800C78A0`. The repository TOML and generated overlay
  table carry the same name, address, and size, and generated callers invoke
  the resolved symbol. No placeholder, duplicate overlay identity, or
  boundary-only mapping was found. No rename or build was warranted; the next
  bounded sweep lead is `0x800C78A0`.

- **s2635 — the `0x800C78A0` sweep lead was already exact.** The companion
  mission symbols name it `calculateDatItemDistanceToPlayer`; the generated
  body has the matching `0xAC` span ending at `0x800C794C`, and the repository
  TOML plus generated overlay table agree on name, address, and ROM size.
  Generated callers invoke the resolved name (10 call sites); the menu symbol
  file has no competing entry in this bounded region. No placeholder,
  duplicate overlay identity, or boundary-only mapping was found. No rename or
  build was warranted; the next bounded sweep lead is `0x800C794C`.

- **s2636 — the `0x800C794C` sweep lead was already exact.** The companion
  mission symbols name it `getScaledPlayerCraftSpeed`; the generated body in
  `funcs_36.c` spans exactly `0x2C` bytes through `0x800C7978`, and the
  repository TOML plus generated overlay table agree on name, address, and ROM
  size. Generated callers at `0x801088D0` and `0x80108EBC` invoke the resolved
  name, and the menu symbol file has no competing identity in this bounded
  region. No placeholder, duplicate overlay identity, or boundary-only mapping
  required an action. No rename or build was warranted; the next bounded sweep
  lead is `0x800C7978`.

- **s2637 — the `0x800C7978` sweep region was already exact.** The bounded
  census through `0x800C7FF8` found matching companion, generated, TOML, and
  overlay-table identities for `spawnEffectOnNamedDatItem`,
  `initActorTowardNamedDatItem`, `initAnchoredActorTowardNamedDatItem`,
  `getDatItemHealth`, `getDatItemHealthPercentage`,
  `despawnEffectOnNamedDatItem`, `setLevelObjectTrackingScalar`, both objective
  voice wrappers, `dispatchHudEffectUpdate`, `delegateToLevelStageTick`,
  `triggerNamedAssetCue`, `triggerSoundCueByType`, and
  `initNpcActorFromSpawnMessage`, with exact adjacent spans. `fake_func_800C7DB4`
  is an explicitly preserved 12-byte companion fragment, not a defensible
  semantic rename. No placeholder, duplicate overlay identity, or boundary-only
  mapping required an action; the next bounded lead is `0x800C7FF8`.

- **s2638 — synchronized one stale generated-symbol mapping.** The active
  generated output defines `updateHudHealthIndicator` at `0x800BF790` with
  the exact `0x634` span, while the repository TOML still used
  `func_800BF790`. The companion mission symbol file and generated header/body
  agree on the semantic name. The TOML row now matches the generated and
  companion identities; no runtime behavior changed. This is an exact
  regeneration/configuration rename, not a boundary-only inference.

- **s2639 — the `0x800C804C` sweep lead was already exact.** The companion
  menu identity is `computeCellGridIndices`; the repository TOML and the
  independent ELF symbol dump agree on `.ovl.menu`, address `0x800C804C`, and
  size `0x1D0`. The adjacent menu entries `buildDebrisCellBitfield` and
  `decodeDeltaCellCounts` likewise have exact names and spans, while the
  mission occupant at `0x800C8178` is a distinct overlay identity. No
  placeholder or stale mapping was found, so no rename or build was warranted.
  This rules out an actionable rename in this bounded lead, not the broader
  symbol-sweep hypothesis. The next bounded lead is `0x800C8178`.

- **s2640 — the `0x800C8178` sweep region was already exact.** The mission
  companion names `spawnNpcDestructionEffect`; its generated body starts at
  `0x800C8178` and spans exactly `0x38C` bytes to `0x800C8504`, matching the
  repository TOML and generated overlay table. The intervening menu-overlay
  entries `buildDebrisCellBitfield` (`0x800C821C`, `0x1C8`) and
  `decodeDeltaCellCounts` (`0x800C83E4`, `0x13C`) are also exact, distinct
  identities. This is an overlay collision-aware resolved region, not an
  actionable placeholder rename; the next bounded lead is `0x800C8504`.

- **s2641 — the `0x800C8504` sweep region was already exact.** The mission
  companion names `spawnNpcImpactEffectVariant`; its generated body/header,
  repository TOML, and mission overlay table agree on address `0x800C8504`
  and size `0x474`, ending at `0x800C8978`. The same VRAM window contains the
  distinct menu-overlay `allocDebrisCellTable` at `0x800C8520` and
  `buildCellSlotTableAndFindFree` at `0x800C86C8`; these are not mission
  siblings to collapse. No placeholder or stale mapping was found, so no
  rename or build was warranted; the next bounded lead is `0x800C8978`.

- **s2642 — the `0x800C8978` sweep region was already exact.** The mission
  companion names `updateNpcOrientationFromMotion` (`0x800C8978`, `0x518`),
  `setupNpcModelForState` (`0x800C8E90`, `0x100`), and `npcTurretUpdate`
  (`0x800C8F90`, `0x11FC`); generated definitions, repository TOML, and the
  mission overlay table match those spans. The overlapping menu-overlay
  entries `allocCellGeometryBuffer` (`0x800C8A64`, `0x1B8`) and
  `buildDebrisMeshFromCells` (`0x800C8C1C`, `0xE6C`) are independently exact
  and must remain distinct overlay identities. No placeholder or stale mapping
  was found, so no rename or build was warranted; the next bounded lead is
  `0x800CA18C`.

- **s2643 — the `0x800CA18C` sweep lead was already exact.** The companion
  mission symbols name it `playNpcAmbientEffect`; repository TOML agrees with
  size `0xE0`, and the next mission symbol `initNpcActorVariant` at
  `0x800CA270` confirms the exact end boundary. No stale placeholder or
  overlay collision was found in the checked-in mapping. The external
  generated-function tree was absent from this workspace, so the fresh
  generated-body/caller line could not be inspected; this is a single-source
  companion/configuration result. No rename or build was warranted; the next
  bounded lead is `0x800CA270`.

## Current state

- The qualified route is `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`; spin yield is diagnostic
  and default-off. `ROGUESQ_AUTOPILOT` is the reliable in-process driver.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `musyx_stub` control. Stock `aspMain` is not the retail contract;
  MORT is a separate CPU speech boundary.
- Image DMEM work, generated DMA, image completion, SP completion, service
  entry/exit, AI/PCM consumers, and target route controls are live. The
  missing edge is publication of nonzero PCM from the port-side equivalent of
  the retail writer family.
- Retail is the independent witness for game-side memory claims. Its
  whole-RDRAM control and target-phase transitions must precede interpretation
  of any narrow null. It reaches attract, title, and hangar, not a mission.

## Active backlog

This is one monotonic sequence; #1 is the next campaign priority.

1. **M5 Step 3 output/publication contract audit — primary active thread.**
  Step 1 now qualifies the silent/image separation through title and hangar:
  image has real DMEM/DMA/image-stage work while silent is the zero-work
  control, but both retain zero task output fields and zero PCM payloads.
  Trace one named output edge with existing task/DMA/PCM artifacts and the
  retail writer evidence before changing behavior; do not add writeback from
  destination overlap alone.
2. **M5 de-stubbing sequence — secondary active thread.** Obtain an independent
   mapping from retail PC `0x800078EC` (and the secondary-span writers) to the
   port-side writer or CPU MORT publication boundary, including destination,
   legitimate payload polarity, and ordering relative to image completion and
   PCM consumption. The s2655 dispatch capture found both output fields zero
   on every qualified task, and s2658 found no retail writes to those fields
   on the repeatedly dispatched task, so do not repeat that field census or
   add output writeback. Trace the next named output contract edge before
   changing behavior. Keep C88=`0` and `ROGUESQ_AUDIO_UCODE=0` as
   rollbacks/controls.
3. **Generated-symbol renaming sweep — parked fallback.** Resume only after
  the M5 control qualifies or is blocked by a new discriminator; use exact
  companion address/name agreement and leave ambiguous placeholders generic.
4. **M3 crash work — parked.** Resume only as a complete idiom-class audit
  with a named discriminator; passive recurrence belongs in the soak queue.
5. **Hangar visual artifact — parked.** H2 and consumer-mode H1 are refuted;
  H3 is unavailable because the oracle cannot screenshot the LLE path.
6. **M4 accumulator origin — parked.** One phase-6 producer/consumer join is
  established; broader slot coverage is optional and lower priority than M5.

## Durable boundaries

### Route, rendering, and Factor 5

Factor 5 uses custom GBI mappings documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md). Do not infer stream
semantics from standard F3DEX. Keep the qualified LLE route and existing
defensive runtime guards until a named writer explains the bad value.

### M5 audio and image output

The Factor 5 image task and CPU MORT speech path must not be conflated. A
`Broke` return is only task completion; it is not proof of PCM correctness.
The image arm's task fields, DMEM, DMA, exit, and SP completion must be joined
to service, slot/voice, MORT, PCM source, and PCM consumer rows. The current
host writer rows are zero-valued and ambiguous. No writeback, gate bypass,
forced slot state, or output remap is allowed without an `ORIGIN:` line naming
the writer and stating whether its value is legitimate.

### Safety and evidence rules

- Ask the retail oracle for ground truth before adding an instrument; its
  whole-RDRAM watch is the positive control.
- Batch every discriminator in one build and one phase-gated run. A null is
  unevaluable without its positive control; a branch counter alone is not one.
- Regenerate in order: `make_elf.py`, N64Recomp, fixup scripts, then CMake.
  Never hand-edit generated game functions for behavior changes.
- Kill runs with SIGKILL and run from `build/` with the ROM present.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export its patches in the same
  iteration.

## Session 2627 result

The bounded sweep audited `0x800C6FFC` and its adjacent boundary. The mission
companion names `0x800C6FFC` `applyNpcPositionDrift`; the generated body starts
at that address and ends at the exact next boundary `0x800C7120`, spanning
`0x124` bytes. The generated overlay table and repository TOML carry the same
name and size, and generated caller `0x800B3DFC` invokes it. `0x800C7120` is
already an exact `getConfigFloatPair` entry, so no placeholder or collision was
available to rename. This selects `H-CompanionExact` as already resolved,
rules out a boundary-only interpretation for the lead, and changes no runtime
behavior. The next bounded lead is `0x800C7120`.

## Session 2628 result

The bounded sweep audited `0x800C7120` against the mission companion symbols,
generated body, overlay table, repository TOML, and callers. The companion
name is `getConfigFloatPair`; the generated body starts at `0x800C7120` and
spans the exact `0x1C` bytes to `0x800C713C`, and the overlay table carries the
matching ROM size. Generated caller `0x800530A4` invokes the target. The
adjacent `0x800C713C` row is already the exact
`accumulateVectorInObjectFrame` mapping. No placeholder or collision remained,
so no rename or runtime change was made. This selects `H-CompanionExact` as
already resolved and moves the next bounded lead to `0x800C722C`.

## Session 2630 result

The bounded sweep audited `0x800C7358` and its adjacent objective-dispatch
region. The mission companion names the target `checkComplexObjectives`; the
generated body starts at `0x800C7358` and spans the exact `0x38` bytes to
`0x800C7390`, while the overlay table and repository TOML carry the same name
and size. Generated caller `0x800FA940` invokes the resolved symbol. The
adjacent `calculateFriendliesSaved` entry at `0x800C7320` is also exact, and
`0x800C7390` is the distinct `dealDamagetoDatItem` boundary. No placeholder,
boundary-only ambiguity, or overlay collision remained, so no source-map or
runtime change was made. This selects `H-CompanionExact` as already resolved;
the next bounded lead is `0x800C7390`.

## Session 2660 result

The M5 Step 3 behavior change remained unevaluable: s2659 still has no named
port writer, legitimate payload, or ordering relation that authorizes output
writeback, remap, gate, or wait changes. The mandated fallback sweep used the
companion symbol files as an independent source and found exact
overlay-qualified mappings for `0x800927B0`, `0x80092A54`, `0x80092CF0`, and
`0x800E9AE0`, with the checked-in TOML sizes unchanged. The first three are
`func_main_*` entries in the companion main overlay; the last is
`func_mission_overlay_*` in the companion mission overlay. The TOML now uses
those four identities, preserving overlay context. This selects
`H-CompanionExact` for the batch and leaves `0x80092F10` and
`0x8000040C` unresolved. No runtime behavior changed.

## Superseded conclusions

The old overlay/menu explanation, intrinsic 640 flakiness, missing-input and
wait-return claims, global-zero image-DMA explanation, route-wide PCM gap,
and force-zero default policy are superseded at their measured scopes. They
were believable before qualified routes, same-build controls, or independent
retail attribution existed. The detailed evidence and failed experiments are
preserved in `PORTING-STATE.md`; do not revive them without a new discriminator.

The prior symbol sweep contains many static boundary-only classifications.
Those fragments remain placeholders when the companion, source, m2c, caller,
and local-semantics searches do not supply a defensible name. Stable companion
duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Session 2661 result

The bounded fallback sweep audited the two remaining true `func_` leads.
`0x80092F10` has only the address-coded companion entry and a matching TOML
size (`0x84`); the companion names the preceding
`resampleVoiceLutSamplesPacked` but supplies no semantic name for this live
tail. `0x8000040C` is likewise only the address-coded `0x34` entry symbol,
explicitly hard-coded by the companion `make_elf.py` entry-segment injection.
Neither lead has a semantic companion identity or an overlay collision. This
selects `H-Unresolved` for both; size/boundary agreement is not sufficient for
a rename. No source, generated-code, runtime, or TOML behavior changed. The
symbol-renaming fallback is now exhausted; priority returns to the M5 plan's
next contract-edge work.

## Session 2662 result

The established M5 output-boundary driver initially returned `H-CoverageInvalid`
because its classifier required descriptor-init rows that this build does not
emit; its logs nevertheless showed the task, image, PCM, route, and phase
controls. A fixed rerun changed only that stale predicate and added a watch for
the secondary retail span. The retail whole-RDRAM and target-phase controls
passed. Both port arms reached hangar. The image arm produced nonzero stage-2
payloads at `0x166450` and `0x166750` (`nz=621` and `639`) and matching PCM
source/consumer samples, while title samples and stage-3 `0x1798B0` rows were
zero. Those rows remained `stage-only`; no same-event retail writer PC/value
or closed completion-to-consumer ordering was present. This selects
`H-DifferentContract` and rules out promoting image writeback or a CPU-MORT
mapping from destination overlap alone. No runtime behavior changed.

## Session 2631 result

The bounded generated-symbol sweep found five exact companion mappings whose
repository TOML entries were still address-coded: `computeTrackedObjectWorldAnchor`
(`0x800AD380`), `updateHangarBayScene` (`0x800AB658`),
`buildFormatMessageGlyphBuffer` (`0x800B2630`),
`buildLevelSelectTextTextures` (`0x800B3824`), and `menuOverlayInit`
(`0x800C58A0`). Each companion name matched the generated function definition;
the existing generated bodies therefore required no regeneration. The TOML
batch was synchronized to those names. The neighboring `0x800AD378` fragment
remains `fake_func_800AD378` because its companion entry is also a gap filler,
not a semantic identity. This selects `H-CompanionExact` for the five-row
batch and advances the next bounded lead to `0x800C7540`.

## Session 2632 result

The bounded `0x800C7540` census found no new rename. The companion mission
symbols, generated definitions, repository TOML, and mission overlay table
agree on exact names and spans for the objective helper family through
`setObjectiveTimer` at `0x800C76FC`; generated mission callers use the
resolved names. The generated JPEG entries `parseJfifDHTMarker` and
`paserJfifSOSMarker` overlap this VRAM range only as a separate overlay
identity, so they remain an overlay collision and must not be collapsed with
the mission helpers. No source-map or runtime change was warranted. This
selects `H-BoundaryOnly`/`H-OverlayCollision` for the remaining ambiguity and
advances the next bounded lead to `0x800C7718`.

## Session 2644 result

The bounded sweep audited `0x800CA270`. The companion mission symbols name
the function `initNpcActorVariant`; the generated body in `funcs_36.c` starts
at that address and ends at the exact next boundary `0x800CA3A4`, spanning
`0x134` bytes. The repository TOML and generated overlay table carry the same
name and ROM size. The companion's deleted `func_800CA270` note identifies an
overlapping duplicate-symbol collision, so it does not create a second
identity to collapse. No generated caller was found in the available tree.
This selects `H-CompanionExact` as already resolved, with the collision
preserved; no rename or runtime change was warranted. The next bounded lead is
`0x800CA3A4`.

## Session 2645 result

The external generated tree confirms that `0x800CA3A4` is already resolved as
`spawnProbeDroidGroundImpactEffect`, with a `0x1BC` body ending at the exact
`0x800CA560` boundary; its neighboring probe-droid functions and callers are
also semantically named. The same census found the remaining exact
companion-backed placeholder at `0x800AD378`: companion and redef sources name
it `storeTrackedObjectAuxiliaryFields`, while the generated definition remains
`fake_func_800AD378` with an `0x8` span immediately before
`computeTrackedObjectWorldAnchor`. The repository TOML now carries that
semantic name, promoting the regeneration-safe mapping from the build redef
append to the source symbol table. No overlay collision or runtime behavior
was changed. The next bounded lead is `0x800CA560`.

## Session 2646 result

The bounded sweep audited `0x800CA560` and the adjacent `0x800CA720`
boundary. The mission companion names `initProbeDroidScatterLaunch` and
`updateProbeDroidHopState`; the generated bodies start at those exact VRAM
addresses and span `0x1C0` and `0x4B4` bytes to the exact next boundaries.
The repository TOML and generated overlay table agree on both names and ROM
sizes, and generated callers invoke both resolved symbols. The menu overlay
has a distinct overlapping identity: `initModelViewer` at `0x800CA638`
through `0x800CA714`, followed by `buildModelViewerTextPage` at `0x800CA714`.
No placeholder or safe rename remained, so this selects `H-CompanionExact` as
already resolved and preserves `H-OverlayCollision`; no runtime behavior
changed. The next bounded lead is `0x800CABD4`.

## Session 2647 result

The bounded sweep audited `0x800CABD4`. The checked-in mission symbol table
already names the `0x11CC` region `npcProbeDriod`, ending at the exact
`0x800CBDA0` boundary; the following mission entries are
`findNearestNpcWithinRange`, `initActorFromSpawnTemplate`,
`tickActorTexturedSoundEffect`, and `tickAtAtBodyTransform`. The same VRAM
window contains the distinct menu-overlay `runModelViewerSoundDemo` at
`0x800CADB8`, so the identities must not be collapsed. A prior bounded ledger
census independently recorded the generated `funcs_36.c` body, exact return
boundary, and section-4 overlay span for the same name and size; that tree is
absent from this workspace but the prior evidence resolves the identity. No
rename or runtime change was warranted; the next bounded lead is
`0x800CBDA0`.

## Session 2648 result

The bounded sweep audited `0x800CBDA0`. The companion mission symbol names it
`findNearestNpcWithinRange`; the available generated snapshot emits that same
name in `funcs_37.c`, and the generated body is followed by
`initActorFromSpawnTemplate` at the exact `0x800CC03C` boundary. The overlay
table independently records the mission entry at ROM offset `0x26C70` with
size `0x29C`, matching the TOML span. The generated mission caller uses the
resolved name at two call sites, and the menu symbol file has no competing
identity in this window. No placeholder or safe rename remained, so no source
or runtime change was warranted; the next bounded lead is `0x800CC03C`.

## Session 2649 result

The bounded sweep compared the companion mission/menu symbol files, checked-in
TOML, generated `funcs_37.c`, generated overlay table, and callers around
`0x800CC03C`. `initActorFromSpawnTemplate` is already an exact mission entry
at that address with size `0x11C`, ending at `0x800CC158`; the generated body
and overlay span agree. The neighboring `fake_func_800CC038` is a distinct
menu-overlay fragment. No rename or build was warranted. This selects the
already-resolved `H-CompanionExact` result and preserves the
`H-OverlayCollision`; the next bounded lead is `0x800CC158`.

## Session 2650 result

The bounded sweep audited `0x800CC158` against the companion mission/menu
symbols, checked-in TOML, generated `funcs_37.c` and header, generated overlay
table, and callers. `tickActorTexturedSoundEffect` is already an exact mission
entry: the generated body and header use that name, its body spans `0x154`
bytes to the exact `0x800CC2AC` boundary, and the TOML and overlay table carry
the matching identity and ROM size. No placeholder, stale mapping, or safe
rename remained; no runtime or build change was warranted. This selects the
already-resolved `H-CompanionExact` result and advances the next bounded lead
to `0x800CC2AC`.

## Session 2651 result

The bounded sweep audited `0x800CC2AC` against the companion mission/menu
symbols, checked-in TOML, generated `funcs_37.c` and header, generated overlay
table, and callers. `tickAtAtBodyTransform` is already an exact mission entry:
the generated definition and header use that name, its body spans `0x70C`
bytes to the exact `0x800CC9B8` boundary, and the TOML and overlay table carry
the matching identity and ROM size. Generated callers at `0x800CE160` and
`0x800CE578` invoke the resolved name. No placeholder, stale mapping, or
safe rename remained; no runtime or build change was warranted. This selects
the already-resolved `H-CompanionExact` result and advances the next bounded
lead to `0x800CC9B8`.

## Session 2652 result

The bounded generated-symbol sweep found two exact source-table mappings that
were stale in the repository TOML. The companion mission symbols, generated
definitions and overlay spans, and generated callers agree on
`initPlayerCraftTrailBuffers` at `0x800AE3F0` (`0x1D4`) and
`stepObjectOrientationTowardTarget` at `0x800FEF10` (`0xEF0`). The TOML now
carries those semantic names, so the next regeneration will preserve the
already-generated identifiers. `0x800E9AE0` remains a placeholder in the
companion symbol file and was not renamed. No overlay collision or runtime
behavior changed; the next bounded lead is `0x800CCB1C`.

## Session 2653 result

The bounded sweep audited `0x800CCB1C`. The companion mission symbol names it
`processAtAtSubFeatureSlot`; the generated body in `funcs_37.c` uses that name,
spanning `0x17C` bytes to the exact `0x800CCC98` boundary, the TOML carries the
same name and size, and the generated caller at `0x800CE24C` invokes the
resolved name. The menu overlay has only data entries in this window. This
selects `H-CompanionExact` as already resolved; no rename or build was warranted.

Full census of remaining true `func_` placeholders in all generated files: 5
entries (`func_8000040C` in funcs_0.c; `func_800927B0`, `func_80092A54`,
`func_80092CF0` in funcs_24.c; `func_800E9AE0` in funcs_39.c). Each has only an
address-coded companion entry — no semantic name is available in the mission,
menu, or main overlay symbol files. The 125 `fake_func_` entries in the
generated files are intentionally preserved gap-fillers and duplicate-symbol
boundaries. The generated-symbol-renaming sweep is CLOSED. Priority shifts to
M5 de-stubbing (backlog #1).
