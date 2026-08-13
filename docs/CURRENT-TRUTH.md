# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history and superseded detail are
in [`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen those
closed lineages without a new class-level lead.

Reviewed through s854 (2026-08-13). The active blocker is the authoritative
FULL_SYNC/E9 accounting path after the post-sec2 gate. M5 audio de-stubbing is
closed. M3 work is limited to systematic idiom-class audits.

## User directive

Priority until changed by the user:

1. Maintenance when this file exceeds 60,000 bytes.
2. A genuinely new M5 audio lead only; the existing M5 campaign is closed.
3. M3 crash work only as whole-idiom audits, not reactive crash chasing.

## Current truth

- The overlay-dispatch problem was fixed sufficiently for the mission-entry
  path to reach post-sec2 outdoor presentation. The remaining blocker is not
  the old boot/menu overlay hypothesis.
- The product multi-header freelist restore is ON. Garbage-CIMG and wrap-drop
  mitigations remain OFF because suppressing the writeback also suppresses
  recovery. Any new mitigation requires an `ORIGIN:` naming the writer and a
  legitimacy assessment.
- Phase-gated port captures can reach VI width 1024 and pass independent
  provenance controls (`emit`, `raw`, `dispatch`, `match`). Pre-chain crashes
  remain several disjoint families; they do not classify parser loss.
- s820 and s821 independently reached width 1024 and showed authoritative
  parser/full-sync advancement, while later entering the known
  `slotDispatcherIter+872` SIGBUS family. This refutes total post-sec2 parser
  loss, not the remaining accounting discrepancy.
- s823–s825 repaired the telemetry ownership join. The post-callback rows have
  matching task serials, aligned guest E9s, and positive controls.
- s826's apparent same-task parser undercount was single-source evidence.
  s827 source audit established that the old `parser_delta` read a cumulative
  counter spanning LLE tasks, reset only at `rs64_run_lle_gfx` entry. It is
  incremented in two RT64 parser fetch paths for raw opcode `0xE9`; producer
  task begin/end do not reset it. The advance ring shares the LLE reset and is
  capped at 512. `g_cumulative_fullsyncs` is a separate process-lifetime
  bridge counter.
- s829 added an explicit epoch at each parser reset and printed it in the
  post-parser report and task join. In the one s790 capture, 58 join rows had
  task/epoch identity (including positive controls), but aligned rows still
  showed bridge E9 counts of 19–36 against parser counts of 0–3. This is
  single-source runtime evidence: it rules out an unlabelled reset epoch as
  the explanation, but does not distinguish consumer ordering from parser
  filtering or establish a writer/legitimacy claim. The known
  `slotDispatcherIter+872` crash recurred at 204s.
- s830 added a monotonic event sequence for reset, first RT64 consumer E9 fetch,
  and join. The Debug build passed. The phase-gated run reached VI width 1024,
  passed all four E9 positive controls (128 provenance rows), and produced 40
  keyed join rows. Every keyed row had reset < first-consumer-fetch < join,
  matching epoch, and parser_delta=bridge_delta=1 (orders 1<2<3 through
  118<119<120). This is single-source runtime evidence against
  producer/consumer ordering for the captured control/sec2 population; it
  does not explain the earlier aligned-task gap or establish parser loss. The
  run later hit the known Metal barriers crash at guest PC 0x8000B650.
- No current conclusion establishes parser loss, a bad RDP writer, or a
  legitimate/illegitimate game value. No mitigation is justified.
- s831 added an independent bridge-submit serial and recorded it again at the
  RT64 consumer call boundary, including task scope and [lo,hi). In the
  corrected capture, all 67 E9-bearing producer serials had a consumer record
  with the same serial and range; 4 control and 58 sec2 provenance rows passed
  `emit/raw/dispatch/match`, and all 36 sec2 join rows had
  `bridge_delta=parser_delta=1`. This is a second independent line against
  producer/consumer range loss for the captured early sec2 population. The run
  reached only VI 320/640, not VI 1024, so it does not settle the late
  post-sec2 mismatch.
- s832 reached VI 1024 at 79.6s, passed all four provenance controls, and
  produced late aligned joins for tasks 570 and 580. Those joins still showed
  `bridge_delta=16/15` versus `parser_delta=2/2`. The submit-range logger's
  128-row budget ended at task 282, so late producer identity remains untested;
  all 128 retained producer serials matched consumer serial/range records.
  The run later hit the known `slotDispatcherIter+872` crash. No parser-loss,
  writer, or legitimacy conclusion is established.
- s833 extended the section-2 provenance latch from 64 to 512 tasks. The same
  VI-1024 recipe reached task 649, passed all four control rows
  (`emit/raw/dispatch/match=1`), and retained 863 E9-bearing producer serials
  across tasks 570–649. Every one had an exact consumer task and [lo,hi)
  range match; the consumer logger's serial is a call-boundary latest-submit
  label, not the producer record's serial. In the independent task-join
  accounting, 20 of 27 late
  aligned rows still had unequal deltas; examples include task 632
  `bridge_delta=27/parser_delta=0` and task 649 `31/3`. This rules out late
  submit-range loss for the captured population and selects the
  parser/filter-or-join-population branch, but does not yet distinguish those
  two or establish a writer/legitimacy claim. The run later hit the known
  `slotDispatcherIter+872` SIGBUS.
- s834 completed the requested source-and-log accounting audit without a new
  build or run. In the s833 log, late tasks 570–649 contain 863 E9-bearing
  accepted submit ranges; all 863 have exactly one RT64 consumer-range record
  with the same task and [lo,hi), and all 80 late tasks have consumer rows.
  The join stream has 80 task/epoch rows: 77 have unequal bridge/parser deltas,
  while 69 retain reset < first-consumer-E9 < join. The source inventory found
  one bridge writer/reset pair (`rs64_count_submitted_e9` / task-begin reset),
  one parser writer/reset pair (the two raw-E9 fetch sites /
  `rs64_rdp_advance_reset`), and one aligned writer/reset pair (the callback /
  `g_e9prov = {}`). This selects H-parser-filter for the captured late
  population: submit/consumer identity and task epochs are aligned, but the
  authoritative parser's raw-E9 count is lower or absent before the join.
  It does not yet identify whether the cause is byte-order/raw-op decoding,
  pending-command handling, or another parser filter, and it is not a writer
  legitimacy claim or a mitigation basis.

- s835 completed the parser-side source audit without a build or run. `MEM_B`
  and the bridge's `g_rdram_for_submit[p ^ 3]` select the same logical first
  byte as RT64's `dl->w0 >> 24`; byte order is refuted. The bridge scans every
  8-byte slot, while RT64 advances by `cmdLength * 8`, so an E9 in an interior
  word of a multiword command is bridge-counted but never a parser opcode.
  Pending completion has a separate valid-sentinel gate. This identifies
  command-boundary filtering as the leading explanation for s833's 9/1, 9/1,
  27/0, and 31/3 rows, but it is source-only and needs a paired runtime probe.
  No mitigation or legitimacy claim is justified.
- s836 paired that audit with one phase-gated runtime probe. The run reached VI
  1024 and passed the four existing E9 provenance controls (310 positive rows).
  Among 651 captured sec2 bridge E9 slots, 65 were exact authoritative parser
  command starts and 582 were covered by a preceding non-E9 parser command
  span; only 4 had neither record in the bounded stream. The parser stream had
  416 direct E9 starts, 977 span records, and no pending-completion E9 record.
  This is a second line with s835's source audit and selects
  H-command-boundary for the captured late population, while leaving the four
  unmatched slots and general pending behavior unclassified. The run later
  hit the known Metal `0x8000B650` crash. No mitigation or legitimacy claim is
  justified.

- s837 added parser command-start/pending telemetry carrying task, submit
  serial, and exact `[lo,hi)` range. Two initial runs reached VI 1024 and
  passed all four controls but exhausted lifetime record budgets before late
  tasks, so they were invalid for classification. The corrected task-scoped
  run reached VI 1024, passed all four controls, and later hit the known
  `slotDispatcherIter+872` crash at task 657. It logged 1,196,701 in-range
  parser command starts, 681 parser E9 records, zero pending completions, and
  657 joins. None of the late unmatched emitted addresses was contained in a
  logged parser call range. This selects H-range-association for the captured
  four-slot class, not H-pending-path or an in-range parser filter. The bridge
  late-slot population still needs an independent range/serial capture because
  its older lifetime budget ended at task 385. No mitigation or legitimacy
  claim follows.
- s838 changed only the bridge boundary-record budget from a lifetime 1,024
  lines to a per-task 1,024 lines, then ran the phase-gated recipe. VI 1024
  was reached, all four provenance controls passed (204 rows), and 889 late
  bridge E9 slots were retained across tasks 570–630. None was contained in a
  parser command range with the same task, and none had a same-serial parser
  range; the parser command stream remained live through task 630. The run
  later hit the known `slotDispatcherIter+872` crash. This is a second,
  independent runtime line selecting H-range-association for the late bridge
  population and ruling out the old bridge-record-budget loss explanation.
  It does not yet identify why the parser call ranges are disjoint or justify
  a mitigation.

- s839 completed the requested source audit without a build or run. Normal
  bridge submissions are synchronous and preserve identity: each accepted
  range calls `rs64_dpc_record_submit`, which stores `[lo,hi)`, increments the
  serial, and immediately invokes `submit_rdp_range`; RT64 passes those same
  arguments to `processRDPLists`, whose parser derives its call range from the
  same pointers. This refutes a normal producer/consumer range race and a
  normal latest-submit ordering explanation. One exception is the non-deferred
  synthetic FULL_SYNC path (`rsp_force_fullsync`), which calls
  `submit_rdp_range` without recording a new serial/range; its consumer and
  parser telemetry therefore carries the previous submit label while parsing
  the synthetic `[addr,addr+8)` range. Deferred synthetic ranges do receive a
  normal record at commit. This identifies a bounded telemetry label-staleness
  path, but does not explain the late ordinary bridge/parser disjointness or
  establish a writer/legitimacy claim.

- s840 added task-scoped synthetic FULL_SYNC markers and explicit ordinary
  E9-bearing submit/consumer markers. The first capture was invalid because
  the recipe omitted `ROGUESQ_LOG_DL_SYNC=1`; the corrected capture reached VI
  1024, passed all four controls, and ran through task 598 before the known
  `slotDispatcherIter+872` SIGBUS. It recorded 3,986 ordinary E9-bearing
  submissions, including 555 late submits from tasks 570–598; every late
  ordinary submit had an exact consumer serial and `[lo,hi)` range match.
  Synthetic submit and consumer markers were both zero. Together with s838's
  independent parser-range capture, this rules out ordinary producer/consumer
  range disjointness and synthetic stale labels for the captured late
  population, and selects H-parser-record-loss/range-association as the
  remaining accounting branch. It does not identify the parser condition and
  gives no writer/legitimacy basis for a mitigation.
- s841 attempted the parser-condition probe three times in one iteration. The
  initial recipe omitted the post-title input schedule; the corrected recipe
  and reduced-trace retry reached VI 1024 and fired the boot controls, but all
  three runs reproduced the Metal `drawIndexedTri` `G_CYC_COPY` assertion at
  about 165–168 seconds, before task 570 or late parser records. This is an
  unevaluable reachability result, not a parser null. The existing s840 late
  capture remains authoritative; the next unit is a systematic source audit
  of the `drawIndexedTri`/`G_CYC_COPY` idiom.

- s842 completed that source-only idiom audit without a build or run. All
  regular triangle callers assert on `G_CYC_COPY`; copy mode has rectangle
  handling but no legitimate regular-triangle path. RSP other-mode setters
  immediately synchronize RDP state, and reset initializes equivalent
  1-cycle values, so no static stale-copy transition was found. Factor 5
  inherits F3DEX dispatch, overrides its documented real triangle opcodes
  0xB4/0xBF with consume-only handlers, and leaves 0xB1 mapped to standard
  F3DEX TRI2. This selects H-wrong-handler as the leading source hypothesis,
  but runtime caller/opcode attribution is still required; no mitigation is
  justified. Full audit: `docs/M3-DRAWINDEXED-COPY-AUDIT.md`.

- s843 added a behavior-neutral dispatch-to-`drawIndexedTri` breadcrumb carrying
  the active GBI, raw opcode, command words, and RSP/RDP other-mode values.
  The Debug build passed. Two full phase-gated captures reached VI 1024 and
  passed the E9 provenance control (211 and 435 rows), but neither produced a
  triangle-call or copy-assert row; the second ran to process exit at 274.7s
  and its independent DL-sync census still showed `tris=599`. This is an
  unevaluable reachability result, not evidence for any copy-cycle hypothesis.
  No behavior or mitigation changed.

- s844 added a behavior-neutral, per-VI-width dispatch breadcrumb immediately
  before the RT64 handler call for raw opcodes `0xB1`, `0xB4`, and `0xBF`.
  The Debug build passed. The phase-gated run reached VI 1024, produced 392
  positive E9 provenance rows, and later hit the known
  `slotDispatcherIter+872` SIGBUS at 202.8s. It recorded 112 candidate
  dispatches (0xB4/0xBF only), but zero `drawIndexedTri` or copy-assert rows;
  the independent DL-sync census continued to run. Together with s842's
  source mapping of 0xB4/0xBF to consume-only Factor 5 handlers, this selects
  H-factor5-consume-only for the captured candidate population and rules out
  H-no-triangle-dispatch there; it provides no runtime evidence for H-wrong-
  handler because 0xB1 did not dispatch. The rows' garbage-shaped operands
  are not a legitimacy or writer attribution. No behavior or mitigation
  changed.

- s845 completed the prescribed source/reference audit of s844's 112 candidate
  dispatches: 37 were 0xB4 and 75 were 0xBF, with 54 textured (`w0 & 2`) and
  58 untextured rows. The independent Factor 5 reference calls these TRI2 and
  TRI1 geometry commands and specifies a conditional total advance of 24 or 8
  bytes. The installed RT64 Factor 5 map instead routes both opcodes to an
  unconditional 16-byte consume-only handler. This selects
  H-misclassified-opcode for the installed map. The repeated opcode-like and
  incoherent operands in the rows keep H-garbage-candidate open as a separate
  stream-provenance question; no writer or legitimacy claim exists, so no
  mitigation or behavior change is justified.

- s847 built the requested within-run Factor 5 TRI A/B and corrected one
  invalid capture that omitted `ROGUESQ_LOG_TRI_DISPATCH`. The corrected run
  reached VI 1024 and all four E9 controls, then recorded 40 candidate
  dispatches before the known `slotDispatcherIter+872` SIGBUS. Every candidate
  row reported `ucode=1`; the RT64 enum defines 1 as the RDP GBI, while
  `F3DFACTOR5` is 12. The A/B handler therefore produced zero arm rows and
  zero triangle-call rows: these candidates were not dispatched through the
  installed Factor 5 map. This is independent source/runtime evidence that
  the s844 candidate census was misattributed to the Factor 5 handler family;
  it does not select H-map-load-bearing, H-map-intentional, or H-map-garbage.
  No game behavior or mitigation changed.

- s848 added a behavior-neutral `[tri-owner]` record at the RT64 handler
  boundary, pairing each B4/BF dispatch row with the selected GBI enum, owner
  name, and map function pointer. The phase-gated capture reached VI 1024,
  passed the E9 provenance controls (165 rows), and produced one positive
  B4/BF dispatch with one matching owner row: `ucode=1`, owner `RDP`; there
  were zero Factor 5 owner rows, zero triangle-copy rows, and no crash marker.
  The source enum independently defines 1 as RDP and 12 as F3DFACTOR5. This
  selects H-rdp-candidates for this capture and rules out H-factor5-candidates
  for the observed row; H-mixed-owner is not observed. It does not establish
  whether the RDP candidate is legitimate, misframed, or garbage, and no
  mitigation or behavior change is justified.

- s849 added a behavior-neutral `[tri-boundary]` record containing the RDP
  command-table map entry, masked opcode, length, current/next parser address,
  preceding parser span, and submit range. The Debug build passed. The
  phase-gated run reached VI 1024, passed the E9 provenance control 402 times,
  and produced 108 matching candidate/owner/boundary rows (28 at VI 512 and
  80 at VI 640) before the known `slotDispatcherIter+872` SIGBUS. Every row
  was `ucode=1 owner=RDP`, had command length 1, and had a valid preceding
  parser boundary except the first row of each width interval. The masked
  opcodes are 0x34 for raw B4 and 0x3F for raw BF; the RDP source table's real
  triangle range is 0x08–0x0F, so these are boundary-shaped non-triangle RDP
  entries rather than genuine RDP triangle commands. This is a second
  runtime/source line selecting H-rdp-garbage as the leading explanation and
  leaving H-rdp-misframed open only for the unmeasured writer/stream origin.
  It does not identify the writer, prove operand legitimacy, or justify a
  mitigation. No behavior changed.

  ORIGIN: host-side parser-boundary telemetry; the candidate values were not
  changed, skipped, or reinterpreted.

- s850 added a phase-gated `[tri-writer]` record at the accepted RDP submit
  boundary, carrying candidate address, task, serial, words, and source range.
  The first capture reached VI 1024 and passed the E9 controls, but its
  lifetime 1,024-row cap saturated at task 387 before the boundary population;
  that result was unevaluable. The fixed per-task 64-row capture reached VI
  1024 and the known `slotDispatcherIter+872` SIGBUS at 205.1s. It retained
  10,476 writer rows across tasks 63–616 and 109 candidate owner/boundary rows
  (81 at VI 640, 28 at VI 512). Every one of 109 boundary submit ranges had an
  exact `[tri-writer]` accepted-range match; 18 also matched the exact
  candidate address. The bridge source independently uses the same RDRAM
  mapping and range passed to `submit_rdp_range`. With the four E9 positive
  controls firing, this selects H-game-writer for the observed RDP-owned
  candidate stream and rules out H-unattributed for that population. It does
  not establish operand legitimacy, explain the RDP table mismatch, or justify
  a mitigation.

  ORIGIN: host-side accepted-submit writer telemetry; no candidate value,
  command advancement, geometry, or mitigation behavior changed.

  ORIGIN: host-side owner telemetry at the RT64 handler boundary; no game
  value, command advancement, geometry, or mitigation behavior changed.

- s851 added behavior-neutral RT64 parser-condition telemetry carrying direct,
  span, and pending condition tags with the exact task submit serial/range;
  the bridge joined those records against emitted E9 slots and reported an
  explicit unassociated class. The phase-gated run reached VI 1024, fired
  653 provenance rows including all four positive controls, and later hit the
  known `slotDispatcherIter+872` SIGBUS at task 653. For late tasks 570–653,
  1,068 emitted slots were classified: direct=66, span=1,001, pending=0,
  unassociated=1. This is a second runtime line with the s835 source audit
  selecting H-span-accounting: most bridge-counted E9 bytes lie inside
  preceding non-E9 parser command spans, so the lower authoritative E9 count
  is command-boundary accounting. It rules out H-pending for the captured
  population and leaves one residual slot for the next source audit. The
  result does not establish a writer defect, operand legitimacy, or justify a
  mitigation.

  ORIGIN: host-side parser-condition telemetry; no game value, parser advance,
  RDP handler, or mitigation behavior changed.

- s852 completed the prescribed source audit without a build or run. The bridge
  scans accepted ranges at fixed 8-byte boundaries using the same logical
  byte-swapped RDRAM selection used to form words, while RT64 loads each parser
  boundary and advances by `commandWordLengths[opCode] * 8`. Normal non-E9
  commands report `span` over that full command interval; E9 command starts
  report `direct`; a split command reports `pending` only on completion. This
  accounts for the 1,001 span rows and rules out a normal byte-order or
  producer/consumer range mismatch. Deferred commits retain normal identity;
  non-deferred synthetic FULL_SYNC is the bounded stale-label exception.
  The one residual remains unclassified because the extended-opcode branch
  bypasses the condition callbacks and has function-controlled advancement.
  No writer, legitimacy, or mitigation conclusion follows.

  ORIGIN: source audit only; no game value, parser advance, RDP handler, or
  mitigation behavior changed.

- s853 added the requested behavior-neutral `kind=extended` condition marker
  at the RT64 extended-opcode branch and exported the submodule patch. The
  Debug build passed. The single phase-gated capture reached VI 1024 and
  passed the E9 provenance positive control 345 times, but the known
  `slotDispatcherIter+872` SIGBUS occurred at task 514 before the late
  residual population previously observed around task 653. Captured summaries
  had `pending=0`, `extended=0`, and no unassociated row. This is an
  instrumented-but-unevaluable reachability result, not evidence against
  H-extended-residual; no parser behavior or mitigation changed.

## Session s854 result

The residual-condition recipe ran twice, including a corrected retry with
`ROGUESQ_LOG_RDP_CONDITION=1`. The first capture reached VI 1024, passed 388
positive E9 provenance controls, and reached task 645 before the known
`slotDispatcherIter+872` SIGBUS; its last join was `bridge_delta=31` versus
`parser_delta=3`. The corrected retry reached VI 1024, passed 357 controls,
but crashed at task 524. Neither capture reached the required task 650 gate,
and neither produced an extended, synthetic, or pending marker for the
residual. These are unevaluable reachability results, not evidence against
H-extended-residual. No parser behavior, game value, or mitigation changed.

ORIGIN: recipe-only condition logging and existing host-side telemetry; no
game value, parser advancement, RDP handler, or mitigation behavior changed.

## Next work unit: audit the recurring slotDispatcherIter+872 crash path

HYPOTHESIS-ID: m3-slot-dispatcher-crash

Perform one bounded source-only idiom audit of every `slotDispatcherIter+872`
definition, call path, crash marker, and guest-PC handoff. Do not build, run,
or change parser advancement, RDP handlers, or mitigation.

Competing hypotheses:

- H-real-stall: the dispatcher intentionally aborts after a guest-side
  scheduler stall and task 650 is unreachable without fixing that idiom.
- H-crash-report-only: the process is still making progress and the host crash
  marker is a false attribution or stale signal.
- H-runtime-corruption: an invalid slot or queue state reaches the dispatcher
  and causes the SIGBUS before the residual task.
- H-unrelated-thread: the marker belongs to a different thread and cannot
  explain the late-task reachability loss.

Discriminator: enumerate every source site and call edge, then classify each
observed marker by thread, guest PC, signal/abort origin, and whether the
dispatcher has a progress counter or explicit stall threshold. A complete
one-to-one match between the task-650 failures and an intentional stall gate
selects H-real-stall; a mismatch selects H-crash-report-only or
H-unrelated-thread; a reproducible invalid-state input selects
H-runtime-corruption. No source-only result authorizes a mitigation.

## Ranked backlog

1. Complete the slot-dispatcher crash idiom inventory and classify the
   recurring signal/guest-PC path.
2. Re-run the residual condition capture only after the blocker is classified.
3. M3 co-gates and crash families: pursue only a complete idiom inventory,
   classification of every site, and proof/guard per site. Passive breadcrumbs
   belong in queued soaks.
4. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`; each needs independent controls.
5. Regeneration-pipeline reliability: retain the delete-before-regen rule and
   audit fixup counts when a reproducible omission appears.

## Closed and parked

- M5 audio (legacy -160..-230) is CLOSED. A new lead is required; see
  `docs/M5-AUDIO-PLAN.md` and PROJECT-OVERVIEW §§9–12.
- Hangar-exit to sec2 is CLOSED except backlog item 1; see PROJECT-OVERVIEW §27.
- Earlier idiom campaigns, duplicate-symbol work, missing-function inventory,
  old ucode/DMA experiments, and rendering dead ends are archived in
  PROJECT-OVERVIEW §§13–26. Do not retry them.
- Parked legacy items include intermittent regeneration omission, isolated
  animation/frameStart SIGBUS reports, the M3 DoD gate, and M4 band-row
  coverage. They are not active work units.

## Ground truth and method rules

- Before runtime instrumentation, consult `tools/oracle/README.md` for retail
  memory watches and `docs/F5-UCODE-REFERENCE.md` for the exact Factor 5 table.
  Arm a positive whole-RDRAM control before interpreting a null.
- Gate animating comparisons on `PROBE_PHASE_WIDTH` and
  `PROBE_KEYS_FROM_PHASE=1`; scope counters and budgets to the phase.
- Batch all instrumentation into one build/run. A counter is evidence only if
  a positive control fires in the same run. Require two independent evidence
  lines before promoting a conclusion.
- Runs must launch from `build/` with the ROM present, use SIGKILL, and write
  capture paths whose final component does not begin with `.`. Queue repeat
  soaks in `scratch/agent/soak_queue/`; do not babysit them.
- Generated diagnostics belong in fixup scripts. Regeneration order is
  `make_elf.py`, N64Recomp, `fixup_game_funcs.py`, then CMake.

## Build and patch cautions

The game-function regeneration sequence and RSP regeneration details are in
PROJECT-OVERVIEW and the repository AGENTS instructions. Never run
`git submodule update`, `git checkout -- lib/...`, `git clean`, or
`git reset --hard`. `lib/N64ModernRuntime` and `lib/rt64` have intentional
working-tree patches; export them with `./submodule-patches/export.sh` if
editing under `lib/`.

The benign `wmain/main` linker warning may be ignored. Prefix environment-led
commands with `env` for the headless allowlist. Do not hand-edit generated
game logic; use `patches/` overrides. No emojis in code or documentation.
