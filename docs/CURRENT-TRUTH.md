# Rogue Squadron 64 Recomp — current truth

Front matter for `PORTING-STATE.md`. Durable history and superseded detail are
in [`docs/PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); do not reopen those
closed lineages without a new class-level lead.

Reviewed through s843 (2026-08-13). The active blocker is the authoritative
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

## Next work unit: establish the triangle-handler dispatch positive control

HYPOTHESIS-ID: m3-drawindexed-copy-cycle

Perform one phase-gated diagnostic build/run that records dispatch of the
Factor 5 candidate triangle opcodes (0xB1, 0xB4, 0xBF) before the existing
`drawIndexedTri` breadcrumb. Keep the E9 provenance positive control in the
same run. Do not change behavior or add a mitigation.

Competing hypotheses:

- H-no-triangle-dispatch: the recipe never dispatches a candidate triangle
  opcode, so the previous null was only a reachability gap.
- H-factor5-consume-only: 0xB4/0xBF dispatches but the installed handlers do
  not call `drawIndexedTri`.
- H-wrong-handler: 0xB1 dispatches under Factor 5 and reaches inherited TRI2.

Discriminator: the E9 controls must fire, and a candidate dispatch row followed
by a draw row is the required triangle positive control. 0xB4/0xBF without a
draw row selects H-factor5-consume-only, 0xB1 with a draw row selects
H-wrong-handler, and no candidate rows selects H-no-triangle-dispatch. Only
then attempt cycle-state attribution or behavior changes.

## Ranked backlog

1. Identify which RT64 parser byte/pending/guard condition accounts for the
   lower late E9 count; no behavior change until the condition is proven.
2. Only after that classification, identify the responsible parser/counting
   path and consider an implementation fix.
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
