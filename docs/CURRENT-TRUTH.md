# Rogue Squadron 64 Recomp — current truth

Operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable background
is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); detailed run evidence remains
in `scratch/agent/` and the append-only ledger.

Current maintenance marker: Session 3377 (2026-08-31); active state refreshed
through Session 3437 (2026-08-31). This file was compacted
from 991 lines / 60,639 bytes to a concise active-state record; sessions
s3201–s3376 remain in the ledger and archived overview.

## Current state

The native port builds and boots through attribution, the N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024
(`0x00790400`), and hangar VI 512 (`0x006AB400`) on the validated
spin-yield/F5-LLE route. Hangar visuals still have geometry/color artifacts.
Audio is not production-complete: the Factor 5 image task is the qualified
real-audio arm and `musyx_stub`/Broke is the silent control.

The default port now returns from the attract viewer and reaches the
cinematic loop, but its stage advancer sees null `0x800B0934`; the
initializer call at `0x800A62B4` is skipped because port skip-allow remains
zero. Retail independently sets that byte to one at about 48.1 seconds,
enters the initializer, and reaches title 1024. This is a known cinematic
parity boundary, not a license to force the flag or bypass state.

M5 is the active engineering thread. Sessions 3369 and 3372 established the
status-03 worker/clear contract on retail and port. Sessions 3373–3376 then
narrowed the remaining gap to zero PCM data at the observed port RSP-DMA
source boundary:

- Retail independently writes all three primary PCM spans 768 times with
  nonzero payloads; the observed guest writer is `0x800078EC`.
- The qualified port reaches title and hangar with phase, audio-task/ABI,
  image-stage/DMA-join, and PCM controls live and no crash/abort.
