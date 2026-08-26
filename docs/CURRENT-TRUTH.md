# Rogue Squadron 64 Recomp — current truth

Operational front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
history through s2357 is archived in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md)
§48; the append-only ledger remains authoritative for exact commands, counts,
and probe rows.

Current maintenance marker: Session 2393 (2026-08-25).

Maintained in Session 2392 (2026-08-25). The corrected M5 task-reporter audit passed all four route controls. Raw `[audtask-join]` records were phase/event-contained for every image-stage candidate: 2,340/2,340 and 2,348/2,348; reporter `complete=1` on 2,150/2,143 rows. The s2388 source audit shows `complete` is a same-range-both predicate, not an aggregate-count or ordering predicate. Among the 411 incomplete rows (232/179), 331 had neither source nor consumer, 38 source-only, 42 consumer-only, and none had both; ordering flags varied only with the one-sided matches. The s2389 range audit found task-reporter selections for 1,454/1,432 title-stage rows, but zero image-stage selections because every relevant stage had `stage_nz=0`, which the image matcher explicitly rejects; there were zero same-range agreements and zero conflicts. The s2390 retained-field audit confirms target-stage zeros in both image arms (1,424/1,421 unique rows), with only two positive rows in one hangar arm; all controls pass. The s2391 retail oracle payload-region capture passed the whole-RDRAM, title, and hangar controls and found 57,871/102,400 final nonzero bytes in the broad candidate region, with phase-gated writer PCs, but no exact per-stage payload bytes or one-to-one port hash join. The s2392 exact-window capture passed the whole-RDRAM control (`12,962` writes), title and hangar VI controls, and exact watches. Window `0x1935E0:0x198` had target-phase writers and a nonzero final snapshot (`186/408`, FNV `0xE2F69C77`) while the retained port stage is `stage_nz=0`, FNV `0x762B22A5`; the other exact windows also ended nonzero but lacked sufficient phase-specific attribution. This selects `H-StageNonzeroLoggingArtifact` at capture scope, not a legitimate-zero or exact PCM-representation conclusion. No task-data, audio, gate, fallback, dispatch, VI, or output behavior change is authorized.

The s2384 completion-producer capture remains valid: image arms emitted 1,147 and 1,022 target-phase completion-call rows, and their stage candidates carried matching completion events, including event `18` for the first image candidate. This selects `H-CompletionProducerCalledAndAssociated` at capture scope and closes the completion-event null; it does not explain task completion or PCM closure.

The s2383 same-build task/output candidate census passed all four route controls. It retained 4,342 phase-keyed image-stage candidates across c88=0/1 image arms; stage/render events were present, but every candidate lacked a completion event/bit and a task DMA-count join, and none had PCM source or consumer events. Stub arms had no image candidates as expected. This narrows `H-TaskOutputGap` to `H-CompletionEventMissing` at capture scope; it does not authorize changing task data, audio, gate, fallback, or publication behavior.

The s2382 same-build M5 downstream capture passed all four route/phase controls. The c88=1 arms joined 124/125 gate fallthroughs and 118/116 key-on rows, but all four arms had zero task-completion joins and zero PCM source/consumer joins; image arms still produced 2,270/4,235 task-DMA ranges and 2,271/2,344 render rows. This selects `H-TaskOutputGap` at capture scope: gate polarity and intermediate downstream work are present, while task completion/output closure is absent. No audio contract or gate change is authorized.

The s2381 corrected M5 gate-writer oracle capture passed whole-RDRAM (`10,017`),
target 640, title 1024, and hangar 512 route controls. Gate `0x800A0F50` had
17 writes; sampled values were `0x00000000` (4) and `0x01000000` (2), with
`0x8008EC88` producing both sampled nonzero stores. Target-phase writer PCs
were `0x8008EB7C`/`0x8008EC88` for origin `0x00696100` and `0x8008ED48` for
`0x00696600`. This selects `H-RetailGateWriterObserved` at capture scope and
provides independent writer/value evidence for the existing `reapplyDisplayMode`
polarity; it does not authorize changing the gate or any audio contract.

The s2372 predecessor capture remains valid: retail's target-phase
`0x80001F84` row had `$a0=1,$a2=0`, while both port arms had
`$a0=0x8010FEE0,$a2=0` before the same null request. The s2373 entry rows
show that retail's `$a0=1` is not its `rs_free` entry argument; it is produced
before the predecessor return. The port entry `$ra` probe is uniformly zero,
so it does not identify the caller. No fallback, dispatch, VI, task, or audio
contract change is authorized.

The M5 A1 pre-target capture passed
the oracle and both early-640 port controls; both arms requested the null
function address before target origin. The resident table contained only
sections 0, 1, and 3, none containing address zero. This selects a missing or
null function request at capture scope, not resident-overlay wrong dispatch.
The first driver attempt was invalid because zsh stored literal `$!` PID
values; the fixed scalar-PID driver reran the same build and arms.

The s2370 A1 origin capture passed the oracle whole-RDRAM, target-origin, and
watch-PC controls. Retail produced zero execution rows for `0x80001F88` in
the target route, while both same-build port arms reached that guest PC and
requested `0x00000000`. This selects `H-RetailCallsiteAbsent` at capture
scope: the port reaches a null-function call site retail does not reach in the
captured phase. It does not identify the preceding branch/input divergence or
authorize a null fallback, dispatch change, VI change, or audio contract edit.

