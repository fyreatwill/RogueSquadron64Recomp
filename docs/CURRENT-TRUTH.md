# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history and superseded detail are
in [`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen those
closed lineages without a new class-level lead.

Reviewed through s869 (2026-08-13). The active blocker is the authoritative
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
- s861 completed the requested source-only attribution audit. The generated
  tree contains 9,550 process-wide breadcrumb writes across 47 guest
  functions; `0x8000834c` is emitted only by `drainMeshReleaseQueue` at the
  `jr $ra` delay-slot `nop`, not by `getNextSlotNpcTypeId` (which has no
  breadcrumb writes). The crash handler synchronously reads the same
  unsynchronized global from the crashing signal thread, with no thread
  identity, epoch, or helper handoff. This selects H-stale-breadcrumb for the
  s860 host-symbol crash family. It does not classify a later invalid slot
  chain and gives no mitigation or legitimacy basis.
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

## Session s855 result

Completed the prescribed source-only inventory of `slotDispatcherIter+872`,
its callers, crash handler, guest-PC handoff, and recent crash markers. There
is one dispatcher definition at guest `0x8003E8DC` in
`../N64Recomp/RecompiledFuncs/funcs_8.c`; its loop walks the NPC slot chain,
calls the update-function pointer, and returns through normal epilogue code.
It contains no progress counter, stall threshold, explicit abort, or signal
path. The documented callers are `cinematicSlotBatchDispatch` and the broader
set of generated `jal 0x8003E8DC` sites; no second definition or host-side
dispatcher was found.

The crash census found 31 matching markers. In the representative late-task
capture, the signal is SIGBUS 10 with `si_addr=0x33cb82199`, and the raw
faulting PC is the same local-symbol `slotDispatcherIter+872`; the backtrace
continues through `runInMissionFrame`, `mainGameLoop`, and
`mainBootstrapWorker` on the game thread. `last-guest-pc=0x80022160` is a
separate sticky breadcrumb and does not identify the faulting dispatcher
instruction. The concurrent VI snapshot says `stalledNow=1`, but the source
has no dispatcher stall gate, so that state is correlation rather than proof
of intentional dispatcher termination.

Two independent lines (source inventory and crash/runtime census) select
H-runtime-corruption as the leading explanation for the reachability loss and
refute H-real-stall, H-crash-report-only, and H-unrelated-thread for the
observed markers. The exact invalid slot/queue input and its writer remain
unidentified; no guard, skip, or other mitigation is justified.

ORIGIN: source audit and existing crash telemetry only; no game value,
dispatcher advancement, parser behavior, or mitigation changed.

## Session s856 result

Completed the requested bounded input/state audit across the sole
`slotDispatcherIter` and `slotDispatcherInner` definitions and all 144
generated `jal 0x8003E8DC` callsites (plus five `slotDispatcherInner`
callsites). `slotDispatcherIter` masks the caller's selector to 16 bits,
recognizes only `0xFFFF` as a sentinel, and uses `0x80130BB0 + index*8` for
both initial and chained indices; there is no table-capacity or chain-cycle
check. A non-null table entry is trusted for reads at `+0`, `+0x14`, and
`+0x1A`; `+0` is the indirect NPC update call, and the post-call `+4/+6`
links feed the next iteration. `slotDispatcherInner` has no null check on
its context argument and trusts the selected `0x80130BC0/BC4` list head,
allocator result, and `+0x44/+0x48` links while inserting the context.
The normal update-pointer writer is `spawnNpcOfType`'s `sw $s2,0($s0)`,
with `setupNpcUpdateFunctions` selecting the function passed into that path;
no source proof identifies the live corrupting write. This selects
H-invalid-slot/H-invalid-update as the actionable runtime branch, keeps
H-caller-state open as the likely writer origin, and refutes H-real-stall and
H-stale-breadcrumb for the observed markers. No mitigation is justified.

ORIGIN: source audit only; the identified writers are normal game
allocation/spawn paths, and their values' legitimacy at the observed crash
is unknown.

## Next work unit: audit the actual 0x8000834c crash family

HYPOTHESIS-ID: m3-guest-pc-8000834c-audit

Perform a source-only, whole-idiom audit of the function at guest PC
0x8000834c (`getNextSlotNpcTypeId`) and every generated caller, including all
reads of the slot-table links and all return-value consumers. Do not build or
run until the inventory identifies whether the crash PC can arise from a
legitimate caller-side state transition, an invalid slot/link, or a symbol/
stack attribution artifact.

Competing hypotheses:

- H-link-state: 0x8000834c reads a live but invalid slot-table link or index.
- H-caller-transition: callers pass a corrupted selector/context into the
  helper or consume its result incorrectly.
- H-legitimate: all observed reads and callers are valid; the crash is outside
  this helper's source path.
- H-stale-breadcrumb: the guest-PC handoff does not identify the faulting
  instruction or function.

Discriminator: the exhaustive source inventory must map every helper read,
caller, and consumer. A missing/invalid link path selects H-link-state; a
caller-only bad argument or result use selects H-caller-transition; complete
valid paths with the crash elsewhere select H-legitimate; an unmappable guest
PC handoff selects H-stale-breadcrumb. This is source-only evidence and
cannot authorize a mitigation without a writer and legitimacy assessment.

## Session s857 result

Added the behavior-neutral `slotDispatcherIter` trace through the generated-code
fixup path and built the Debug target successfully. The retail oracle was run
before the build-side probe with a whole-RDRAM positive control plus the
physical `0x130BB0..0x130FB0` table watch: 1,593,920 whole-RDRAM writes and
256 table-region writes occurred in 8 emulated seconds, confirming that the
independent watch was live and that retail populates this structure.

The phase-gated port capture reached VI width 1024 at 79.5 seconds, entered
trace phase ordinal 6, and filled all bounded controls: 512 dispatcher-entry
rows, 256 pre-call rows, and 256 post-call rows. Every pre-call row had a
KSEG0/RDRAM-range slot pointer (`valid=1`); update pointers were in the
observed `0x800403EC..0x8006FC90` function range, and every post-call row
returned `1`. The capture ran without a `[CRASH]` marker and ended when the
probe budget left the 1024 phase, so it did not observe the known dispatcher
fault itself.

This is two-source evidence (retail table-watch control plus port trace) that
the first bounded post-sec2 dispatcher population is not an invalid-slot or
invalid-update population. It does not classify the later crash-triggering
population, identify a writer, or establish legitimacy; H-caller-state remains
open and no mitigation is justified. The next unit expands the same trace
window to test whether the invalid state appears later in the phase.

ORIGIN: retail memory-watch control and host-side dispatcher telemetry only;
no game value, dispatcher control flow, parser advancement, or mitigation
behavior changed.

## Session s858 result

Expanded the behavior-neutral dispatcher trace through the generated-code
fixup path from 512 entry / 256 detail rows to 4096 entry / 2048 detail rows;
the Debug target built successfully. The single phase-gated capture reached
VI width 1024 at 79.8 seconds, then ran 54 post-gate frames before the process
died at 167.9 seconds. The positive control fired: 626 entry rows, 790
pre-call rows, and 790 post-call rows were captured. Every pre-call slot was
KSEG0/RDRAM-range valid, every update pointer was in the observed
0x800403EC..0x8006CBB0 range, and every post-call return was 1.

The death did not match the hypothesized dispatcher fault: the host marker was
the local-symbol artifact `__isPlatformOrVariantPlatformVersionAtLeast...`,
with sticky guest PC 0x8000834c, rather than slotDispatcherIter. Thus the
expanded observed dispatcher population remains valid and the later
crash-triggering population remains unevaluable. This is two-source runtime
evidence with the existing s857 retail-watch line, but it does not establish
H-stale-breadcrumb as a general explanation or identify a writer. No
mitigation was added.

ORIGIN: host-side dispatcher telemetry; no game value, dispatcher control
flow, parser advancement, or mitigation behavior changed.

## Session s859 result

Completed the prescribed source-only whole-idiom audit of
`getNextSlotNpcTypeId` (guest `0x80040218`, the function containing the
`0x8000834c` return-site breadcrumb) and all 25 generated callsites across
`funcs_9.c`, `funcs_11.c`, `funcs_17.c`, `funcs_18.c`, `funcs_19.c`,
`funcs_29.c`, `funcs_30.c`, `funcs_33.c`, and `funcs_42.c`. The helper masks
the selector to 16 bits, treats only `0xFFFF` as terminal, reads the slot
table pointer at `0x80130BB0`, loads the selected slot's `+4` link, and then
trusts the linked slot's `+0` context pointer before reading context `+0x16`.
There is no capacity, KSEG0, null-context, or cycle check in this helper.

The 25 callers pass either halfword fields from NPC/effect/HUD records or a
previous helper result. Every return consumer masks to 16 bits and compares
against `0xFFFF`; non-sentinel results are then passed to the expected NPC
context/destroy helpers or stored as a 16-bit selector. No source caller
widens, fabricates, or otherwise mishandles the helper result. This selects
H-link-state (the helper's trusted link/context chain) over
H-caller-transition for the actionable runtime probe, while H-stale-breadcrumb
remains open because the s858 host marker does not prove the faulting
instruction. H-legitimate is not established. No mitigation was added.

ORIGIN: source audit only; the normal slot-table/link and context writers are
game allocation/spawn paths, but legitimacy of the live crash-time values is
unknown.

## Session s860 result

The retail oracle was run before the port build with both required controls:
the whole-RDRAM watch recorded 1,596,697 writes in 8 emulated seconds, and the
physical slot-table watch `0x130BB0..0x130FB0` recorded 256 writes from boot
PCs `0x80000420/0x80000424`. Fresh regeneration (`make_elf.py` -> N64Recomp
-> fixup) and the Debug build succeeded. The fixup anchor audit initially
found that the helper's normal return included delayed-instruction comments;
that omission was corrected and a second fresh regen verified two helper trace
sites.

The phase-gated port run reached VI width 1024 and fired the positive controls:
627 dispatcher-entry, 791 pre-call, and 791 post-call rows. It captured 32
`getNextSlotNpcTypeId` rows. Twenty-eight terminal rows had `link=0xFFFF`; the
four non-terminal rows all had the in-range table `0x80202120`, in-range linked
slots, contexts, and type values, with returns matching the captured type. The
process later died at 168.3s with the known local host-symbol artifact and
sticky guest PC `0x8000834c`; no helper row occurred at the crash boundary.

The independent retail watch plus the port's positive-controlled trace show
that the observed helper population is valid and that retail writes the table;
s859's complete caller/consumer inventory independently found no caller-side
result fabrication. This selects H-valid-helper-population for the captured
window and leaves H-later-invalid-chain and H-stale-breadcrumb open for the
actual death. It does not identify a writer, establish crash-time legitimacy,
or authorize a mitigation.

ORIGIN: host-side helper telemetry and retail table-watch evidence; no game
value, helper control flow, or mitigation behavior changed.

## Session s861 result

Completed the prescribed source-only audit of the complete
`g_rs64_last_guest_pc` attribution chain. The generated recompiled tree has
9,550 writes across 47 guest functions. The exact `0x8000834c` writer occurs
twice in `drainMeshReleaseQueue`'s generated `jr $ra` delay-slot
representation (one executable pre-return stamp and one unreachable delayed
instruction copy); there are no `0x8000834c` writes elsewhere.
`getNextSlotNpcTypeId` at guest `0x80040218` has zero breadcrumb writes,
including both s860 trace exits.

The only definition is the process-wide `volatile uint32_t` in `main.cpp`,
declared through `recomp.h`. Guest bodies in multiple functions write it,
while pollers, watch-fault diagnostics, and the crash handler read it. The
POSIX crash handler samples it synchronously on the signal-delivery thread,
but the value has no TLS, writer thread, epoch, or call-chain association;
the Windows crash path does not print it. Therefore a crash symbolized as
`getNextSlotNpcTypeId+448` with `last-guest-pc=0x8000834c` is not a helper
instruction handoff: it is a stale process-wide breadcrumb from
`drainMeshReleaseQueue` or another guest execution path. This is source-only
evidence, but it directly discriminates the attribution hypotheses and
explains why s860 had no helper row at the death boundary.

The audit rules out using `0x8000834c` as a faulting-instruction attribution
for this family. It does not prove that a later helper invocation cannot carry
an invalid slot/link/context, and it adds no guard or other mitigation.

ORIGIN: generated breadcrumb writes and host crash-handler handoff semantics;
no game value, helper control flow, or mitigation behavior changed.

## Session s862 result

Completed a source-only whole-idiom audit of the recurring
`coalesceFreeHeapBlocks` local-symbol family. The function has one generated
caller (`funcs_0.c` at guest `0x80001430`) and two independent forward walks:
`0x80002390`/`0x80002434` from the global free-list head and
`0x80002474`/`0x8000247c` from the caller-supplied block base. Each computes
`next = block + MEM_W(block, 4)` and then reads `next+0x10`; both reads have
regeneration-safe range checks and safe loop-exit behavior. The caller's
`a0/a1` come from the heap globals at `0x801163e4/0x801163e8`, while `a2/a3`
and the internal free-list links remain unproven at the call boundary.

This source inventory selects H-heap-entry-state over H-missing-read-guard,
but cannot identify the writer or establish value legitimacy. It is
single-source evidence; no build, run, or mitigation was performed.

ORIGIN: source inventory only; existing guards change only the handling of
out-of-range computed next pointers, and no game value or control flow was
changed in s862.

## s863 coalescer entry-state probe

The regeneration-safe entry probe fired 3 times in a phase-gated port capture
that reached VI width 1024 and passed 147 E9 provenance positive-control rows.
All three rows carried an invalid incoming base (`a0=0x00000001` twice and
`a0=0` once); all three carried the same out-of-range global head
`0x830A10A0`. The other incoming bases were in KSEG0, and all 209 computed
next values at the two guarded reads were in-range. The run had no crash marker.
This selects H-heap-entry-state for the captured port population, but does not
identify the writer or establish legitimacy. It is single-source runtime
evidence. The retail oracle's whole-RDRAM control fired 11,785,315 times and a
known active control at `0x11A860` fired 24 times; the `0x1F3CC0` heap-slot
watch stayed at zero while retail remained at VI 320, so that heap-slot null is
unevaluable rather than a retail negative.

ORIGIN: the probe only reads and logs incoming registers, the global head, and
already-computed next pointers; it changes no game value, guard, or control
flow. No mitigation is justified.

## s864 retail coalescer-state writer presence

The retail oracle ran for 30 seconds with whole-RDRAM, VI-trace, and physical
watches on caller globals `0x1163E4..0x1163F0` and head global
`0x10FF18..0x10FF1C`, using the documented repeated-Start schedule. It reached
1,792 VI and the whole-RDRAM control recorded 5,199,604 writes. The caller
watch recorded 9 writes and the head watch recorded 3 writes. This selects
H-retail-writer over H-retail-no-write and rules out H-retail-control-invalid
for the run. Because the oracle's process-wide 200-hit detail cap was consumed
by the whole-RDRAM control, the target-hit PC lines were suppressed; the exact
writer PCs remain unclassified. This is one retail runtime evidence line and
does not establish that the port's invalid values are legitimate or authorize
a mitigation.

ORIGIN: retail debugger write-watch observation only; no port value, game
control flow, or mitigation behavior changed.

## s865 retail coalescer writer PCs are early-only

Added the bounded `--detail-watch N` oracle option so selected watch indices
continue printing hit PCs after the global whole-RDRAM detail cap. The oracle
rebuilt successfully. In the same 30-second retail run, whole-RDRAM recorded
5,199,605 writes, VI reached 1,792 frames at width 320, and the target watches
recorded 9 caller-global plus 3 head-global writes. Caller PCs were
`0x80000420`, `0x80000424`, `0x80000ED8`, `0x80000FFC`, and `0x8000104C`;
head PCs were `0x80000424` and `0x800021D8`. No later writer appeared because
retail remained in the width-320 phase. This selects H-init-writer for the
observed population and rules out H-control-invalid, while leaving
H-runtime-writer open for a later phase. No legitimacy or mitigation conclusion
follows.

ORIGIN: retail debugger write-watch PC attribution and VI/whole-RDRAM controls;
no game value or control flow was changed.

## Session s866 result

The 180-second retail oracle run preserved the whole-RDRAM control, VI trace,
retail ROM, repeated-Start schedule, and `--detail-watch 1 --detail-watch 2`.
The whole-RDRAM control recorded 29,825,154 writes and the VI trace recorded
10,792 frames, so the controls were live. The target watches recorded the same
9 caller-global and 3 free-list-head writes as s865, all at the early PCs
`0x80000420`, `0x80000424`, `0x80000ED8`, `0x80000FFC`, `0x8000104C`, and
`0x800021D8`. The run remained at width 320 for its full duration despite the
scheduled Start presses; therefore no later-phase writer was observable.

This strengthens H-init-writer for the observed width-320 population and rules
out H-control-invalid. H-runtime-writer remains unevaluable because the phase
discriminator never advanced. No port value, game behavior, or mitigation
changed.

ORIGIN: retail debugger write-watch PC attribution with whole-RDRAM and VI
positive controls; no port value or mitigation behavior changed.

## Session s867 result

The 70-second retail oracle run used the documented eleven-Start schedule,
whole-RDRAM positive control, VI trace, and target-write detail watches. The
whole-RDRAM control recorded 11,785,465 writes over 4,199 VI, and both target
watches fired (9 writes to `0x1163E4..0x1163F0`, 3 writes to
`0x10FF18..0x10FF1C`). Every target hit occurred at the early PCs already seen
in s865/s866: `0x80000420`, `0x80000424`, `0x80000ED8`, `0x80000FFC`,
`0x8000104C`, and `0x800021D8`. The VI trace remained width 320 for the full
run; no later phase was observed despite all eleven scheduled Start presses.

This rules out H-control-invalid for this run and strengthens H-init-writer
only for the observed width-320 population. It does not test H-runtime-writer,
because the required phase transition did not occur. The next experiment must
validate the input schedule at the PIF boundary before using another retail
watch to infer writer absence.

ORIGIN: independent retail debugger write-watch, VI trace, and whole-RDRAM
control; no port value, game behavior, or mitigation behavior changed.

## Session s868 result

The 20-second retail oracle run used the whole-RDRAM positive control, VI
trace, retail ROM, `--pif-trace`, and nine Start presses at 2–18 seconds.
Whole-RDRAM recorded 3,574,338 writes over 1,198 VI, proving the watch and
emulator controls were live. The oracle's PIF trace is printed as `[pad]`:
each scheduled press produced `0x7C4=0x10000000` and the release returned it
to zero, so Start reached the retail PIF boundary. VI remained width 320 for
the full run.

This selects H-game-state for the early schedule and rules out H-input-map:
the injector delivered Start, but those presses occurred before the
phase-appropriate title-driving window and did not advance the retail state
machine. It does not yet establish that the documented 6–56 second schedule
will reach a later phase, and it says nothing about any later writer. No port
behavior or mitigation changed.

ORIGIN: independent retail PIF button-word trace plus whole-RDRAM and VI
positive controls; no game value or control flow was changed.

## Session s869 result

The 70-second retail oracle used the phase-appropriate eleven-Start schedule,
whole-RDRAM positive control, VI trace, PIF trace, and retail ROM. The positive
control recorded 11,785,805 writes over 4,199 VI. Every scheduled press
produced `0x7C4=0x10000000` at PIF and every release returned it to zero. VI
changed from width 0 to 320 and changed origin once, then stayed at width 320
for the full run.

This is a second independent line for H-game-state under the phase-appropriate
schedule and rules out H-input-map plus a dead whole-RDRAM/PIF/VI instrument.
It does not establish why the retail state machine remains at width 320 and
does not authorize a later writer-watch or mitigation.

ORIGIN: independent retail PIF button-word trace plus whole-RDRAM and VI
positive controls; no port value, game behavior, or mitigation changed.

## Next work unit: test retail Start pulse duration

HYPOTHESIS-ID: m3-coalesce-phase-driver

Run one 70-second retail-oracle experiment with the same ROM, whole-RDRAM
positive control, VI trace, PIF trace, and eleven-entry schedule, but add
`--hold-ms 1000`. Do not add target watches or change emulated game behavior.

Competing hypotheses:

- H-short-pulse: longer Start holds produce a post-320 VI transition.
- H-game-state: sustained Start reaches PIF but VI remains width 320.
- H-input-queue: sustained holds alter the PIF pattern or produce repeated
  transitions, showing injector pulse semantics are the driver.

Discriminator: whole-RDRAM must fire; PIF must show sustained Start for each
scheduled press; and VI must show a post-320 width/origin transition. A
transition only with long holds selects H-short-pulse; sustained PIF Start
with no transition selects H-game-state; an altered/repeated PIF pattern
selects H-input-queue.

## Ranked backlog

1. Do not use the process-wide `0x8000834c` breadcrumb to select a helper
   crash site. Re-run the expanded dispatcher capture only after a new,
   phase-gateable caller/state boundary is identified independently.
2. M3 co-gates and crash families: pursue only a complete idiom inventory,
   classification of every site, and proof/guard per site. Passive breadcrumbs
   belong in queued soaks.
3. M4 correctness: outdoor `baseFixed=-32768` zero shade, attribution S=0
   triangles, then I4 `sample=64x128`; each needs independent controls.
4. Regeneration-pipeline reliability: retain the delete-before-regen rule and
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