- Joined stage-2/3 rows have zero source-DMEM, zero post-transform DMEM,
  and zero destination payload (`F59C39C5` / `762B22A5`, `nz=0)).
  Stage-2 destination was nonzero before the observed DMA, so this is not
  merely an empty destination read.
- This selects `H-PortRSPSourceZero` at the observed boundary and refutes
  `H-PortDMADestinationMismatch` for those joined rows. Transform behavior
  on nonzero input is unevaluable.
- Session 3378's source-DMA census passed its hook control and found 12 narrow
  target-phase DMAs: 7 from `0x1797B0` into DMEM `0x6F0` and 5 from
  `0x1798B0` into `0xCB0`; all payloads were zero. Broad task-data DMAs were
  excluded from the narrow count. Session 3379 attributed 512 target-phase
  port stores into `0x1797B0:0x1798B0` to `0x800078EC`; every observed byte was
  zero. Retail independently attributes that PC to nonzero writes in both
  spans. This selects `H-PortSourceWriterZero`, refutes writer absence for the
  observed port span, and moves the gap upstream to the writer's input/caller
  contract. Transform behavior on nonzero input remains unevaluable.
- Session 3385 rebuilt the stale executable and re-qualified the paired route:
  no-log and established-logging arms both reached title VI 1024 and hangar
  VI 512, with zero crash/abort markers. The logging arm's phase and audio/task
  controls fired. The prior s3384 pre-title crash was not reproduced; no
  direct-writer row occurred in this qualification window, so writer-edge
  hypotheses remain open.
- Session 3380's fixed caller census passed whole-RDRAM, title, hangar,
  audio-ABI, image-join, PCM-join, and PCM-boundary controls. The port target
  span was issued by `rs_memset` callsite `0x8008F2CC` with
  `dst=0x801797B0`, `val=0`, `len=0x298`; retail's target-phase writer
  predecessor was independently `0x8002BEEC` (399 rows), with the same
  sampled zero-fill tuple. This selects `H-PortSourceCallerMismatch` at the
  observed boundary. It does not establish that the zero fill is illegitimate
  or select a nonzero-input path.
- Session 3386 phase-qualified the direct-writer edge. The port reached title
  and hangar with all controls live; its only target-overlap row was the
  zero-fill `0x8008F2CC -> rs_memset` path, with no `0x8002BEEC` caller edge or
  callback-writer row. The independent retail control fired, and its
  undriven route executed `0x800078EC` 9,667 times but not `0x8002BEEC`.
  This selects `H-EarlierProducerGap` for the driven port route and refutes a
  port-side dispatch alias at the observed boundary. It does not establish
  whether the zero fill is legitimate.
- Session 3387 asked the independent retail oracle for the selected producer
  edge, with a whole-RDRAM positive control, then ran the existing port census
  in the same phase-qualified route. Retail reached title and hangar, and its
  two target spans each had 449 writes: 256 phase writes from `0x800078EC`,
  116 from `0x80007670`, and small initialization bursts. The port reached
  both phases and exposed only the zero-fill `0x8008F2CC -> rs_memset` row at
  the target span; it exposed no matching `0x800078EC`, `0x80007670`, or
  `0x8002BEEC` edge. This selects `H-RetailDrivenProducer` and refutes a
  matching port producer edge at the observed boundary. It does not establish
  that the port zero fill is illegitimate or identify the missing producer's
  input/dispatch contract. Detailed evidence is in
  [M5-S3387-PRODUCER-EDGE.md](M5-S3387-PRODUCER-EDGE.md).

- Session 3388 repeated the qualified pair with both producer execution
  watches. Retail's whole-RDRAM control and both phase gates fired; target
  writer histograms included `0x80007670` (116/184) and `0x800078EC`
  (512/816), and `0x8002BEEC` preceded `0x800078EC` in 387 execution rows.
  The port reached title and hangar but exposed only the zero-fill
  `0x8008F2CC -> rs_memset` at `0x801797B0`, with no matching producer edge;
  PCM remained zero. This reinforces `H-RetailDrivenProducer` at the observed
  boundary and points the next census at the predecessor/call chain. Evidence
   is in [M5-S3388-PRODUCER-PREDECESSOR.md](M5-S3388-PRODUCER-PREDECESSOR.md).

- Session 3389 watched the selected predecessor PCs on retail with a
  whole-RDRAM control. Retail reached title and both `0x8002BEEC` and
  `0x800078E8` fired there; their immediate predecessors were `0x8002BEE8`
  and `0x800078E0`. Retail target spans had 502/500 writes, but the explicit
  hangar 512 bucket had no rows. The port reached title and hangar with
  controls live and again exposed only `0x8008F2CC -> rs_memset` zero-fill at
  the target span, with no matching producer or callback row and zero PCM.
  This reinforces an earlier producer gap at the observed boundaries, but is
  not a like-for-like hangar discriminator; the next probe moves to
  `0x800078E0`/`0x8002BEE8`.

- Session 3390 repeated the retail arm with the selected predecessor PCs and
  target-span payload control. Whole-RDRAM and target controls fired (11,830
  and 1,830 writes); retail reached hangar and had 664 target-writer samples,
  189 nonzero. The port reached title and hangar with controls live but again
  exposed only `0x8008F2CC -> rs_memset` zero-fill, with no matching producer
  edge and zero PCM. This selects `H-EarlierRetailProducer` and refutes a
  matching port predecessor edge and a legitimate zero boundary at this
  scope. The port later hit the existing unaligned-ROM DMA assertion after
  leaving hangar, outside the discriminator. Evidence is in
  [M5-S3390-PREDECESSOR-EDGE.md](M5-S3390-PREDECESSOR-EDGE.md).

- Session 3391 enumerated the current generated `jal 0x800078E0` set (88
  callsites) and ran the selected earlier-producer census. Retail's
  whole-RDRAM control fired 223,338 times over 7,169 VI frames; its
  `0x8002BEE8` predecessor execution watch fired 37,635 times and its
  `0x800078E0`/`0x800078E8` controls were live. The target-span oracle watch
  produced no visible hit rows, so payload attribution for this arm is
  partial. The port reached title and hangar with phase, static-call, and PCM
  controls live; its only hangar target row remained the zero-fill
  `0x8008F2CC -> rs_memset` path (`dst=0x801797B0`, `len=0x298`), with no
  callback or earlier-producer row and zero PCM. This selects
  `H-EarlierPortContract` at the observed boundary, but does not establish
  that the zero fill is illegitimate or provide a retail payload comparison.
  Evidence is in [M5-S3391-EARLIER-PRODUCER.md](M5-S3391-EARLIER-PRODUCER.md).

- Session 3392 first ran the independent oracle with the selected predecessor
  watches. Its whole-RDRAM and predecessor controls fired, but the
  target-span watch again produced no recognizable target rows, so retail
  payload attribution was partial. The first port arm hit the known
  pre-title `filterVoiceSampleBlock` crash; a same-build retry reached title
  and hangar with controls live and no crash/abort markers. It again exposed
  only the zero-fill `0x8008F2CC -> rs_memset` row and zero PCM, with no
  callback or earlier-producer row. This reinforces `H-EarlierPortContract`
  at the port boundary, but does not add the required like-for-like retail
  payload edge. Evidence is in
  [M5-S3392-EARLIER-PRODUCER-RETRY.md](M5-S3392-EARLIER-PRODUCER-RETRY.md).

- Session 3393 lowered oracle noise to the exact target span and only the
  `0x800078E8/0x800078EC` execution watches. Retail controls fired: 11,125
  whole-RDRAM writes, 1,125 target-span writes, 6,507 `0x800078E8` executions,
  and 3,244,851 `0x800078EC` executions. The target-span phase attribution
  remained zero, so payload attribution is still partial. The port reached
  title and hangar with phase and PCM controls live; it exposed only the
  `0x8008F2CC -> rs_memset` zero fill at `0x801797B0` and no matching producer
  row. This reinforces `H-EarlierPortContract` only at the observed port
  boundary and closes this exact census as non-discriminating. Evidence is in
  [M5-S3393-LOWER-NOISE-TARGET-ATTRIBUTION.md](M5-S3393-LOWER-NOISE-TARGET-ATTRIBUTION.md).

No output substitution or mitigation is authorized. Do not change waits, slots,
status handling, consumer dispatch, or PCM writeback while tracing the source.

Session 3394 attempted the prescribed dual-origin retail repair. The 120-second
oracle arm passed the whole-RDRAM control and reached the 512 route, with
`0x800078E8/0x800078EC` rows under `origin=0x006AB400` and none under
`0x006AB000`, but stopped before final watch and histogram summaries. A
same-recipe 45-second retry exited before the 512 phase. The exact target
watch and both final phase histograms are therefore unavailable; this oracle
attribution field is unevaluable and no origin hypothesis is selected.

Session 3395 rebuilt the target and ran the existing phase-qualified image /
silent contract pair after the retail oracle. The oracle positive control
passed at 10,000 whole-RDRAM callbacks and reached title 1024 and hangar 512,
but both port arms crashed before any phase-qualified audio row, at the same
`spTaskSchedulerThread+9536` / guest PC `0x8000834c` scheduler boundary. Each
arm had zero dispatch, ABI, DMA, image-join, return, service/slot, and PCM
rows. The candidate image DMEM-to-RDRAM edge is therefore unevaluable; no
audio edge or behavior change is selected. Evidence is in
`scratch/agent/s3395_m5_contract_edge_qualification_retry/RESULTS.md`.

Session 3396 repaired the ground-truth completion path by adding a SIGUSR1
request serviced at the next retail VI callback on the emulator thread. The
same-run whole-RDRAM control reached 10,000 callbacks; retail reached title
1024 and hangar 512, and the checkpoint was observed before SIGKILL. At the
checkpoint, candidate destination watches had 16, 16, 16, and 36 writes at
`0x166D50`, `0x167050`, `0x167350`, and `0x1935E0`; the four phase histograms
were emitted, though only the title bucket attributed 16 writes at
`0x1935E0` to `0x800078EC`. The concurrent port arms both reached title and
hangar without crash/abort markers: silent had 680 ABI/DMA rows and zero
image-stage rows; image had 679 ABI rows, 1,370 DMA rows, and 2,749 image-stage
rows. Both retained zero PCM (`FNV=0xF59C39C5`, `nz=0`). This refutes the
specific s3395 pre-dispatch failure as a repeatable qualification blocker and
establishes a completion-safe retail/port comparison path, but does not yet
select `H-ImageEdgeMissing` or `H-ImageEdgePresent`: the checkpoint has no
post-store payload values and the retail target writes are not yet a complete
like-for-like phase attribution. No audio behavior changed. Evidence is in
`scratch/agent/s3396_m5_checkpoint_pair/driver.log` and the paired logs.

Session 3397 rebuilt the oracle checkpoint to emit post-store values, then ran
the complete retail/port matrix. Retail's positive control reached 10,000
callbacks and both title/hangar gates. At the checkpoint, retail had 16 writes
each at `0x166D50`, `0x167050`, and `0x167350`, with no retained post-value
samples, and 36 writes at `0x1935E0`, including 18 retained post-value samples
and 12 nonzero samples from writer `0x800078EC`. The paired port arms reached
title and hangar without crash/abort. Silent had 678 ABI/DMA rows and no
image-stage rows; image had 673 ABI rows and 2,740 image-stage rows. Image's
stage-2 candidate publications were zero (`FNV=F59C39C5`, `nz=0`), while its
stage-3 publication went mainly to `0x178D80` (651 rows), not retail's
`0x1935E0`; its two `0x1935E0` rows were also zero. PCM remained zero. This
selects `H-ImageEdgeMissing` for the observed stage-3 publication contract and
refutes matching nonzero retail/port publication at that destination. It does
not establish why the port destination differs or whether stage-2 zero output
is legitimate. Evidence is in [M5-S3397-IMAGE-PAYLOAD.md](M5-S3397-IMAGE-PAYLOAD.md)
and `scratch/agent/s3397_m5_image_payload_pair/driver.log`.

Session 3398 repeated the completion-safe matrix with the existing stage-3
contract recipe. The retail positive control reached 10,000 callbacks and
title/hangar; its phase-qualified `0x1935E0` watch had 34 writes, 18 retained
post-store samples, and 12 nonzero samples from `0x800078EC`. Both port arms
reached hangar without crash/abort markers. The image arm had 2,753 image-stage
and 1,372 DMA rows; stage 3 completed from DMEM `0xCB0` to `0x801798B0`
(`0x1798B0` physical), with zero payload (`762B22A5`, `nz=0`) and no matching
`0x1935E0` publication. SP completion/delivery, guest receive, and PCM rows
were present, while PCM remained zero. The two independent lines select
`H-PortStage3Missing` at the observed publication boundary and refute a
destination alias or legitimate-zero explanation there. The destination
contract and output legitimacy remain unresolved. Evidence is in
[M5-S3398-STAGE3-DESTINATION.md](M5-S3398-STAGE3-DESTINATION.md).

Session 3399 repeated the completion-safe destination-contract matrix after a
fresh build. The oracle whole-RDRAM control reached 10,000 callbacks, both
title/hangar phase gates fired, and its checkpoint retained 16 post-store
samples at `0x1935E0` from `0x800078EC`, with 12 nonzero. Both port arms
reached hangar without crash/abort markers. The image arm again enumerated
stage 3 as `r2=0x350`, `field348=0x801797B0`, `field44=0`, and
`dest=0x801798B0` (`0x1798B0` physical), copying DMEM `0xCB0..0xE48`
(`len=0x198`) with `762B22A5`, `nz=0`; its join rows were `stage-only`,
while DMA/exit, SP delivery, guest receive, and PCM rows were present. The
silent arm supplied the expected ABI/DMA and completion controls, and PCM
remained zero. This independently repeats the selection of
`H-PortStage3Missing` at the observed publication boundary and refutes an
address-alias or legitimate-zero explanation there. The field/caller origin
and zero-output legitimacy remain unresolved; no audio behavior changed.
Evidence: `scratch/agent/s3399_m5_stage3_destination_contract/driver.log` and
the paired logs.

Session 3409 joined the port's phase-qualified `0x800052C4` route to
post-`rs_memset` bytes in one fresh-build concurrent silent/image pair. Both
arms reached title 1024 and hangar 512 with task ABI/DMA controls live and no
crash/abort markers. The keyed witness fired 64 bounded rows per arm, proving
the candidate route is live, but none targeted `0x801797B0` or `0x801798B0`;
the target clear remained the independent `0x8008F2CC` callsite. This selects
`H-Port052C4Distinct` and refutes `H-Port052C4Publishes` at the observed
destinations. The upstream zero-output cause remains unresolved. Evidence is
in [M5-S3409-052C4-JOIN.md](M5-S3409-052C4-JOIN.md).

Session 3412 reran the downstream producer join from a fresh build. Both
silent and image arms passed title 1024 and hangar 512, with ABI/DMA controls
live and no crash/abort markers. The image arm joined the hangar clear at
`0x8008F2CC` to `field348=0x801797B0`; `0x800078EC` executed on that route and
wrote the source span, but every observed byte was zero. Stage 3 copied zero
DMEM `0xCB0..0xE48` to `0x801798B0` (`FNV=762B22A5`, `nz=0`), while the silent
control produced no image-stage rows and PCM stayed zero. This selects
`H-PortImageSourceStillZero`, refutes a missing producer edge at the observed
boundary, and does not establish why the producer input is zero. Evidence is
in [M5-S3412-DOWNSTREAM-PRODUCER.md](M5-S3412-DOWNSTREAM-PRODUCER.md).

Session 3413 ran the prescribed retail source-span oracle. The Rice-plugin
attempt failed during GLSL compilation, so it was rerun with the installed
Glide64mk2 plugin. The repaired run completed 120 seconds, passed the
whole-RDRAM positive control at 10,000 writes, and observed `0x800078EC`
9,667 times, but recorded zero writes to physical `0x1797B0:0x179A48` and no
phase-qualified source-span rows. All producer execution rows had
`prev=0x800078EC`. This is a valid global negative but the planned hangar
classification is unevaluable because the phase bucket was absent; it selects
neither retail-nonzero nor shared-zero. Evidence is in
[M5-S3413-RETAIL-SOURCE-SPAN.md](M5-S3413-RETAIL-SOURCE-SPAN.md).

Session 3414 corrected the retail route to Rice video, driven Start presses,
and an explicit hangar phase width. The whole-RDRAM control reached 11,866
writes and the run reached 7,173 VI frames. In the 512-wide
`0x006AB400` hangar bucket (1,540 VI rows), `0x800078EC` wrote the port source
span `0x1797B0:0x179A48` 664 times; it wrote none of the previously observed
`0x1935E0:0x1935F0` destination. Source-span post-store samples included 340
nonzero producer samples. This selects `H-RetailPublishes1797B0` and refutes a
retail-only destination mismatch at `0x1935E0`; the remaining gap is the
port-side producer input/payload formation. Evidence is in
[M5-S3414-RETAIL-DESTINATION-MAP.md](M5-S3414-RETAIL-DESTINATION-MAP.md).

Session 3415 ran the fresh-build phase-qualified port silent/image pair with
the producer witness. Both arms reached title 1024 and hangar 512; phase,
field-writer, PCM-writer, audio ABI/DMA, and route controls fired, with no
crash/abort markers. In the hangar bucket, `0x800078EC` wrote 384 bytes into
`0x1797B0:0x179A48` in each arm, all with `value_nz=0`; the writer PC was
`0x800078EC` for every row. The image arm also produced 1,209 ABI/DMA rows
and 1,209 stage-3 rows; stage 3 copied `0xCB0..0xE48` to `0x801798B0` with
`FNV=0x762B22A5`, `nz=0`. This selects `H-PortProducerZero`, refutes producer
absence and a nonzero port producer at the observed edge, and leaves the
producer entry-input/transform contract unresolved. Evidence is in
`scratch/agent/s3411_m5_downstream_join/{silent,image}.log`.

Session 3416 attempted the producer-entry contract census. The debugger-heavy
oracle arm did not reach shutdown because watched-execution detail flooded the
capture; the retained s3414 retail control remains valid with whole-RDRAM,
title/hangar, and nonzero target-span writer controls. The fresh-build port
pair was asymmetric: image reached title and hangar with 1,176 audio ABI/DMA
rows and 768 field-writer rows, all target-span producer bytes zero; silent
crashed at `spTaskSchedulerThread+9536` / guest PC `0x8000834c` before target
phase. The port entry witness captured the title zero-fill
`0x8008F2CC -> dst=0x801797B0, val=0, len=0x298`, but no like-for-like hangar
producer-entry tuple. This selects none of `H-PortEntryInputZero`,
`H-PortEntryTransformZero`, or `H-PortEntryRouteMismatch`; it is a
qualification failure, not evidence that the zero is legitimate.

Session 3417 could not qualify the required retail entry-argument ground truth.
The prescribed no-video oracle passed the whole-RDRAM control (10,000
callbacks) and observed 9,667 executions at `0x800078EC`, but its requested
hangar phase bucket contained zero rows. The fixed Rice/Start-driven route
passed the same control and reached title 1024 (VI 2037), then stopped at about
34.6 seconds before hangar and emitted no final target histogram. No port entry
witness was added or run. This was a qualification failure, not evidence about
the producer inputs.

Session 3418 reran the retail arm in the foreground with the validated Rice/
Start route and preserved its final summaries. The whole-RDRAM control reached
10,000 callbacks; title 1024 and hangar 512 at `0x006AB400` were observed, with
1,540 VI rows in the hangar bucket. The target span had 1,166 writes, including
664 from `0x800078EC`; post-store sampling reported 325 nonzero and 339 zero
samples. This qualifies the independent retail phase and producer controls,
but is single-source ground truth and does not identify the port's missing
input or make a legitimacy claim about retail zero writes. Evidence is in
`scratch/agent/s3420_retail_producer_entry_qualification/oracle_final2.log`.

Session 3419 ran the fresh-build port entry-argument witness in concurrent
silent and Factor 5 image arms. Both arms passed title 1024 and hangar 512,
both entry controls fired, and neither crashed or aborted. Their first
phase-qualified target entries were identical:
a0=0x801797B0, a1=0, a2=0x298, v0=0x801797B0; the image arm also retained
4,909 image-stage rows while silent retained none. This selects
H-PortEntryArgsZero and refutes matching nonzero entry arguments at the
observed port boundary. The generated host call exposed ra=0, so caller route
remains open. This does not establish that the zero fill is illegitimate; a
like-for-like retail entry tuple is the next discriminator. Evidence is in
M5-S3419-WRITER-ENTRY-ARGS.md.

Session 3420 ran the independent retail oracle with whole-RDRAM, target-span,
producer-PC, and target-store controls. The route completed cleanly with
11,166 whole-RDRAM writes, 1,166 target-span writes, and 1,289,923 producer-PC
execution hits. All 664 target-span writes from `0x800078EC` had the same
entry tuple as the port: `a0=0x801797B0`, `a1=0`, `a2=0x298`,
`ra=0x8008F2D4`. They occurred under width 1024/origin `0x006AB800`; the
prior 512 gate was not the callback's live phase and produced a false zero.
Retail post-store samples remained mixed, with 65 nonzero bytes in the final
range. This selects `H-RetailEntryZero`, refutes `H-RetailEntryNonzero`, and
closes the entry-argument explanation at this boundary. The next discriminator
is writer-loop internal state or the subsequent publication path; no runtime
behavior changed. Evidence is in
[M5-S3420-RETAIL-ENTRY-ARGS.md](M5-S3420-RETAIL-ENTRY-ARGS.md).

Session 3421 added the regeneration-safe writer-loop witness and ran the
silent/image pair. Both arms reached title 1024 and hangar 512 with all route
controls live and no crash/abort. The new witness produced 72 rows in each
arm; the target tuple matched between arms but differed from the retail
ordinary-loop ground-truth shape: port target `s0=0x12`, `s1=0x5622`, versus
retail `s0=a0`, `s1=0x18`. Port target `v0`/`v1` advanced normally, and the
non-target port control showed `s0=a0`, `s1=a2`, validating the witness. This
selects `H-PortWriterStateDiffers` at the observed boundary, but does not
establish whether the difference is caller state or host register setup.
Evidence is in [M5-S3421-WRITER-STATE.md](M5-S3421-WRITER-STATE.md).

Session 3422 joined the exact retail target-span stores to writer-loop state.
The corrected oracle passed whole-RDRAM, target-span, producer-PC, and both
target phase controls; all 664 phase-qualified retail rows at `0x800078EC`
had `s0=0x12`, `s1=0x561F`, `t0=0x2000FF01`, `t1=0x8010FEF8`, and
`ra=0x8008F2D4`. The fresh-build silent/image pair reached title and hangar
with all controls live and no crash/abort; both had target rows with
`s0=0x12`, `s1=0x5622`, `t0=1`, `t1=0`, and `ra=0`. This selects
`H-RetailTargetStateDiffers`, refutes matching target state and another retail
writer, and moves the probe to the first producer of the differing
`s1/t0/t1/ra` state. The port `v0/v1` loop advanced normally; no audio behavior
changed. Evidence is in
[M5-S3422-RETAIL-WRITER-STATE.md](M5-S3422-RETAIL-WRITER-STATE.md).

Session 3423 compared the target writer state immediately before guest caller
`0x8008F2CC` invokes `rs_memset` and at host entry. The first concurrent pair
hit the known early scheduler crash before M5 controls; same-build retries
reached hangar 512 with no crash or abort. Silent and image both fired the
setup positive control and target row. At the caller edge, both had
`s1=0x5622`, `t0=1`, `t1=0`, `ra=0`, with `s0=0x12`, `a0=0x801797B0`, and
`a2=0x298`; host entry retained the same tuple. This selects
`H-PortSetupStateDiffers` and refutes a first divergence introduced by the
host wrapper for the observed target call. The earlier producer of this state
and zero PCM output remain unresolved. Evidence is in
[M5-S3423-WRITER-SETUP.md](M5-S3423-WRITER-SETUP.md).

Session 3424 extended the setup witness to guest PCs `0x8008F2A8`,
`0x8008F2BC`, `0x8008F2C0`, `0x8008F2C4`, and `0x8008F2C8`. Both concurrent
silent and image arms reached title/hangar with phase, ABI/DMA, setup, target,
and image controls live and no crash/abort markers. Both arms already had
`s1=0x5622`, `t0=1`, `t1=0`, and `ra=0` at the first edge `0x8008F2A8`, and
the tuple stayed unchanged through the target caller. This selects
`H-PortEarlierSetupProducer`, refutes an internal divergence in the five
observed setup edges, and moves the boundary to the caller/entry of
`allocateSongChannelArray`. It does not establish that the port tuple is
illegitimate or identify the upstream producer; PCM remains zero. Evidence is
in [M5-S3424-WRITER-SETUP-PREDECESSOR.md](M5-S3424-WRITER-SETUP-PREDECESSOR.md).

Session 3425 qualified the caller/entry boundary with the independent retail
oracle first, then ran a fresh-build silent/image port pair. Retail's
`allocateSongChannelArray` entry at `0x8008F0A0` had `a0=0x12`, `a1=0x561F`,
and `prev_pc=0x80091934`; its `0x8008F2A0` edge had `a0=0x3C9`, `s1=0x561F`,
and `v0=0x80175AF0`. Both port arms had live controls and the same entry
boundary before title: `a1=0x5622`; their `0x8008F2A0` rows had `s1=0x5622`
and arm-specific allocator returns. This selects `H-UpstreamCallerContract`
and refutes `H-InternalMallocReturn` at the observed boundary: the divergence
is already present at function entry, not introduced by the first observed
malloc return. The caller contract remains unresolved and is not proven
illegitimate. Evidence is in
[M5-S3425-ALLOCATE-CALLER-BOUNDARY.md](M5-S3425-ALLOCATE-CALLER-BOUNDARY.md).

Session 3426 qualified the preceding `initN64RspMixer` edge. Retail's
independent oracle saw `0x80091934` enter `allocateSongChannelArray` with
`a1=0x561F`, and the callee retained that value. In both fresh-build port
arms, the phase-gated init witness saw entry
`a0=0x80165ED0, a1=0x0F, a2=0xA0, a3=1`; immediately before the
`0x80091934` call it saw `a0=0x0F, a1=0x5622, a2=0xA0, a3=1`.
Whole-RDRAM, title, hangar, witness, and audio ABI/DMA controls were live, and
both arms had no crash/abort markers. This selects `H-CallerPassesPortCount`
at the observed init-to-allocate edge and refutes `H-CalleeMutatesCount` and
`H-CallerUnevaluable` there. It does not establish that `0x5622` is legitimate
or identify the earlier producer. Evidence is in
[M5-S3426-INIT-MIXER-CALLER.md](M5-S3426-INIT-MIXER-CALLER.md).

Session 3427 corrected a stale caller-watch address: `0x80091898` is the
delay-slot NOP; the function entry is `0x8009189C`. Generated-source census
found two JALs, at `0x80091C58` and `0x80091D14`. The corrected retail oracle
passed its whole-RDRAM control, title/hangar gates, and watched the entry
twice, both from `prev_pc=0x80091D14`, with `a0=0x80165ED0, a1=0x12, a2=0,
v0=1`; no `0x80091C58` hit occurred on the driven route. A retry of the
same-build silent/image port pair qualified both arms through title and
hangar with init and audio ABI/DMA controls live and no crash/abort markers.
Both port arms retained the Session 3426 init/pre-allocate tuples, but the
entry witness's `ra` was zero in every sampled row, so it cannot identify a
direct caller. This selects a retail/port caller-site asymmetry at the
observed route, not caller parity; it does not prove the port count
illegitimate. Evidence is in [M5-S3427-INIT-CALLER-CHAIN.md](M5-S3427-INIT-CALLER-CHAIN.md).

Session 3428 added direct phase-gated witnesses immediately before both
generated `initN64RspMixer` callsites. The independent retail oracle passed
its whole-RDRAM control (10,000 writes), reached title/hangar, and again
observed two `0x80091D14` calls and zero `0x80091C58` calls. The fresh-build
silent/image pair both reached title 1024 and hangar 512 with init and audio
ABI/DMA controls live; image-stage was live only in the image arm, and neither
arm crashed or aborted. Both port arms reported `caller=0x80091D14` in title
and hangar with the same arguments as the prior init witness; neither reported
`0x80091C58`. This selects `H-PortCallerD1D14`, matching retail, and closes
the direct caller-site question. The earlier producer of port `a1=0x5622`
remains unresolved; no audio behavior changed. Evidence is in
[M5-S3428-INIT-CALLSITES.md](M5-S3428-INIT-CALLSITES.md).

Session 3429 tested the prescribed setup-state labels with ground truth first.
The retail whole-RDRAM control reached title/hangar and fired 10,000 writes;
retail executed `0x80091848` 9,753 times and `0x80091B84` zero times. Static
symbols show these are instructions inside generated functions, not the named
function entries. A fresh-build silent/image pair reached title/hangar with
controls live and no crash/abort. Actual generated entry witnesses saw only
`reapplyAudioConfig` once per arm, with `a1=0x12`; no target-phase
`initAudioSubsystem` row occurred. This refutes the current labels as a
like-for-like count boundary but leaves the producer unevaluable. Evidence is
in [M5-S3429-SETUP-STATE-ENTRY.md](M5-S3429-SETUP-STATE-ENTRY.md).

Session 3430 qualified the real `setDisplayMode` callsites with ground truth
first. Retail passed the whole-RDRAM control and title/hangar gates; its
`0x8008EBC0` watch fired in both target phases with
`a0=0x80165ED0, a1=0x12, a2=0x0E, a3=0`, while `0x8008EA78` had no hit on the
driven route. The fresh-build concurrent silent/image pair reached title 1024
and hangar 512 with all controls live and no crash/abort markers. The caller
witness fired only for `set-reapply`, once per arm at title, with
`a0=0x80165ED0, a1=0x12, a2=0, a3=0`; neither arm exposed `set-init`. This
selects `H-DirectSetupCallerCountParity`: port and retail both pass
`a1=0x12` at the observed reapply call, although their other arguments are not
identical. It refutes the proposed `0x5622` count at either observed
`setDisplayMode` audio callsite. The earlier producer of the init-to-allocate
`0x5622` value remains unresolved. Evidence is in
[M5-S3430-SETDISPLAY-CALLERS.md](M5-S3430-SETDISPLAY-CALLERS.md).

## Next steps

Session 3432 repeated the frequency-result work unit. The retail oracle passed
its whole-RDRAM control (10,041 callbacks) and observed 41 writes to physical
`0x165ED0`, but its configured title/hangar phase buckets remained zero. The
lifetime writer histogram included `0x800331E0` twice and `0x80007670` four
times among several setup/initialization writers, so exact frequency-return
attribution is unevaluable. The sequential port pair independently qualified
both silent and image arms through title 1024 and hangar 512 without crash or
abort; both returned `0x5622` from `osAiSetFrequency` and supplied the same
title/hangar count tuples to the downstream chain. This refutes a silent/image
arm divergence at the observed port boundary, but selects none of the retail
writer hypotheses. Evidence is in
[M5-S3432-FREQUENCY-WRITER.md](M5-S3432-FREQUENCY-WRITER.md).

Session 3433 repaired the retail phase signal. A `--vi-trace` arm with the
whole-RDRAM positive control observed the title's width-1024 origins alternating
between `0x00790400` and `0x00790800`. A second arm configured both origins and
again passed the control; physical `0x165ED0` had 12,536 lifetime writes, with
634 VI rows in the `0x00790400` bucket and 633 in the `0x00790800` bucket.
Phase writer histograms were nonempty in both buckets and post-value samples
included nonzero `0x5622` and `0x561F`. This selects `H-OraclePhaseOriginMismatch`
and refutes phase-signal absence at the observed title route, but does not yet
identify the exact frequency writer because each phase bucket still contains
multiple writers. Evidence is in [M5-S3433-FREQUENCY-PHASE.md](M5-S3433-FREQUENCY-PHASE.md).

Session 3434 isolated the retail frequency-result writer with the repaired
phase signal. The oracle positive control reached 10,000 callbacks and both
title buckets recorded 632 VI rows. Target writes at `0x165ED0` joined
`0x800331E0` in both buckets; its post-store samples were 442/442 nonzero.
`0x80033420` joined only the second bucket and its 8/8 post-store samples were
zero. This selects `H-Candidate331E0`, refutes `H-Candidate33420` as the
nonzero result writer, and makes an unlisted writer unlikely at this boundary.
The caller/input contract remains unresolved. Evidence is in
[M5-S3434-FREQUENCY-WRITER.md](M5-S3434-FREQUENCY-WRITER.md).

Session 3435 traced the selected `0x800331E0` writer with both title origins,
the whole-RDRAM control, field dumps, and post-value sampling. The control
reached 10,000 callbacks. Phase-gated field tuples were highly non-unique:
3,735 distinct tuples in `0x00790400` and 4,088 in `0x00790800`. The target
post-value watch retained 701 samples with 64 distinct values, including 450
`0x00000001` samples. This selects `H-Multiple331E0Inputs` and refutes a
single stable writer-input tuple. The field dump did not directly join each
target post-value to one tuple, so `H-PhaseJoinMissing` remains open only for
the finer producer/result join. Evidence is in
[M5-S3435-FREQUENCY-CONTRACT.md](M5-S3435-FREQUENCY-CONTRACT.md).

Session 3436 added the port-side frequency-contract witness after the retail
ground-truth attempt. The oracle whole-RDRAM control and both title origins
fired, but watched-PC output flooded the capture and it was SIGKILLed before
final summaries; Session 3435 remains the qualified retail field-family
source. The fresh-build port image route reached title and hangar with phase
and image-stage controls live, no crash/abort markers, and 256 bounded witness
rows. All rows were in origin `0x00790400`; the port set had 107 distinct
tuples and no exact intersection with the 6,825 distinct retail field-dump
tuples. This does not select a missing port tuple family because retail
`0x800331E0` is inside `osRecvMesg`, while the port witness is at the host
`osRecvMesg_recomp` entry. It selects `H-PhaseJoinMissing` for this instrument
and leaves port tuple parity unevaluable. Evidence is in
[M5-S3436-PORT-FREQUENCY-CONTRACT.md](M5-S3436-PORT-FREQUENCY-CONTRACT.md).

Session 3437 repeated the frequency-contract comparison at the actual common
`osRecvMesg` entry `0x800331D0`. Retail passed the whole-RDRAM control, both
title-origin phase gates, and retained 7,815 field rows. The fresh-build port
image arm reached title and hangar with phase, image-stage, RSP-source, task,
and PCM controls live and no crash/abort markers; it retained 107 distinct
normalized tuples. The exact intersection over
`s0,s1,source_word,source_byte,branch_selector,branch_state` was zero. This
selects `H-PortTupleFamilyMissing` at the common entry boundary and refutes
`H-PortTupleFamilyMatch` plus the prior interior-PC/entry-boundary mismatch
explanation. The missing input/dispatch producer remains unidentified and no
audio behavior changed. Evidence is in
[M5-S3437-FREQUENCY-ENTRY.md](M5-S3437-FREQUENCY-ENTRY.md).

Session 3438 qualified the earlier caller boundary after first running the
independent retail oracle with the whole-RDRAM control. Retail reached both
title origins and produced 7,806 unique normalized rows at `0x800331D0`. The
fresh-build port image arm used the validated LLE/spin-yield route, reached
title 1024 and hangar 512 with task/RSP/PCM controls live, and emitted 256
caller rows plus 107 unique tuples at generated `osRecvMesg` callsites. The
wrapper emitted the same 107 tuples; the caller/wrapper intersection was 107,
but the port caller/retail intersection was zero. This selects
`H-EarlierPortInputGap` and refutes `H-PortWrapperContractGap` and
`H-EarlierBoundaryUnevaluable` at the observed scope. It does not identify
the earlier producer or establish tuple legitimacy. Evidence is in
[M5-S3438-FREQUENCY-CALLERS.md](M5-S3438-FREQUENCY-CALLERS.md).

Session 3439 ran the independent retail oracle first with a whole-RDRAM
positive control, both title origins, hangar, and the four selected
predecessor PCs. The control reached 10,000 callbacks; the PCs executed
`12,652/11,527/1,504/5,407` times for `0x80001B04/0x80001CB8/0x80006EFC/0x80006F5C`.
The fresh-build port route reached title and hangar with phase, caller,
wrapper, and image-stage controls live and no crash/abort markers. A new
phase-scoped `osSendMesg_recomp` census reached its 512-row budget: 486 rows
used queue `0x8010FEE0`, and 490 of 512 published message value zero. The
producer and receive schemas were not like-for-like, and retail had no send
publication table, so the exact requested producer/caller/retail tuple join is
unevaluable. This selects `H-EarlierBoundaryUnevaluable` for this census and
leaves the earlier input gap open; it does not establish that the zero
publication is illegitimate. Evidence is in
[M5-S3439-FREQUENCY-PRODUCER.md](M5-S3439-FREQUENCY-PRODUCER.md).

Session 3440 qualified the selected send/receive queue boundary. Retail's
whole-RDRAM control reached 10,000 writes, `0x80033410` fired 169,394 times,
and 12,534 phase-qualified rows used queue `0x8010FEE0`, all normalized as
`(queue=0x8010FEE0,msg=0,flag=0)`. The fresh-build silent/image port pair
reached title 1024 with controls live and no crash/abort markers. Port had 486
matching target sends and 512 target receives; every consumed queue-head
message was zero. This selects `H-RetailSendParity` and refutes
`H-EarlierPortSendGap` at the queue contract. Zero is not treated as
illegitimate; the remaining boundary is downstream receive-consumer/output
use. Evidence is in
[M5-S3440-SEND-RECEIVE-JOIN.md](M5-S3440-SEND-RECEIVE-JOIN.md).

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).

1. Trace the post-receive consumer/output edge selected by Session 3440. Join
   the phase-scoped `0x8010FEE0` receive rows to the first generated consumer
   PCs after `osRecvMesg`, beginning with high-count routes
   `0x80001B04`, `0x80001CB8`, `0x80006EFC`, and `0x80006F5C`. The
   discriminator is matching retail downstream state, an immediate port
   state divergence, or an unevaluable consumer edge despite live controls.
   Keep waits, slots, clear behavior, and PCM writeback unchanged.
2. The direct `setDisplayMode` audio callsite boundary is closed for the
   count: retail and port both pass `a1=0x12` at observed `0x8008EBC0`, though
   other arguments differ; neither exposes `0x5622`.
   The `0x8008EA78` route was absent in both qualified target-phase captures.
3. The direct `initN64RspMixer` callsite boundary is closed: both retail and
   port use `0x80091D14` on the qualified route. The
   `allocateSongChannelArray` entry/first-malloc boundary and the
   init-to-allocate edge are closed at their observed scopes. Port `a1=0x5622`
   is supplied immediately before the allocate call, while retail supplies
   `0x561F`; the callee does not mutate the value at either observed entry.

M5 Step 3 remains gated until a like-for-like target row names one missing image
task/output contract edge. Configured-host PatchesLib validation is an open
dependency only; this Unix checkout lacks the MIPS toolchain and generated
patch input, so do not repeat the local missing-target check.

Closed or parked work:

- The task-start guest-pointer guard is landed and runtime-validated on the
  title/hangar route; the task-pointer class is closed.
- The callback-table source/target qualification is closed: port matches the
  retail guest chain `0x800919D4 -> 0x800919EC -> 0x80007910`; unresolved
  indirect consumer/output behavior is subsumed by the active PCM boundary.
- The B1C source census, generated free-list-walk class, and generated-symbol
  renaming campaign are closed at their measured scopes.
- Keep external retail-entry, hangar `0x8000` Y/accumulator arithmetic, and
  M5 SP-yield/MORT publication threads parked pending a new discriminator.
- The corrected MORT descriptor edge is `+0x190` to
  `dmaVoiceSampleAndSignal`.

Session 3408's independent oracle run passed the whole-RDRAM control and
reached title/hangar. The watched port candidate `0x800052C4` executed 3,728
times, including 1,274 and 1,663 executions in the two hangar origins. Retail
target-span writer histograms and post-store samples were live and nonzero in
those same phase buckets, but `0x800052C4` was not a direct target-span store
PC. Combined with s3407's port rows, this selects `H-PortBoundaryDifferent`
and refutes a missing retail execution boundary at that PC. It does not yet
join the port call to the target payload or explain the zero PCM source.
Evidence is in [M5-S3408-PORT-BOUNDARY-ORACLE.md](M5-S3408-PORT-BOUNDARY-ORACLE.md).

Session 3410 completed the field-input join after first correcting the oracle
physical address and then adding route ordinal/row capture to the port input
witness. Retail's corrected arm passed the whole-RDRAM control (11,836
writes), reached title/hangar, wrote slot `0x149764` six times, and wrote the
target span 1,830 times; its target post-value control contained 189 nonzero
samples from `0x800078EC`. The paired port arms both reached title 1024 and
hangar 512 without crash/abort markers and passed ABI/DMA controls (1211/1218
rows); the input witness stored `0x801797B0` in both arms at hangar and joined
the active route (ordinals 1187 and 1186 respectively). The target clear at
`0x8008F2CC` joined the same port ordinal, with `dst=0x801797B0`,
`len=0x298`, and zero fill. Image stage 3 then consumed that target field at
`0x801797B0` and copied zero DMEM to `0x801798B0`; silent had no image-stage
rows as expected. This selects `H-PortField348ClearIsExpected` and refutes
`H-PortField348InputMismatch` at the observed hangar route. It also closes
`H-PortField348JoinGap` for the input-to-clear edge, while leaving the
downstream missing nonzero producer/PCM source unresolved. Evidence is in
`scratch/agent/s3410_retail_field348_ground_truth/correct-result.txt` and
`scratch/agent/s3410_m5_field348_input_join/`.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and related defenses are safety mechanisms, not explanations.
Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control, a
phase-scoped budget, and two independent lines of evidence before promotion.
Phase-gate animated comparisons on VI transitions. Batch all A/B arms in one
build and run. A null without a positive control is worthless.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches in the same
iteration. Never run submodule update, checkout, clean, or hard reset commands.
Kill runs with SIGKILL and run from `build/`. A mitigation-shaped change needs
an `ORIGIN:` line naming the writer and stating whether its value is legitimate.

CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. The strong
SP-task override and completion-aware `osSpTaskYielded` contract are the
current defaults; request-only behavior is an explicitly superseded diagnostic
arm. Static boundary-only symbol classifications remain non-renames without
defensible semantic evidence.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield interpretation and viewer-stall chain from sessions
3288–3302 describe only the old diagnostic arm. Session 3304's
completion-aware default returns the viewer, so those findings are not the
current default explanation.

The session-3402 attribution that `0x8002BEEC` is the retail JAL dispatch to
`0x800078EC` is superseded as a current oracle target. It was believable
because earlier captures reported execution there, but the same validated
120-second route plus an adjacent-PC corrective capture found zero executions
at both `0x8002BEE8` and `0x8002BEEC` while `0x800078EC` was live. The earlier
route-dependent attribution remains unreconciled rather than discarded.

The old interpretation of the 1,578-entry cinematic dispatcher pool as an
audio-slot pool was superseded by the actual MusyX voice-table measurement:
title/hangar reachability is valid and the voice mask is zero/max=1.

The old `H-PtrZeroSkip`/cinematic loop findings remain descriptive of the
port/retail parity boundary, but do not justify forcing state; the skip-allow
writer and initializer ordering are the measured explanation.

## Evidence index

Latest M5 evidence:

- `docs/M5-S3409-052C4-JOIN.md`
- `docs/M5-S3433-FREQUENCY-PHASE.md`
- `docs/M5-S3434-FREQUENCY-WRITER.md`
- `docs/M5-S3435-FREQUENCY-CONTRACT.md`
- `docs/M5-S3420-RETAIL-ENTRY-ARGS.md`
- `docs/M5-S3426-INIT-MIXER-CALLER.md`
- `docs/M5-S3413-RETAIL-SOURCE-SPAN.md`
- `docs/M5-S3402-SLOT-PREPHASE.md`
- `docs/M5-S3401-FIELD348-INPUT.md`
- `scratch/agent/s3386_m5_direct_writer_census.md`
- `docs/M5-S3393-LOWER-NOISE-TARGET-ATTRIBUTION.md`
- `docs/M5-S3398-STAGE3-DESTINATION.md`
- `docs/M5-S3394-DUAL-ORIGIN-ATTRIBUTION.md`
- `docs/M5-S3389-PREDECESSOR-EDGE.md`
- `scratch/agent/s3376_m5_zero_pcm_source.md`
- `scratch/agent/s3379_m5_source_writer.md`
- `scratch/agent/s3375_m5_port_pcm_writer.md`
- `scratch/agent/s3374_m5_retail_pcm_writer.md`
- `scratch/agent/s3373_m5_consumer_output_contract.md`
- `scratch/agent/s3372_m5_status03_port_contract.md`
- `scratch/agent/s3369_m5_status03_worker_contract.md`
- `scratch/agent/s3364_m5_port_callback_edge.md`

Session 3400 enabled the existing field348 writer/candidate/memset and static
`rs_memset` caller probes in the fresh-build contract pair. Retail again passed
whole-RDRAM, title, hangar, and checkpoint controls; its `0x1935E0` checkpoint
had 18 retained post-store samples, including 12 nonzero writes from
`0x800078EC`. Both port arms reached hangar without crash/abort. The image arm
consistently supplied `field348=0x801797B0`; that span was zero-valued
(`25E26BC5`, `nz=0`), initialized by the target zero-fill at `0x8008F2CC`
(`dst=0x801797B0`, `len=0x298`), and written only with zero bytes by
`0x800078EC`. Stage 3 copied zero DMEM `0xCB0..0xE48` to `0x1798B0`
(`762B22A5`, `nz=0`) while DMA/exit, guest service, and PCM controls were
live. This selects `H-PortStage3Field348ProducerGap` for the observed content/
producer contract and refutes address alias and legitimate-zero explanations
against the retail publication. The input preceding the zero-fill remains
unresolved; no audio behavior changed. Evidence is in
[M5-S3400-FIELD348-PRODUCER.md](M5-S3400-FIELD348-PRODUCER.md).

Session 3401 added the durable `0x8008F2C8` caller-input witness and rebuilt
successfully. The retail oracle controls passed in both qualification attempts.
The first attempt reached hangar only in the image arm; the silent arm crashed
at `spTaskSchedulerThread+9536` / guest PC `0x8000834c`. The retry reached
hangar only in the silent arm and the image arm crashed at the same boundary.
In the two valid individual arms, the witness fired positively and repeatedly:
slot `0x80149764` stored `0x80178C80` at title 1024 and `0x801797B0` at hangar
512. Because no attempt had both arms phase-qualified, the discriminator is
unevaluable; no hypothesis is selected and no audio behavior changed. Evidence
is in [M5-S3401-FIELD348-INPUT.md](M5-S3401-FIELD348-INPUT.md).

Session 3402 ran a retail-oracle-only capture watching slot `0x149764:0x149768`
with whole-RDRAM positive control, title/hangar phase gates, and `0x1935E0`
post-value control. All controls passed (10,046 callbacks, 633 title VI, 1,316
hangar VI, 40 `0x1935E0` hits). Slot `0x149764` had 6 writes total from
`pc=0x8008F2C8`, all storing `0x801797B0` (fnv=`0x380f190b`), all occurring
before the first phase gate (0 during title-1024, 0 during hangar-512).
Combined with s3401's port witness, this gives two independent lines:
- `H-PortStage3OwnerAbsent` REFUTED: retail writes slot 6 times pre-phase.
- `H-PortStage3Field348ProducerGap` SELECTED for title-1024: port stores
  `0x80178C80`; retail stored `0x801797B0` pre-phase.
- `H-PortStage3DownstreamGap` SELECTED for hangar-512: both store `0x801797B0`
  but port PCM is zero. The gap is in the dispatch of `0x8002BEEC` (JAL to
  `0x800078EC`), which fires 37,635 times in retail and 0 times in the port.
  The slot-level investigation is closed for hangar-512. Evidence is in
  [M5-S3402-SLOT-PREPHASE.md](M5-S3402-SLOT-PREPHASE.md).

Session 3403 ran the prescribed retail `--watch-pc 0x8002BEEC` probe for 60
seconds with whole-RDRAM, title/hangar, and `0x1935E0` controls. The oracle
reached title 1024 (632 VI) and hangar 512 (397 VI); the positive control
reached 10,000 callbacks and the secondary PCM control fired 40 times. The
caller watch had zero execution hits and no `exec-prev` rows. Because the
secondary path was only lightly active in this shorter route, this is a valid
instrument null but not a dispatch discriminator: it selects none of
`H-Dispatch-DirectCaller`, `H-Dispatch-IndirectCaller`, or
`H-Dispatch-BootOnly`. A longer same-route capture is required before adding
port caller instrumentation. Evidence is in
`scratch/agent/s3403_retail_8002beec_caller/oracle.log`.

Session 3404 extended the retail `0x8002BEEC` watch to 120 seconds and ran a
corrective adjacent-PC watch set. Both runs passed whole-RDRAM, title/hangar,
and PCM controls. The target `0x8002BEEC` and predecessor `0x8002BEE8` were
both zero, while `0x800078EC` executed 9,699 times; the only `exec-prev` row
was a self-reentry row for `0x800078EC`. This selects a stale target-address
explanation for the current oracle route and refutes the three caller-shape
hypotheses at `0x8002BEEC`; the earlier 37,635 attribution remains
unreconciled. No audio behavior changed. Evidence is in
[M5-S3404-PCM-DISPATCH-ADDRESS.md](M5-S3404-PCM-DISPATCH-ADDRESS.md).

Session 3405 repeated the completion-safe 120-second retail census with the
known producer, the earlier `0x80033300` candidate, both adjacent producer
sites, whole-RDRAM, title/hangar, and `0x1935E0` controls. All controls passed:
10,040 whole-RDRAM writes, 40 target-span writes, title histogram VI 632, and
hangar histogram VI 972. `0x800078EC` had 9,699 execution hits; every
`exec-prev` row was `prev=0x800078EC`. `0x80033300`, `0x800078E8`,
`0x8002BEE8`, and `0x8002BEEC` each had zero hits. This selects
`H-ProducerSelfLoopOnly` for the watched candidate set and refutes a live
direct or adjacent external caller at those addresses in this route. It does
not reconcile the earlier `0x8002BEEC` attribution or identify the external
dispatch site. No port instrumentation or audio behavior changed. Evidence is
in `scratch/agent/s3405_retail_pcm_dispatch/oracle.log`.

Baseline and independent boundary evidence remains indexed in the ledger and
PROJECT-OVERVIEW section 54. Use bounded `grep`/ `sed` windows for
PORTING-STATE.md; never read it wholesale. The soak queue is consumed by
automation; fold only new tail lines into the next audit.

Session 3406 scanned the retail ELF across main and all overlay sections and
found 88 direct JAL sites to `rs_memset`; `0x8002BEEC` is not a direct JAL
(`0x42000018` there). The focused independent oracle arm passed its controls
(10,010 whole-RDRAM writes, 10 target writes, 1,281 hangar VI rows), observed
`0x8002BEEC` 191,046 times, and recorded
`exec-prev pc=0x800078EC prev=0x8002BEEC n=177`. No direct candidate was an
observed producer predecessor. This selects `H-IndirectDispatch` at the
measured boundary and refutes `H-StaticCallsite` and `H-RouteMismatch`; the
predecessor-field/static-instruction reconciliation remains open. Evidence is
in [M5-S3406-RETAIL-PRODUCER-DISPATCH.md](M5-S3406-RETAIL-PRODUCER-DISPATCH.md).

Session 3407 ran the port producer-boundary witness after an initial
concurrent attempt hit the known pre-phase scheduler crash. The fixed
sequential qualification passed title 1024 and hangar 512 in both silent and
image arms, with no crash/abort markers. The phase-qualified static-call
witness produced 512 silent and 1024 image rows; image hangar rows were
dominated by callsite `0x800052C4` (508), with one each at `0x8008F2CC`,
`0x800B33BC`, `0x800B3490`, and `0x800B3500`, and zero rows at `0x8002BEEC`
or `0x800078EC`. This selects `H-PortBoundaryAbsent` at the measured port
witness and refutes a matching port predecessor relation there. The host
witness cannot distinguish an indirect predecessor from another translated
route, and target PCM payload remains zero. Evidence is in
[M5-S3407-PORT-PRODUCER-BOUNDARY.md](M5-S3407-PORT-PRODUCER-BOUNDARY.md).