The s2371 M5 A1 predecessor capture passed the oracle whole-RDRAM, both target
origins, and range-watch positive controls. Retail executed the bounded
`0x80001F40..0x80001FA0` window 230,902 times overall and the target 640
origins produced 19,196 rows, including 2,408 at `0x80001F84`, immediately
before the port's `0x80001F88` last-guest-PC marker. Both port arms again
reached the same phase-4 null request and resident table. This selects
`H-RetailPredecessorPresent` at capture scope and rules out
`H-RetailPredecessorAbsent`; the port-side `$a0/$a2` values were not captured,
so `H-RetailPredecessorMatches` versus `H-RetailPredecessorArgsDiffer` remains
open. No dispatch, VI, fallback, task-data, or audio contract change is
authorized.

The M5 A1 second-origin capture passed
retail whole-RDRAM and both target-origin controls, but both same-build port
arms aborted in `get_function` before reaching either target origin; no A1
publisher comparison is valid. The M5 payload-owner join passed all
route and execution controls and placed both target-stage rows inside a
containing audio task; no audio contract change is authorized. The M5
retail writer-source capture
passed its controls and found a direct task relation in every target phase:
`$s1 == data_ptr+0x100` at the exact task-field writer counts, with repeated
`$a2 == data_ptr` rows. The source join is phase/field scoped because the
oracle's execution GPR rows do not carry an exact VI; no port contract change
is authorized.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The old boot/menu-overlay explanation is closed.
- The qualified route is
  `ROGUESQ_LLE_FORCE=1`, `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is gated and
  default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation requires a named writer, a
  legitimacy judgment, and an `ORIGIN:` line.
- M5 defaults to the Factor 5 image arm. `ROGUESQ_AUDIO_UCODE=0` selects the
  silent `M_AUDTASK` `Broke` stub used for controls. The image arm performs
  real DMEM work, returns `Broke`, emits generated DMA, and can publish PCM;
  its host canary is probe data only. Stock `aspMain` is not this game's
  contract. MORT is a separate CPU speech asset.
- `docs/M5-AUDIO-PLAN.md` is the design gate for incremental audio
  de-stubbing. The current measured boundary is retail task-field writer
  source/payload relation; no port contract change is authorized.
- The independent retail oracle is the witness for game-side memory claims.
  Its whole-RDRAM, target-window, phase, status/task, and named-PC controls
  must pass before a retail null is interpreted. It reaches attract, title,
  and hangar, not a mission.
- The M5 task ABI address relation is independently real: retail type-2 tasks
  point at the watched field set through `data_ptr+0x100`. Retail PC
  `0x80090CA4` then stores nonzero values at every task-matched phase/field key
  in the s2359 capture, but 910 comparable values mismatch the retained s2352
  port field payload and none match. This is a payload/source discriminator,
  not permission to alter task data or port writeback.
- The M5 retail writer-source relation is positive at phase/field scope: the
  exact task field is present in `$s1` for all four task-matched writer buckets,
  while `$a2` repeatedly carries the matching task `data_ptr`. The oracle does
  not join those GPR rows to an exact writer VI, so this selects a source class
  without authorizing a port writeback or task-data edit.
- The s2361 same-build stub/image validation was route-valid for both arms. The
  stub was a true no-op (`dmem_changed=0`, no DMA, canary preserved); the image
  arm changed DMEM and emitted two destination DMAs per task. Its bounded
  table had two target-stage rows but zero same-task pre/post joins. s2362
  superseded that local timing label by joining stages to containing task
  boundaries; no port contract change is authorized.
- The s2362 expanded timing table is route-valid for both arms and contains
  two target-stage rows. Both rows fall inside task ordinal 0 and have task
  ordinal 1 as the next task; no earlier task exists in the retained scope.
  The previous zero same-task event result was a join-window/ordinal artifact,
  not evidence that the stage preceded all task work. This selects
  `H-StageInsideTask` at capture scope; it does not identify a legitimate
  output writeback or authorize a contract change.
- The s2363 same-build stage/output table passed oracle, route, VI, ABI,
  filter/voice, and image-stage controls. Both target rows matched the
  containing task's DMA start, length, payload hash, and nonzero count, but
  the containing task records had `complete=0`, `source_matches=1`,
  `consumer_matches=0`, and no nonzero task-window PCM rows. This selects
  `H-ContainingTaskInternalOnly` at capture scope: stage/DMA closure exists,
  while completion and output/PCM closure do not. No port contract change is
  authorized. Artifacts: `scratch/agent/s2363_m5_stage_output_contract_join_final/`.

## Latest evidence

- **s2393 — exact port byte capture was route-invalid.** The build added a
  bounded pre-join capture for `0x167050:0x300`, `0x1935E0:0x198`, and
  `0x166D50:0x300`, including a 16-byte sample and recomputed nonzero/FNV
  tuple. The first qualified image run stayed at VI 640 despite active VI
  updates and emitted zero stage rows. A fixed run with drain/route controls
  crashed at guest PC `0x80001F88`, still at VI 640, also with zero stage rows
  and zero byte captures. This selects `H-PortStageCaptureInvalid` for the
  iteration and leaves all stage-byte hypotheses open. Artifacts:
  `scratch/agent/s2393_stage_bytes_run2/`,
  `scratch/agent/s2393_stage_bytes_run3/`.

- **s2392 — exact retail windows are active where the retained port stage is
  zero.** The first capture covered only one alternating VI origin; the fixed
  capture added both title origins (`0x790400/0x790800`) and both hangar
  origins (`0x6ab400/0x6ab800`). The whole-RDRAM positive control recorded
  `12,962` writes and the run reached title and hangar. Exact watch
  `0x1935E0:0x198` had target-phase writers at title (`0x800078EC`, 408
  writes) and hangar (`0x80018F5C`, 103; `0x80018F60`, 99); its final snapshot
  was `186/408` nonzero, FNV `0xE2F69C77`, versus the retained port stage's
  `stage_nz=0`, FNV `0x762B22A5`. Exact windows `0x167050:0x300`,
  `0x166D50:0x300`, and `0x178D80:0x198` ended `765/768`, `759/768`, and
  `20/408` nonzero respectively, but had no phase-hist writer rows. The
  independent oracle/port comparison selects `H-StageNonzeroLoggingArtifact`
  at capture scope; it does not identify whether the port logger region,
  payload representation, or stage join is wrong. Artifact:
  `scratch/agent/s2392_oracle_exact_stage_windows/`.

- **s2386 — raw task reporter association is positive.** The build succeeded
  and the same-built stub/image × c88=0/1 driver passed title `1024` and
  hangar `512` controls in all four arms, with no crash or abort. The
  corrected phase/event interval table matched raw `[audtask-join]` records
  to every image-stage candidate: image c0 `2,340/2,340` and image c1
  `2,348/2,348`; reporter `complete=1` counts were `2,150` and `2,143`.
  Source/consumer matches were present on `2,186/2,188` and `2,153/2,151`
  rows. This selects `H-TaskReporterAssociated` at capture scope, refutes
  `H-TaskReporterUncalled` and `H-TaskReporterKeyMismatch`, and supersedes
  s2385's reducer-based task/output-gap label. Artifact:
  `scratch/agent/s2386_m5_task_reporter_boundary/`.

- **s2387 — incomplete reporter rows are mostly stage-only.** The same-build
  four-arm driver passed title `1024` and hangar `512` in every arm, with zero
  crash/abort markers. Filtering only raw `[audtask-join]` rows with
  `complete=0` retained 232 image c0 and 179 image c1 candidates; stub arms
  retained none. The dominant pattern was no source and no consumer match
  (166/165), with source-only (36/2) and consumer-only (30/12) minorities;
  no retained row had both. This selects `H-IncompleteStageOnly` at capture
  scope and rules out a single missing-consumer or missing-source explanation.
  It does not authorize a task-data, audio, gate, fallback, dispatch, VI, or
  output change. Artifact: `scratch/agent/s2387_m5_incomplete_reporter/`.

- **s2388 — reporter completion is same-range-both.** The retained s2387
  four-arm logs passed the existing title/hangar controls and were reduced
  against the raw reporter records. The reporter implementation sets
  `complete` only when a single DMA range has both `source_pcm` and
  `consumer_pcm`; aggregate source/consumer totals and ordering flags do not
  set it. The 411 incomplete candidates were no-match `331`, source-only
  `38`, consumer-only `42`, and both-match `0`. This selects
  `H-PredicateRequiresSameRange` for the reporter label, refutes
  `H-PredicateGlobalCounts` and `H-PredicateOrderingOnly`, and leaves
  `H-PredicateReducerMismatch` open only for any future independent reducer
  disagreement. Artifact: `scratch/agent/s2387_m5_incomplete_reporter/`.

- **s2389 — reporter and image-stage range policies meet no image-stage row.**
  The retained four-arm logs passed title `1024`, hangar `512`, and zero
  crash/abort controls. Reimplementing the task reporter's exact first-unused
  range matcher selected PCM ranges for `1,454` image c0 and `1,432` image c1
  title-stage rows. Reimplementing the image matcher selected zero rows in
  every arm/phase because every relevant stage had `stage_nz=0`, while the
  implementation requires nonzero stage data. There were zero same-range
  agreements, zero differing-range conflicts, and no multiplicity result.
  This exposes the image-stage nonzero predicate as the next boundary; it does
  not authorize a contract or runtime change. Artifact:
  `scratch/agent/s2387_m5_incomplete_reporter/`.

- **s2390 — retained image-stage nonzero audit.** The fixed reducer passed
  controls for stub c0/c1 and image c0/c1 (`controls=1`, zero crash/abort).
  Across unique stage events, target image rows were all `stage_nz=0`
  (`1,424` c0 and `1,421` c1); the only positive values were two hangar rows
  in image c0. No exact stage/PCM range agreement was present. The retained
  records expose hash, length, and nonzero fields but not payload bytes, so a
  byte-level positive-control recomputation is unavailable. This selects
  `H-StageNonzeroLegitimate` only for the logged-field fact, while leaving
  `H-StageNonzeroLoggingArtifact` and `H-StageNonzeroPcmMismatch` open. It
  does not authorize a predicate relaxation or any task/audio/output change.
  Artifact: `scratch/agent/s2387_m5_incomplete_reporter/`.

  ORIGIN: no mitigation or behavior change; added only a bounded retained-log
  audit and its output.

- **s2391 — retail candidate region is active but the broad payload witness is
  not exact.** The first oracle attempt failed before launch because the
  documented `build/Debug/rogue_squadron.z64` path is absent; the corrected
  run used the present `build/rogue_squadron.z64`. Whole-RDRAM control reached
  `21,381,891` writes, title and hangar phase buckets were observed, and the
  candidate range `0x167000:0x180000` received `21,371,891` retail writes.
  Its final snapshot had `57,871/102,400` nonzero bytes. Hangar-phase writer
  PCs included `0x80090F8C`, `0x800923B8`, `0x80090268`, and `0x800908D4`.
  Because the range contains many unrelated fields and the snapshot is not
  per-stage or per-length, this is independent evidence that the retail
  region is active, not a payload-level match to the port's zero stage rows.
  `H-StageNonzeroLegitimate`, `H-StageNonzeroLoggingArtifact`, and
  `H-StageNonzeroPcmMismatch` remain open; no predicate relaxation or output
  change is authorized. Artifact:
  `scratch/agent/s2391_oracle_stage_payload.log`.

  ORIGIN: no mitigation or behavior change; added only a ground-truth watch.

- **s2382 — gate/downstream path is positive but task/output closure is absent.**
  The same-build driver passed controls for stub c0/c1 and image c0/c1; each
  reached title 1024 and hangar 512. The c88=1 arms had three gate writers,
  `stored_nonzero=2`, `fallthrough_joined=124/125`, and `keyon_joined=118/116`.
  Across all arms `task_complete=0`, `pcm_source_joined=0`, and
  `pcm_consumer_joined=0`; image c0/c1 nevertheless had `task_dma_ranges`
  `2270/4235` and `render_rows` `2271/2344`. This selects
  `H-TaskOutputGap` at capture scope, rules out a route-invalid or wholly
  pre-gate explanation, and does not authorize changing the gate, task data,
  audio contract, fallback, or output publication. Artifact:
  `scratch/agent/s2345_m5_c88_downstream_ordinal_join/ordinal-summary.tsv`.

- **s2379 — retail call/return is positive, but the delay-slot flag is not
  observable through the oracle breakpoint.** The fresh oracle run passed the
  whole-RDRAM positive control (`10,000` writes), observed both target 640
  origins, and recorded `8,510` executions each at `0x80001CB8` and
  `0x80001CC0`. Every successor row had `prev_pc=0x80033300`; the call rows
  had `prev_pc=0x80001CB4`. The requested delay-slot watch at `0x80001CBC`
  recorded zero hits, so the varying `$a2` values at `0x80001CB8` are the
  pre-delay register state, not proof of the flag passed after the delay-slot
  instruction. This selects `H-RetailCallReturnJoin` at capture scope, rules
  out `H-RetailLabelArtifact`, and leaves `H-RetailNonblocking` versus
  `H-RetailBlockingObserved` unresolved. The s2377 `$a2=0` observation must
  not be used as an effective-call contract. No behavior, fallback, dispatch,
  VI, task, audio, guard, or mitigation change was made. Artifact:
  `scratch/agent/s2379_m5_a1_retail_flag_semantics/`.

- **s2380 — retail callee entry receives a blocking flag.** The fresh oracle
  run passed the whole-RDRAM positive control (`10,000` writes), observed both
  target 640 origins, and watched the call, delay-slot address, `osRecvMesg`
  entry (`0x800331D0`), and successor. It joined `2,524` target rows by
  `prev_pc=0x80001CB8` at the callee and by the `0x80001CC0` successor; all
  `2,524` callee rows had `$a2=1`, while the call-site rows had `$a2=0` before
  the unbreakable delay slot. The delay-slot watch remained unhit, as
  expected from the debugger limitation. This selects
  `H-RetailBlockingObserved`, rules out `H-RetailNonblocking` and
  `H-RetailLabelArtifact` at capture scope, and closes the effective-flag
  work unit. It does not identify the upstream caller/input divergence or
  authorize changing the port flag, fallback, dispatch, VI, task, audio,
  guard, or mitigation. Artifact:
  `scratch/agent/s2380_m5_a1_retail_flag_semantics.log`.

- **s2378 — port `$a2=1` is generated, not host-translated.** The generated
  `rs_free` body explicitly sets `$a1=0` at `0x80001CB4`, calls
  `0x800331D0` at `0x80001CB8`, and executes delay-slot `addiu $a2,$zero,1`
  at `0x80001CBC` before `osRecvMesg_recomp`. Both the project override and
  the weak librecomp binding forward `ctx->r6` unchanged to the host
  `osRecvMesg`, whose `flags` parameter is then compared directly to
  `OS_MESG_BLOCK`. This selects `H-GeneratedFlag` and refutes
  `H-HostTranslation` at capture scope. The port call/marker join is positive;
  the companion retail body is `INCLUDE_ASM`, so the retail instruction source
  remains open and the label conclusion is single-source for the port side.
  No behavior, fallback, dispatch, VI, task, audio, guard, or mitigation
  change was made.

- **s2376 — generated `rs_free` boundary has no source-visible control-flow
  mismatch.** The generated body maps `0x80001CAC` to `lui $a0,0x8011`,
  `0x80001CB0` to `addiu $a0,-0x120`, `0x80001CB4` to `addu $a1,$zero,$zero`,
  and `0x80001CB8` to `jal 0x800331D0` with delay-slot `a2=1`. After the call,
  it reads the queue head and tests bit `0x8` at `0x80001CD4`; only the
  not-taken path reaches `0x80001CD8`. The companion project provides no C
  body for `rs_free` (`INCLUDE_ASM` only), while the s2375 port rows show the
  `0x80001CD8F` marker after the call. This selects
  `H-InputDependentPath` only for the available generated/runtime evidence,
  and leaves the retail-vs-port queue/return state open. It rules out a
  generated mismatch visible in the audited body, not the underlying writer
  or caller divergence. No behavior, fallback, dispatch, VI, task, audio,
  guard, or mitigation change was made. This is single-source for the body
  audit. Artifact: source audit only; s2375 capture retained.

- **s2377 — A1 queue state matches between port arms but the receive flag
  differs from retail.** The oracle passed whole-RDRAM, both target origins, and
  the `0x80001CB8` call-site controls. Retail target rows carry
  `$a0=0x8010FEE0,$a1=0,$a2=0`; its queue-field watch produced no writes and is
  unqualified. Both same-build port arms passed early-640, A1, and abort
  controls and each recorded 204 target-phase receives at queue `0x8010FEE0`
  with `msg=0`, `flag=1`, result `0`, and `validCount 1 -> 0`, `first=0`,
  `msgCount=1`, `msg=0x8010FEF8`. This selects `H-CallContractDiffers` at
  capture scope, rules out a port-arm-specific queue-state difference, and
  supersedes s2376's `H-InputDependentPath` label as an explanation of this
  boundary. It does not identify why the generated delay slot supplies `1` or
  authorize changing it. No behavior, fallback, dispatch, VI, task, audio,
  guard, or mitigation change was made. Artifacts:
  `scratch/agent/s2377_m5_a1_queue_boundary/` and
  `scratch/agent/s2377_ground_truth/`.

- **s2373 — `rs_free` entry/return boundary is positive and internally
  divergent.** The fresh oracle passed whole-RDRAM `10,000`, both target 640
  origins, and the predecessor/`rs_free` live execution controls. Retail
  produced `2,390` target-origin `rs_free` rows in the retained log; its
  entry rows carried ordinary heap pointers, while corresponding predecessor
  rows reached `$a0=1,$a2=0`. Both same-build port arms passed early-640,
  `[a1-args]`, and `[a1-abort]` controls, with `369/374` `rs_free` entries;
  the phase-4 sequence entered with ordinary heap pointers and returned with
  `$a0=0x8010FEE0,$a2=0`, and every shown `$ra` was zero. This selects
  `H-RsFreeInternalPathDiverges` at capture scope and rules out treating the
  retail predecessor `$a0=1` as the `rs_free` entry argument. The caller is
  still unidentified; no behavior change is authorized. Artifact:
  `scratch/agent/s2373_m5_a1_rs_free_boundary_fixed/`.

- **s2375 — `rs_free` internal control flow diverges after the shared prefix.**
  The fresh oracle passed whole-RDRAM `10,000`, both target origins, the
  predecessor range, and live entry controls. It retained `4,980` widened
  `rs_free`-entry rows and `2,489` predecessor rows. In target-origin rows,
  the retail sequence reaches `0x80001CAC`, `0x80001CB0`, then
  `0x80001CB4`; both same-build port arms passed early-640,
  `[rs-free]`, `[a1-args]`, and `[a1-abort]` controls and emitted the same
  internal sequence through `0x80001CB0`, then `0x80001CD8F` instead of the
  retail successor. This selects `H-RsFreeInternalWriteDiverges` at capture
  scope and rules out `H-RsFreeInternalMatches` and the prior join-invalid
  result. It identifies neither the writer/caller nor a legitimate fix; no
  behavior, fallback, dispatch, VI, task, audio, or mitigation change is
  authorized. Artifact:
  `scratch/agent/s2375_m5_a1_rs_free_internal_join/`.

- **s2374 — port internal `$a0` trace is positive but retail join-invalid.** The
  fresh oracle passed whole-RDRAM `10,000`, both target origins, predecessor
  range, and live `rs_free` entry controls. Both same-build port arms passed
  early-640, `[rs-free]`, `[a1-args]`, and `[a1-abort]` controls, and both
  emitted the same bounded internal sequence: ordinary entry pointer, the
  `0x80110000` message-queue argument, then `$a0=0x8010FEE0` at the internal
  `0x80001CD8` assignment. The oracle emitted no internal rows because its
  watch range began at `0x80001F40`; this selects `H-RsFreeJoinInvalid`, not
  `H-RsFreeInternalWriteDiverges` or `H-RsFreeInternalMatches`. Artifact:
  `scratch/agent/s2374_m5_a1_internal_a0/`.

- **s2372 — retail and port predecessor arguments differ.** The fresh oracle
  passed whole-RDRAM `10,000`, both target 640 origins, and the predecessor-PC
  control. It recorded `2,411` target-phase executions at `0x80001F84`, with
  target rows showing `$a0=0x00000001,$a2=0`. Both same-build port arms passed
  early-640 and emitted the phase-4 null request; their bounded predecessor
  rows showed `$a0=0x8010FEE0,$a2=0`. This selects
  `H-RetailPredecessorArgsDiffer` at capture scope and rules out matching
  predecessor arguments. It does not identify the writer/caller divergence or
  authorize a fallback, dispatch/VI change, or audio/task contract edit.
  Artifact: `scratch/agent/s2372_m5_a1_port_predecessor_args/`.

- **s2371 — retail executes the A1 predecessor window.** The fresh oracle
  passed whole-RDRAM `10,000` and both target-origin controls. The bounded
  predecessor range fired `230,902` times overall and `19,196` times in the
  target 640-origin rows, including `2,408` executions at `0x80001F84`.
  Both same-build port arms passed the early-640 control and emitted the same
  phase-4 `[a1-abort]` requesting zero, with last guest PC `0x80001F88` and
  three resident sections. This selects `H-RetailPredecessorPresent` and
  rules out `H-RetailPredecessorAbsent`; it is single-source for the
  retail/port argument comparison because the port abort row has no `$a0/$a2`.
  Artifact: `scratch/agent/s2371_m5_a1_caller_input_boundary/`.

- **s2370 — retail does not execute the port's A1 null-function call site at
  this capture scope.** The repaired same-build runner passed the oracle
  whole-RDRAM positive control (`10,000` callbacks), both target 640 origins,
  and the oracle watch-PC mechanism control. Retail produced zero execution
  rows for `0x80001F88` in the target route. Both same-build port arms passed
  the early 640 transition and emitted one `[a1-abort]` row at phase 4
  requesting `0x00000000`; both had the same three resident sections, none
  containing address zero. This selects `H-RetailCallsiteAbsent` at capture
  scope and rules out a shared retail null request. It does not name the
  preceding divergence or authorize a fallback, dispatch/VI change, or audio
  contract edit. Artifact:
  `scratch/agent/s2370_m5_a1_null_function_origin/`.

- **s2368 — A1 target-origin comparison was route-invalid on the port.** The
  fresh retail oracle passed the whole-RDRAM positive control (`10,000` hits)
  and reached both target 640 origins (`0x00696100` and `0x00696600`, two VI
  rows each). Both same-build port arms emitted the early transition producer
  and positive context controls, but both aborted at `get_function` with last
  guest PC `0x80001F88` before reaching either target origin. The named-PC
  phase rows were zero, so those PCs are not positive controls for this A1
  capture. This selects `H-A1-CoverageInvalid` for the port comparison and
  does not identify a publisher or authorize a VI change. Artifact:
  `scratch/agent/s2368_m5_a1_second_origin_discriminator_result/`.

- **s2369 — A1 pre-target abort is a null/missing function request.** The fresh
  retail oracle passed the whole-RDRAM positive control and both target origins.
  Both same-build port arms independently passed the early 640 transition
  control, then emitted one `[a1-abort]` row for requested `0x00000000` at
  guest PC `0x80001F88`. Each resident table had the same three sections
  (0, 1, and 3), and none contained address zero. This selects
  `H-MissingOverlayFunction` at capture scope and rules out
  `H-ResidentOverlayWrongDispatch`; it does not identify the guest writer or
  authorize a fallback, guard, overlay change, or audio contract change.
  Artifact: `scratch/agent/s2369_m5_a1_pre_target_route_boundary_fixed/`.

- **s2357 — task ABI names the exact field destination.** A fresh retail
  capture passed whole-RDRAM `59,327`, target window `44,120`, exact fields
  `492/1,734/1,492/1,489`, four phase histories, writer histograms, named PCs,
  and the retained four-arm port controls. The task probe at `0x80033FCC`
  recorded `2,477` bounded type-2 rows, with zero invalid pointers or
  overflow; every `data_ptr+0x100` matched one of four watched fields. The
  writer/port join had `1,153` nonzero relations and `1,324` zero/sentinel-only
  rows. This selects `H-RetailTaskAbiNamesPortField` at capture scope. It does
  not authorize writeback, task-data edits, consumer/default changes, or a
  guard. Artifacts: `scratch/agent/s2357_m5_task_abi/`.
- **s2359 — exact writer is present but payload-mismatched.** The corrected
  capture passed whole-RDRAM `59,303`, target window `44,100`, exact fields
  `491/1,733/1,491/1,488`, all four phase histories, 25/25 named PCs, the
  task dump, four port controls, and post-value detail with zero detail
  overflow. The writer histogram and post-value rows were positive for all
  four task-matched phase/field keys. Of 2,038 joined post rows, 910
  nonzero values mismatched the retained s2352 field payload, 0 matched, 17
  were zero/sentinel-only, and 1,111 had no retained port profile. The task
  ordinal can only be carried as a phase/field range because the oracle emits
  task ordinal and writer VI separately. Artifacts:
  `scratch/agent/s2359_m5_task_value_order/`.
- **s2360 — retail writer source is directly task-related.** The fresh capture
  passed whole-RDRAM `50,486`, target-window `36,080`, exact fields
  `384/1,710/1,158/1,154`, all four phase histories, writer histograms 2–5,
  named PCs `25/25`, four retained port controls, and `1,902` type-2 task rows
  with zero invalid/overflow. It produced `40,237` phase-gated execution GPR
  rows and `1,600` task-matched post-value rows. `$s1 == data_ptr+0x100`
  occurred `376/376/431/417` times for the four phase/field keys, exactly
  matching the corresponding writer buckets; `$a2 == data_ptr` occurred
  `4,768/4,799/4,877/4,826` times. This selects
  `H-RetailWriterSourceIsTaskData` at phase/field scope and rules out a null
  direct source relation. The exact VI-to-GPR join remains open because the
  oracle line format has no per-execution VI field. Artifacts:
  `scratch/agent/s2360_m5_writer_source/`.
- **s2364 — post-task publication is partial, not closed.** The oracle gate and
  both stub/image route controls passed. Both nonzero target-stage rows matched
  the containing task's exact DMA destination, length, FNV, and nonzero count.
  The corrected post-task table found source+consumer rows and a later completed
  task record for `1/2` rows; the other row had no exact post-task PCM tuple.
  This selects `H-ContainingTaskInternalOnly` at this capture scope. Artifacts:
  `scratch/agent/s2364_m5_post_task_publication_join_final/`.
- **s2365 — destination/length candidates expose a changed post-task payload.**
  The same-build stub/image pair retained the oracle, route, VI, ABI,
  filter/voice, image-stage, and image-join controls. Both nonzero target rows
  had a destination/length DMA candidate and exact stage payload identity. One
  row had no post-task PCM candidate; the other had six destination/length
  candidates, all with `F59C39C5:0` rather than the stage's `6ADD4218:639`.
  This selects `H-PayloadTransform` at capture scope and rules out interpreting
  that row as an exact post-task publication. It does not identify the writer,
  establish legitimacy, or authorize a port contract change. Artifacts:
  `scratch/agent/s2365_m5_mixed_stage_publication_split/`.
- **s2366 — phase-wide provenance does not identify a legitimate transform.**
  The fresh oracle, route, VI, ABI, filter/voice, image-stage, and image-join
  controls all passed for the same-build stub/image pair; both arms reached the
  target phase with zero crash/abort markers. One changed destination/length
  candidate had eight phase-scoped source and eight consumer events, but every
  event had zero payload and zero writer fields (`writer_pc=0`,
  `writer_writes=0`), and the retained task completion sequence did not close
  the candidate. This selects `H-MixedOrUnrelatedCandidate` at capture scope,
  not a legitimate transform or a port contract. Artifacts:
  `scratch/agent/s2366_m5_payload_transformation_provenance/`.
- **s2367 — payload-owner join still has no legitimate transform source.** The
  fresh oracle and both same-build stub/image arms passed all retained route,
  VI, ABI, image-stage, image-join, filter/voice, and crash controls. The
  target table retained two rows and one changed destination/length candidate;
  source and consumer events were present, but writer/source fields were zero
  and zero changed rows had same-task ordered owner events. This selects
  `H-MixedOrUnrelatedCandidate` at capture scope and rules out a legitimate
  transform from this table. Artifacts:
  `scratch/agent/s2367_m5_payload_owner_join/`.
- **s2361 — stub/image route validation is positive but same-task timing is
  unresolved.** One binary ran both arms. Oracle whole-RDRAM writes were
  `487,474`; route, VI, task-ABI, filter/voice, and PCM controls passed for
  both arms. The stub had unchanged DMEM and no DMA; the image arm had roughly
  `1,600` changed DMEM bytes and two stage DMAs per task. The bounded table had
  `target_stage_rows=2`, `same_task_pre_rows=0`, and
  `same_task_post_rows=0`, so the driver selected
  `H-PreEvents-EarlierTick`. This proves execution of the image internal path,
  not downstream audio completion. Artifacts:
  `scratch/agent/s2361_m5_step1_stub_image/`.
- **s2356 — value-only role join was ambiguous.** Controls passed, but the
  candidate writer/value join had zero nonzero matches and only zero/sentinel
  intersections. This is superseded by s2357's independent address relation.
- **s2355 — hangar writer values did not match port fields.** All nine positive
  writer keys were retained after the detail cap was raised; the only shared
  value was the common zero sentinel. This selected
  `H-RetailWriterIsUnrelated` at that capture scope, before the independent
  task-ABI naming result.
- **s2354 — first payload capture overflowed.** The result was rejected as a
  capture-capacity failure, not as evidence of a null writer.
- **s2343–s2353 — C88 and field provenance.** Retail independently writes
  `0x8008EC88 -> 0x01000000`; the port arms requested nonzero but stored zero.
  An opt-in C88 treatment restores the gate and exposes intermediate
  key-on/slot/filter work, but not a complete PCM/voice contract. Subsequent
  output and writer censuses found zero port ABI output metadata, closed
  `0x80094648` as an unrelated sentinel writer, and mapped known retail writer
  PCs to the exact title/hangar field set. The payload/order contract remains
  open. See §48 for the durable sequence and independent controls.

## Active backlog

Closed investigations are not active work items. This is one monotonic
sequence; #1 is the next campaign priority.

1. **M5 audio de-stubbing — active.** Keep `docs/M5-AUDIO-PLAN.md` as the
   design gate and proceed only with ground-truth-first, positive-control-
  qualified steps. The reporter-predicate audit is closed; the next queued
  boundary is whether the image-stage `nonzero` predicate is a legitimate
  output-contract requirement or a capture/reducer artifact. s2390 confirmed
  the retained target zeros but could not recompute bytes; s2391 confirmed
  retail activity in the broad candidate region but not exact stage payloads.
  s2392 found nonzero retail bytes in a retained-zero exact window; audit the
  port logger's exact region and bytes before changing the predicate.
2. **M5 task/output closure — closed at current capture scope.** s2387's
   corrected reporter-candidate table associated raw `[audtask-join]` records
   with 100% of 4,688 image-stage candidates; reporter completion was true for
  4,293 rows. Among incomplete rows, neither source nor consumer matched in
  166/165 candidates, with source-only and consumer-only minorities and no
  both-match row. The s2385 zero was caused by joining the wrong marker family,
  not by absent task records. Keep the corrected reducer and do not change
  task data or audio based on the old gap.
3. **M5 gate polarity/writer join — closed at current capture scope.** s2381
   independently identified retail gate writer/value behavior and s2382
   supplied the port-side downstream comparison; no gate treatment is
   authorized.
4. **M5 payload-transformation provenance — closed at current capture scope.**
   s2367's owner join retained source/consumer events but no nonzero
   writer/source relation or same-task ordered owner events. Do not repeat this
   phase-wide candidate join without a new ground-truth discriminator.

5. **M5 A1 retail flag semantics — closed at current capture scope.** s2380
  independently observed `osRecvMesg` entry with `$a2=1` on all `2,524`
  target call joins, despite the pre-delay call-site `$a2=0`. Do not repeat
  the delay-slot watch or change the flag based on this result; the upstream
  caller/input divergence remains a separate question.
6. **M5 A1 pre-target route boundary — closed at current capture scope.** The
   requested address is `0x00000000`, outside every resident section in both
   arms. Do not repeat the resident-overlay table without a new ground-truth
   discriminator or add a null fallback.
7. **M3 crash work — parked.** Resume only as a systematic idiom-class audit
   with a named discriminator; do not chase a single recurring crash.
8. **Hangar visual artifact — parked.** Malformed-triangle H2 and consumer-mode
   H1 are refuted. H3 is unavailable because the oracle cannot screenshot the
   LLE path; do not repeat the capped `0xD60` scan.

## Durable boundaries

### Route, rendering, and Factor 5

The accepted route table selects `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches
title and hangar, `01` reaches title only, and `10`/`00` reach neither. Menu
spin yield is a diagnostic route aid, not a default behavior change. Factor 5
command mappings and the required independent controls are documented in
[`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). Read them before
reasoning about a DL/RDP anomaly; the runtime cannot witness its own null.

### M5 audio and image output

Direct service entry/exit, the service gate/loop, and task/AI boundary are live
on the port. The image arm changes DMEM, completes, emits generated DMA, and
can publish a nonzero PCM join; destinations and stage/consumer polarity
rotate by capture. The C88 treatment reaches intermediate key-on/slot/filter
work, but exact task publication and voice completion remain open.

The durable recent sequence is: s2346 found completed image tasks with zero
output metadata and zero generated-range overlap; s2347 found an independent
retail output-span writer while port ABI output stayed zero; s2348 closed that
writer as unrelated to the computed task field; s2349–s2353 mapped the exact
field set across title and hangar; s2354 rejected an overflowing payload
capture; s2355 found no nonzero value match; s2356 left the task-ABI relation
open; s2357 closed the address/naming boundary with `1,153` nonzero
task/field/writer/order relations; and s2359 found the exact retail writer but
a payload mismatch at the comparable rows. The remaining question is writer
source/provenance, not permission to patch the port. s2360 then selected the
direct task source class at phase/field scope: `$s1` matched each task-field
address and `$a2` repeatedly matched each task `data_ptr`; the exact writer-VI
join remains unavailable in the oracle output.

No behavior change is authorized by these results. In particular, do not
promote the C88 writer, invent output metadata, remap destinations, alter task
data, force a consumer, or add a defensive guard without a new discriminator
and a named legitimate/illegitimate writer.

### VI state and second origin

Retail's `__osViNext` context uses `framep` plus the selected field to produce
the next origin. The port has matching framebuffer/mode candidates, but its
default selector, guest `comRegs.vCurrent`, and published current-line bit
remain zero. Opt-in field/current-register/timing/total-VI arms recover the
split, but the natural host publisher and cadence are unidentified. The A1
matrices were route-invalid and do not select a VI arm.

### Key-on, M3, M4, and symbols

Retail reaches the alternate key-on transfer path and skips the eight port
divide PCs. The port has positive normal-tail/slot behavior with divisor
`0xC0` and no guard hits. Exact `(origin,width,PC)` buckets differ in both
directions; the common cross-runtime pointer/source/state witness is not
restored. The `-0x25A4` pointer-chase, six-site PIC, ten-site audio-slot,
slot-dispatch, two-line overlay-move, and leftover `fake_func_*` size-class
audits are closed at their stated scopes. Generated-symbol renaming is closed
at the useful boundary; do not invent names for
`func_8000040C`, `func_800927B0`, `func_80092A54`, `func_80092CF0`, or
`func_800E9AE0`.

## Superseded conclusions

These were believable before qualified routes and independent controls, but
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
  independent retail nonzero ring, and exact PCM joins.
- s2331's unevaluable filter/voice null; s2332 added a host-positive span
  control and showed the real port audit still had zero rows while retail
  executed the caller/callee.
- s2335–s2342's successive inactive-parent/gate labels; each was refined by a
  deeper positive control until the measured boundary reached the C88 byte
  test. s2343 then identified the port writer mismatch, and s2344 showed the
  opt-in gate treatment was real but incomplete.
- s2345's task-output-gap label; s2346 found completed image task intervals
  whose output metadata and DMA overlap were both zero.
- s2346's output-metadata-writer-absent label; s2347 found a positive retail
  output-span writer, and s2348 closed the observed candidate as unrelated to
  the task field.
- s2349–s2356's successive retail writer-placement/value ambiguities; s2357's
  independent task dump established the exact `data_ptr+0x100` field relation.
- s2376's `H-InputDependentPath` boundary label is superseded for the A1
  receive call: it was believable because the generated body visibly tests the
  post-call queue-head bit, but s2377 independently measured retail `$a2=0`
  versus port flag `1` in both arms. The remaining question is contract
  provenance, not queue-state arm divergence.
- s2379's unresolved `H-RetailNonblocking` versus
  `H-RetailBlockingObserved` split is superseded by s2380's callee-entry
  capture. The call-site zero was believable as a semantic flag only because
  the debugger labels the `jal` PC, but it is pre-delay state; the callee
  received one in every target join.
- s2383's `H-CompletionEventMissing` label is superseded by s2384's
  phase-keyed callback audit. It was believable because the prior candidate
  census only retained stage-to-output rows and had no direct callback
  invocation marker; the new marker and the existing completion-event field
  both show producer invocation and association in the image arms.

## Evidence and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm its
  whole-RDRAM positive control first; watches are physical and phase-gated by
  VI callbacks.
- A null requires a same-run positive control. Batch all counters and A/B
  arms in one build/run, scope budgets to the phase, and use VI gates rather
  than elapsed time for animated scenes.
- Regenerate in order: `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then
  CMake. Diagnostics in generated output belong in fixup scripts.
- Kill runs with SIGKILL, never SIGTERM. Run from `build/` with the ROM
  present. Capture paths must not start with `.` in the final component.
- Never run `git submodule update`, `git checkout -- lib/...`, `git clean`, or
  `git reset --hard`. If `lib/` changes, export submodule patches in the same
  iteration.
- A mitigation is not an explanation: name the writer, state legitimacy, and
  add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a complete discriminating table and an
  outcome that can select among hypotheses.
