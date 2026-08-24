# Rogue Squadron 64 Recomp — current truth

Front matter for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable history
is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); the ledger remains
authoritative for exact commands and probe rows. Maintained in Session 2211
(2026-08-23); behavioral and source evidence is current through s2211.

The detailed s2164–s2197 chain is archived in
[`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md) §43; s2198–s2206's exact rows remain in
the append-only ledger. This file is the compact operational state, not a
second ledger.

## Current state

- Overlay dispatch is fixed enough for mission entry and post-sec2 outdoor
  presentation. The original boot/menu overlay explanation is closed.
- The qualified route reaches title VI `1024 @ 0x00790400` and hangar VI
  `512 @ 0x006AB400` with `ROGUESQ_SPIN_YIELD=1`,
  `ROGUESQ_LLE_UNGATED=1`, and `ROGUESQ_LLE_SOLO=1`. Spin yield is
  environment-gated and default-off.
- Product multi-header freelist restore is on. Garbage-CIMG and wrap-drop
  mitigations are off. Any future mitigation must name its writer, state
  whether the value is legitimate, and include an `ORIGIN:` line.
- M5 audio is still defaulted to the silent `Broke` stub. The Factor 5
  image arm is opt-in through `ROGUESQ_AUDIO_UCODE=1`; it is not default-on.
  The M5 plan is [`M5-AUDIO-PLAN.md`](M5-AUDIO-PLAN.md).
- s2162 fixed the unsigned PATCH `MEM_BU(0X1AD0, 0X80140000)` by using an
  S32-addressed KSEG0 value; the image arm then returned from
  `waitForAnyAudioSlot` and reached title/hangar. s2163's same-build retry
  selected `H-CinematicRegress`: unset/`=1` failed intermittently in the
  post-wait 640 cinematic while `=0` reached title/hangar. The default flip
  was reverted.
- The image arm performs real DMEM work and generated DMA writes, then
  returns `Broke`. Its host canary is inside the generated mix-buffer span;
  `canary_ok=0` is a probe field and does not gate completion, writeback, or
  DMA recording. MORT is a CPU speech asset, not a second RSP image.
- s2184 classified one completing image run as title/hangar-only: 5,841
  joins, a positive 640 phase control, zero 640 image joins, and zero
  overlap with six named physical words. s2185 independently confirmed
  that retail writes all six words, but only named the `0x2231EC` writer;
  five retail writer identities remain open. These results are scoped and
  do not authorize a guard, task rewrite, or default flip.
- s2187 independently repeated the image-arm census with 6,118 joins and a
  positive `640 @ 0x00696100` phase. Joins were title/hangar-only (3,449 at
  `1024 @ 0x00790400`, 2,669 at `512 @ 0x006AB400`, zero at target 640) and
  none overlapped the six named words. The run later crashed in
  `recomp::do_rom_read` after a later 640 phase; this is scoped evidence,
  not an explanation of the intermittent cinematic failure.
- s2188's corrected single-run retail writer census passed the whole-RDRAM
  control (33,145 writes), observed seven 640-VI rows at origins
  `0x00696100`/`0x00696600`, and saw all six named words written: counts
  `5, 1, 5, 23,124, 9, 1` for the six targets in watch order. Histograms
  identify narrow writers for targets 1/2/3/5/6 (`0x80018F5C`,
  `0x80018F60`, `0x800078EC`/`0x800A8144`, `0x800078EC`/`0x80018F60`,
  `0x80057100`); target 4 has 123 distinct PCs with no overflow. This is
  single-source oracle evidence that corroborates s2185's target-write
  result, rules out coverage failure, and does not yet distinguish the two
  640 origins or explain the failing image join.
- s2189 added repeatable `--pc-hist-phase ORIGIN` buckets to the retail
  oracle, preserving the whole-RDRAM control and collecting writer PCs per
  target only at width 640 and the configured origin. One run had 33,011
  control writes, 211 rows at `0x00696100`, 221 at `0x00696600`, and target
  phase matrices `1/0/0/1203/0/0` and `4/1/5/8207/5/1` writes for targets
  1–6. The writer sets split by origin, selecting H-PhaseSplit; target 4 is
  broad in both buckets. This is single-source oracle evidence and does not
  authorize a port guard or audio default change.
- s2190's batched fixup-injected port census passed its own 640 positive
  control and reached title `1024 @ 0x00790400` plus hangar `512 @
  0x006AB400`. At the covered port origin `0x00696100`, it observed target
  unique-PC rows `1/0/2/65/1/1` with sparse writer sets `0x80057100`, absent,
  `0x800078EC`/`0x800A8144`, broad, `0x800078EC`, and `0x80057100` for
  targets 1–6. Retail at that origin is `1/0/0/1203/0/0` with target 1
  writer `0x80018F5C`; the port therefore selects H-PortOriginMismatch at
  the covered origin. The route exited before port origin `0x00696600`, so
  those six cells remain uncovered rather than null. This is two-line
  port/oracle evidence and authorizes no guard, task rewrite, or default flip.
- s2191's same-built no-menu retry passed the writer control (29 records) and
  the phase control (640 at `0x0066A500` and `0x00696100`), but still produced
  no `0x00696600` phase. It aborted in `get_function(0)` from
  `slotDispatcherIter` after the first-origin phase. First-origin target rows
  were `1/0/2/54/0/1`; all six second-origin cells are uncovered. This selects
  H-PortSecondOriginAbsent, rules out H-PortCoverageFailure for this run, and
  authorizes no writer guard, task rewrite, or audio default flip.
- s2192's same-build logging-cadence A/B passed the writer control in both
  arms (noisy 29, quiet 31) and the phase control at `0x0066A500` and
  `0x00696100`, but neither arm reached `0x00696600`. The quiet arm later
  crashed in `slotDispatcherIter+3508` with last guest PC `0x80022160`, while
  the broad-logging arm remained alive until its watchdog timeout. First-origin
  target rows were noisy `1/0/2/54/0/1` and quiet `1/0/2/69/1/1`. This refutes
  logging cadence as a route to the second origin and shows that logging
  changes the failure mode; it does not prove a shared crash boundary or
  authorize a guard, task rewrite, or audio default flip.
- s2193 isolated the grouped route logging into quiet, broad, and route arms.
  All three passed the writer control (31/30/31) and the phase control at
  `0x0066A500` and `0x00696100`, but none reached `0x00696600`. First-origin
  target rows were quiet `1/0/2/64/1/1`, broad `1/0/2/65/1/1`, and route
  `1/0/2/65/1/1`; target order is the six physical words listed in s2190.
  All three emitted crash markers from `slotDispatcherIter+3508`; quiet and
  route ended with guest PC `0x80022160`, while broad ended with `0x80007904`.
  This selects `H-SecondOriginStillAbsent`, refutes the planned
  `H-NarrowRouteLogBoundary` and the specific “broad arm remains live” form of
  `H-LoggingOnlyThroughput`, and leaves individual category effects unresolved.
- s2194 isolated the three remaining route log categories into quiet, slot,
  event, and audio arms. Writer controls fired 30/29/30/29 times; all four
  arms reached 640 origins `0x0066A500` and `0x00696100`, and each optional
  category control was positive in its arm (8,192 slot-dispatch, 130
  event-wiring, and 266 audio-return rows). None reached `0x00696600`.
  Each arm produced the same `slotDispatcherIter+3508` crash boundary with
  guest PC `0x80022160`. At the first origin, all arms observed target cells
  1, 3, 4, 5, and 6; target 2 remained absent. This selects
  `H-NoIndividualCategoryBoundary`, refutes the slot/event/audio individual
  boundary hypotheses and coverage failure, and leaves pairwise logging
  interaction or another source open.
- s2195 ran the planned pairwise logging A/B after recreating its missing
  self-contained runner: quiet, slot+event, slot+audio, and event+audio.
  Writer controls fired 29/29/31/30 times; all four arms reached 640 origins
  `0x0066A500` and `0x00696100`, and none reached `0x00696600`. Optional
  controls were positive (8,192 slot, 130 event, and 266/263 audio rows).
  First-origin target cells were quiet `1/0/2/61/0/1`, slot+event
  `1/0/2/63/0/1`, slot+audio `1/0/2/64/1/1`, and event+audio
  `1/0/2/62/1/1`. All arms emitted 36 crash markers, but endpoints diverged:
  quiet ended at `allocAndInitGridCellArray+1280` / guest `0x80001C94`,
  slot+event at the Metal barrier path / guest `0x8000B650`, and the two
  audio pairs at `slotDispatcherIter+3508` / guest `0x80022160`. This selects
  `H-NoPairInteraction` for second-origin reachability and refutes the three
  named pair interactions at that scope; the endpoint divergence is not a
  shared route-boundary explanation.
- s2196's retail oracle caller control passed with 10,000 whole-RDRAM writes,
  1,173 `osViSwapBuffer` executions, and repeated 640 VI rows at both
  `0x00696100` and `0x00696600`. The port caller probe passed its first-16
  control, writer control (29), and first-origin phase, but no second-origin
  phase appeared before the post-first-origin collection ended. Retail's
  execution histogram has callers `0x8001BE24` and `0x80019B14`; the port's
  host-symbol table recovers both corresponding generated callers at the first
  origin. Port swap arguments there were `0x62B800` plus `0x695C00`, while
  retail control rows showed `0x805D4000`/`0x8066A000`. `$r31-8` was
  `0xFFFFFFF8` in every port row, so it is not a usable guest caller field in
  this recomp; host-symbol mapping is diagnostic fallback only. This exposes
  a caller-contract/argument mismatch, not the missing-second-origin cause.
- s2197's independent retail swap table passed the whole-RDRAM control
  (10,000 writes), the swap execution control (1,171 hits), and repeated
  640-VI rows at both `0x00696100` and `0x00696600`. At the first origin,
  retail had `(prev_pc=0x8001BE24, a0_phys=0x0062B800)` and
  `(prev_pc=0x80019B14, a0_phys=0x0062B800)`; at the second it had the first
  pair. The port already produced that same first pair at its first origin
  in s2196. This selects H-RetailPortCallerParity, refutes
  H-PortMissingSecondCaller and H-CoverageFailure at this scope, and moves
  the discriminator past the guest swap call to host VI-state publication.
- s2198 ran the batched host boundary table after an independent retail
  preflight. Retail again passed the whole-RDRAM control (10,000 writes), the
  `0x80035500` execution control (1,579 swaps), and repeated 640 rows at both
  target origins, including `(prev_pc=0x8001BE24, a0_phys=0x0062B800)` at
  both. The port passed its caller control (16 rows), writer control (29
  rows), and first target phase, then produced 64 capped rows each for
  first-origin commit, screen, and swap edges but no second-origin phase or
  boundary row. The run later aborted in the existing unaligned PI-DMA
  assertion, so this run selects H-CoverageFailure for the planned joined
  edge discriminator rather than treating a second-origin null as a commit
  or screen boundary. A source audit found `ViState::field` is read by
  `update_vi` but never assigned in `events.cpp`; H-ViFieldAlternation is a
  new bounded candidate, not yet a landed fix. The logger's atexit summary
  was not reached because the process aborted.
- s2199 ran the same-built field-alternation A/B after a retail oracle
  preflight. Both arms passed caller control (16) and writer control (29) and
  reached `0x00696100`. With `ROGUESQ_VI_ALTERNATE_FIELDS=0`, the port filled
  64 capped first-origin commit and screen rows and zero second-origin rows.
  With `=1`, it filled 64 capped commit and screen rows at both
  `0x00696100` and `0x00696600`, with caller rows at both origins. This selects
  H-ViFieldNotToggled at the qualified port scope and refutes
  H-SecondOriginElsewhere and H-CoverageFailure for this A/B. The target-phase
  causal claim is single-source port evidence: the independent oracle only
  corroborated retail field 0 on the sampled 320 route. The alternation knob
  remains diagnostic and default-off.
- s2200's phase-gated retail oracle passed the whole-RDRAM positive control
  (10,000 callbacks, then removal), and its VI trace showed repeated 640 rows
  at both `0x00696100` and `0x00696600`. The `0x80034D90`
  `osViGetCurrentField` watch produced 202 target rows at the first origin and
  213 at the second; every row returned `v0=0`, with zero `v0=1` rows. This
  independent target-phase result refutes H-RetailFieldAlternates and selects
  H-RetailField0Target. The s2199 port knob remains a route-recovery
  diagnostic, not retail ground truth; the next discriminator is the retail
  mode/field-descriptor or swap-buffer source of the second origin.
- s2201's single-run retail descriptor/source census passed the whole-RDRAM
  control (10,000 callbacks, then removal), repeated both target 640 origins,
  and collected 13 `osViSetMode` executions plus 1,593 `osViSwapBuffer`
  executions. All seven printed 640-wide descriptors fit the cap and had
  `fldRegs[0].origin=0x500` and `fldRegs[1].origin=0xA00`; their yScale pairs
  varied, but no descriptor supplied either absolute target origin. Target
  swap rows retained `$a0=0x0062B800` at `0x00696100` and `0x00696600`
  (36 and 16 rows, respectively; the first origin also had 37 rows from the
  second caller). At the pre-swap observation scope this selects
  H-SwapBufferSource and refutes H-FieldDescriptorSource, but the row reads
  the current VI origin before `osViSwapBuffer`; a causal post-swap match is
  still required before changing the port.
- s2202's same-run post-swap oracle table passed the whole-RDRAM control
  (10,000 writes), observed both target 640 origins, and produced 86 joined
  rows with zero row overflow: 71 at `0x00696100` and 15 at `0x00696600`.
  The target rows carried `a0_phys=0x0062B800` except for one
  `0x00790000` row; every joined mode descriptor had field origins `0x500`
  and `0xA00`. Neither `a0 + fld0.origin` nor `a0 + fld1.origin` matched the
  joined next origin in any row. This single-source retail evidence selects
  H-PostSwapStateBase and refutes post-swap field-descriptor arithmetic and
  join coverage at this scope; it does not identify the later origin
  producer.
- s2203's retail `__osViNext` context table passed the whole-RDRAM control in
  both collections. The exact 45-second recipe reached both target origins but
  overflowed the 256-row cap (256 joined, 171 overflow), so that collection
  selected H-ContextCoverage. A fixed 10-second retry reached both origins with
  zero overflow: 192 joined rows, 96 at each origin, 277 dropped non-target
  joins, and zero pending rows. Every joined row had a valid context and mode,
  `state=0x0001`, `framep_phys=0x00695C00`, field origins `0x500`/`0xA00`, and
  `candidate0=0x00696100` or `candidate1=0x00696600` matching its next origin;
  `current_field` was 0/1 respectively. This single-source retail result
  selects H-ContextFramep and refutes H-ContextOther and H-ContextCoverage at
  the fixed scope. Together with s2202's independent post-swap table, it moves
  the open comparison to the port's `ViState` field/frame/mode state. No port
  guard, mitigation, task rewrite, or audio default change was made.
- s2204's same-build port commit table passed the all-width prefix control in
  both arms and collected target-window rows with zero overflow: control 185,
  alternate 150. Both arms had framebuffer `0x00695C00`, guest mode
  `0x80128DA0`, field origins `0x500`/`0xA00`, and candidates
  `0x00696100`/`0x00696600`. Control selected field 0 for all 185 rows and
  committed only `0x00696100`; the opt-in alternate arm selected field 0/1
  for 75/75 rows and committed the corresponding first/second origins. This
  selects H-PortFieldSelector at the qualified target scope and refutes
  H-PortStateTuple's predicted candidate mismatch and H-PortCommitOrdering's
  predicted candidate/commit divergence. The port logger reports
  `next_state->state=0`, while retail's context table reports `state=1`; that
  semantic state-word difference is recorded but does not alter either
  candidate sum or committed origin. Both arms had eight positive-control rows
  and no `[CRASH]`/`[ABORT]` marker. The independent retail oracle preflight in
  this iteration again passed its 10,000-write control and produced 203 joined
  context rows with both target origins. No default flip, guard, mitigation, or
  task rewrite was made.
- s2205 ran the prescribed same-build concurrent field-selector A/B with the
  qualified silent-audio route and the port context logger enabled. Both arms
  passed the positive prefix control (`8` rows), collected the capped `256`
  context rows, and committed the first target origin `0x00696100`; control
  committed the sibling origin `0` times and alternate committed it `128`
  times. Neither arm produced a later `1024 @ 0x00790400` or
  `512 @ 0x006AB400` phase, and neither emitted `[CRASH]`/`[ABORT]`; both were
  SIGKILLed by the 180-second watchdog. This single-source port A/B refutes
  H-ViToggleNonTargetDamage at the covered target scope, but selects none of
  the three predeclared stability/regression outcomes because the control also
  lost the later phases. The alternate commit result without a later phase
  leaves post-target VI presentation/consumption and logger sensitivity open;
  no default flip, guard, mitigation, task rewrite, or audio dispatch change
  was made.
- s2206 ran the prescribed same-build concurrent logger-isolation table with
  logged/quiet × field-0/field-1 arms. All arms ran to the 180-second watchdog
  with zero `[CRASH]`/`[ABORT]` markers and zero title/hangar phases. The
  logged control passed the early `640 @ 0x0066A500` and committed only
  `0x00696100` (151 rows); logged alternate passed the early control, committed
  `0x00696100` (75) and `0x00696600` (75), and emitted the sibling phase. Quiet
  control passed the early control and emitted `0x00696100`; quiet alternate
  instead emitted `0x0066AA00` before later emitting `0x00696100`. This was a
  provisional early-prefix observation, not a corruption finding: s2208's
  independent retail trace shows that `0x0066AA00` is a legitimate early
  origin. The post-target consumer remains unresolved because no arm reached
  title/hangar. No default flip, guard, mitigation, task rewrite, or audio
  dispatch change was made.
- s2207's independent retail-oracle census passed the whole-RDRAM positive
  control with 10,000 writes and successful watch removal, but the undriven
  dummy-video recipe produced only the boot `320 @ 0x006DD280` row and zero
  width-640 rows in 45 seconds. Neither `0x0066A500` nor `0x0066AA00` was
  observed. This selects H-RetailTraceCoverage for that recipe only; it is
  not evidence about retail's early-origin set. The next census must use the
  documented Rice video plugin and Start schedule.
- s2208's Rice-driven retail census passed the whole-RDRAM positive control
  (10,000 writes, successful removal) and reached width 640. Its early trace
  included `0x0066A500`, `0x005D4500`, and `0x0066AA00`, followed by repeated
  `0x00696600`/`0x00696100` target origins; it later reached title and hangar
  as well. This independent result selects H-RetailEarlyAA00, refutes
  H-RetailEarlyA500 as an exclusive explanation and H-RetailTraceCoverage for
  the Rice recipe, and establishes that the port's quiet `0x0066AA00` is
  retail-grounded at origin level. The early context/field selector remains
  unidentified.
- s2209's single-source retail context join passed the whole-RDRAM positive
  control (10,000 writes), joined 468 rows with zero drops and zero overflow
  at the 1024-row cap, and covered five observed 640 origins. The early rows
  split by field: `0x0066A500` was field 0/candidate 0 (17/17),
  `0x0066AA00` was field 1/candidate 1 (139/139), and `0x005D4500` was field
  0/candidate 0 (121/121). The target rows independently retained the same
  relation (`0x00696100`: 96/96 field 0; `0x00696600`: 95/95 field 1).
  This selects H-RetailEarlyContextAlternates and refutes fixed-field,
  unexplained-candidate, and coverage forms at this scope. It identifies the
  retail early selector, not the port's early context tuple; a port census is
  next.
- s2210's bounded port context census passed its positive prefix (8 rows),
  admitted 512 width-640 rows with zero overflow, and observed early
  `0x0066A500` and `0x005D4500` rows plus target `0x00696100` rows. Every row
  selected field 0. The port's early contexts produced candidate 0 and
  committed `0x0066A500`/`0x005D4500`; no `0x0066AA00` commit appeared. In
  combination with s2209's independent retail table, this selects
  H-PortEarlyContextFixedField at the qualified control scope, refutes
  H-PortEarlyContextParity and H-PortEarlyContextCoverage there, and moves
  the open question to the host VI field source. No default, mitigation, task,
  or audio-dispatch change was made.
- s2211's independent retail preflight passed the whole-RDRAM positive control
  (10,000 writes), reached all five relevant 640 origins, and observed
  `osViGetCurrentField` return `v0=0` at every early and target origin,
  including `0x0066AA00` and `0x00696600`. The same-built port table passed its
  prefix control (8 rows), collected 512 width-640 rows with zero overflow,
  and selected field 0 in all rows. Its `VI_V_CURRENT_LINE_REG & 1` was zero
  in every observed bucket: 127 rows at `0x0066A500`, 128 at
  `0x005D4500`, 135 at target `0x00696100`, and 122 other 640 rows; no bit-1
  row or `0x00696600` commit appeared. This selects
  H-PortCurrentRegFixed and refutes H-PortCurrentRegAlternates,
  H-PortCurrentRegDecoupled, and H-PortCurrentRegCoverage at the qualified
  scope. The current-line register is not the missing field-one producer;
  the next discriminator is the guest mode's `comRegs.vCurrent`. No default,
  mitigation, task rewrite, or audio-dispatch change was made.

## Active backlog

The backlog is one monotonic sequence. Closed investigations are not active
work items.

1. **M5 A1 identify the missing second-origin transition; blocks
   default-on.**
   s2190 selected H-PortOriginMismatch at port `0x00696100`, s2191 selected
   H-PortSecondOriginAbsent, and s2192–s2195 showed that broad, grouped,
   individual, and pairwise route logging do not reach `0x00696600` despite
   positive controls. s2195's divergent crash endpoints are not a stable
   route-boundary discriminator, so pairwise logging is closed at this
   scope. s2196 found that `ctx->r31-8` is always `0xFFFFFFF8`; s2197 then
   retained the retail target-origin table and found the port's first-origin
   `(0x8001BE24, 0x0062B800)` pair also occurs in retail at
   `0x00696600`. s2198 found that the port commits and consumes only
   `0x00696100`; s2199's same-built A/B showed that toggling the host
   `ViState::field` after each VI commit restores repeated commits and screen
   consumption at both target origins. s2200's independent target-phase watch
   found `osViGetCurrentField` returns only field 0 at both retail origins.
   s2201 found all observed 640 mode descriptors use field origins `0x500` and
   `0xA00`, while same-run target-origin swap rows carry `$a0=0x62B800`.
   s2202 joined each 640 swap to the following VI callback with both target
   origins covered and zero row overflow. The observed framebuffer base plus
   either active field origin never equaled the next origin, selecting
   H-PostSwapStateBase. s2203's fixed-scope retail `__osViNext` join then
   selected H-ContextFramep: the context's frame pointer plus the field
   selected by `VI_CURRENT_REG & 1` exactly produced both target origins.
   s2204's target-scoped port table selects H-PortFieldSelector: the port has
   the retail frame/mode candidates and follows the selected field, while the
   field-0 baseline is the only arm that misses the sibling origin. s2205's
   same-build stability A/B reproduced the target commit split, but both arms
   stalled before title/hangar under the context logger: control had
   `target_second=0`, alternate had `target_second=128`, and both had zero
   later phases and zero crash markers before watchdog SIGKILL. This leaves the
   predeclared stability/regression discriminator unresolved and makes logger
   sensitivity a bounded next candidate. s2206's four-arm logger isolation
   then found that the quiet field-1 arm takes early origin `0x0066AA00`
   rather than the logged/other-arm positive prefix `0x0066A500`, while all
   arms still stall before title/hangar. This was a provisional early-prefix
   observation, not a corruption finding: s2208's independent retail trace
   shows that `0x0066AA00` is legitimate. s2207's undriven
   retail census passed its whole-RDRAM control but never reached a 640 phase,
   so it selected H-RetailTraceCoverage for that recipe rather than
   classifying either origin. s2208's Rice-driven census passed the control and
   observed both early origins, selecting H-RetailEarlyAA00; it makes the quiet
   port origin legitimate but does not identify its retail context selector.
   s2209's context join shows that retail selects field 0 for `0x0066A500` and
   `0x005D4500`, field 1 for `0x0066AA00`, and the corresponding field for both
   target origins, with valid frame/mode candidates and no coverage overflow.
   s2210's all-width port table shows the qualified default selects field 0 for
   every observed 640 row, including both early mode contexts, and therefore
   never commits `0x0066AA00`. The next unit identifies whether the port's
   host VI current-field register supplies an omitted alternation source or is
   itself fixed at zero. Keep the field knob and logger diagnostic-only.
2. **M5 drain in-loop tick A/B; parked.** s2125 selected
   `H-PumpIrrelevant` only at route scope. s2126–s2128 failed to put both
   drain arms in the target comparison despite positive controls. Resume
   only with a new renderer-recovery or ground-truth discriminator.
3. **M3 crash work.** Continue only as systematic idiom-class audits with
   a named discriminator. The dormant `slotDispatcherIter+872` class has
   7,659 clean hangar calls in its guarded run; no mitigation is authorized.
4. **Hangar visual artifact.** Malformed-triangle H2 is refuted by writer
   attestation and consumer-mode H1 by the RT64 census. H3 is unavailable
   because the oracle cannot screenshot the LLE path. Do not repeat the
   `0xD60` scan.
5. **Generated-symbol renaming sweep; closed.** s2149 closed the two-line
   overlay-move class and s2150 selected `H-LeftoverAllHolds` for leftover
   `fake_func_*` with ELF size `> 0xC`. The remaining generated names are
   the five parked/intentional holds `func_8000040C`, `func_800927B0`,
   `func_80092A54`, `func_80092CF0`, and `func_800E9AE0`. Do not re-census
   or invent names for them.

## Durable boundaries

### Route and rendering

Factor 5 custom opcode mappings and independent-ground-truth requirements
are in [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md) and
[`tools/oracle/README.md`](../tools/oracle/README.md). The runtime cannot be
its own witness for a null result.

Forced LLE is the route gate under the common wrapper. The accepted
four-arm table selected `LLE_UNGATED=1, LLE_SOLO=1`: `11` reaches title and
hangar, `01` reaches title only, and `10`/`00` reach neither. This is
recipe-level port evidence, not an explanation of audio or PCM. Menu spin
yield is a diagnostic route aid, not a default behavior change.

Route history is in `PROJECT-OVERVIEW.md` §§36–43. s2093–s2096 closed the
wrapper, task-thread, SP external-delivery, and guest-receive route at the
qualified recipe scope. s2111 superseded B40 as a route-admission cause at
that recipe; s2112 selected recipe timing for the unreproduced phase-7
origin split. Do not reopen the SP queue or B40 read-site census.

### M5 status, service, wait, AI, and MORT

The generated tree reaches both target phases. Direct service entry/exit and
the service gate/loop are live. The port observes the legitimate slot-0
sequence through the service store at `0x8009B7EC`, guest address
`0x80154620`, including `0x03 -> 0x00`. Retail independently observes the
same status-table cycle. Retail does not execute port crash labels
`0x8000B650`/`0x80095D54`; that is a PC-scope boundary, not permission to
change port wait or guard behavior.

s2122 is a normal-path hangar key-on contract at sampled scope: four valid
`0xC0` divides and a normal tail with no early-return guard hit. s2123
independently establishes that the completion-wait contract is live on the
qualified retail route. s2125 closed the pump's sampled route-admission
question. A10 is parked after three coverage-only pairs.

s2132–s2133 plus s2152–s2153 close the sampled AI-status/queue boundary:
retail queues through `osAiSetNextBuffer`; the only status poll is the
in-function `__osAiDeviceBusy`; on the covered title/hangar route it never
returns FIFO-full; and the generated caller ignores v0. Do not change
`osAiGetStatus_recomp` or `osAiSetNextBuffer_recomp`.

s2135–s2140 close the sampled RSP-image/task/output edge:
`factor5b_rsp.toml` is the retail audio image, MORT speech is separate,
task fields match, and both retail and port write `data_ptr+0x100`.
s2138/s2139/s2151 close the MORT remaining-class reference decode. None of
these results defaults the image arm or rewrites task fields.

s2154–s2158 close the canary location/effect and host-isolator questions:
the canary lies in the mix buffer, is log/storage only, and the only live
image-arm isolation is the `ROGUESQ_AUDIO_UCODE` dispatch in
`get_rsp_microcode`. s2159 closed the named blocker census as policy-only;
s2160–s2163 then showed why the policy remains opt-in: the pre-S32 wait fault
was fixed, but the same-build image arm still has intermittent cinematic
regressions. The full pointer, heap, transform, NaN, and image-DMA chain is
archived in `PROJECT-OVERVIEW.md` §43.

The stock `aspMain` contract is not the game's MusyX contract. C88 testing
selected reversed-or-suppressing polarity at sampled port gate scope; no
blanket gate flip is authorized.

The port's `ViState::field` is host-side state used by `update_vi`; in the
default arm the only visible assignment is initialization at zero, while the
field alternation knob toggles it after each VI commit. s2210 shows that this
default field 0 is used across the early 640 contexts, unlike retail's
field-1 `0x0066AA00` context. s2211 shows the RT64-facing current-line bit is
also fixed at zero in the qualified port rows, so it is not that missing
source. The legitimate field-one producer remains open; this is not
permission to enable the knob by default.

### M3, M4, and generated symbols

The `-0x25A4` pointer-chase family, six-site PIC class, ten-site audio-slot
class, dormant slot-dispatch census, two-line overlay-move class, and
leftover `fake_func_*` size-`> 0xC` class are closed at their stated scopes.
M3 resumes only as an idiom-class audit or with a new discriminator. M4
accumulator/beam evidence rules out the old shade-lane theory but is not
pixel ground truth. Remaining `func_*` placeholders are semantic holds or
intentional non-sync entries.

## Superseded conclusions

Detailed reversals are archived in `PROJECT-OVERVIEW.md` §§26 and 35–43 and
remain in the append-only ledger. Operationally:

- “640 is a flaky crash,” missing-input, missing-wait-return, and
  unqualified PCM-null claims were believable while target-phase rows were
  absent. Same-run controls and the qualified LLE/spin recipe later reached
  both phases.
- The old title/hangar callback split and global zero-payload image-DMA
  claim were believable before joins carried guest address/full-span
  identity and before a nonzero hangar task was sampled.
- Clean-stub, canary-poison, final-E50, uniform-gate, and host-isolator
  explanations were believable before complete task/consumer and
  writer-specific tables existed. Current controls show real image DMEM
  activity, a mixed retail gate, and sampled nonzero PCM joins; they do not
  authorize a runtime change.
- The s2160 wait-slot crash was initially believable as a guest wait/slot
  defect. s2161 named retail's count-byte writers and matched the fault to an
  unsigned PATCH address; s2162 fixed that PATCH and reached title/hangar.
- The s2163 cinematic regression is not explained by NULL pointers,
  guessed KSEG0 addressing, missing +0x50 or heap0 stores, a deterministic
  match-keyword hang, or retail absence from the transform/vec3 path:
  s2164–s2182 independently refuted each at its stated scope. The failure
  remains intermittent and unresolved.
- s2184's title/hangar-only image-DMA result is a completing-run result, not
  a universal claim. s2185's retail writer run proves target writes exist,
  but incomplete per-target attribution leaves the failing image join as
  the next discriminator. s2187's positive-control run independently
  repeats the title/hangar-only result, but its later PI-DMA crash is not
  evidence about the target cinematic phase.
- s2190's missing `0x00696600` port cells are a route-coverage limitation,
  not evidence that the six target writers are absent there. The covered
  `0x00696100` mismatch is independently meaningful because the s2189 retail
  matrix supplies the comparison origin and sparse writer identities.
- s2192's noisy/quiet A/B is not evidence that broad logging is the route
  boundary. Both arms missed the second origin with positive controls; the
  different quiet crash/noisy timeout outcomes identify a logging-sensitive
  failure mode, not a writer defect or permission to add a mitigation.
- s2194's category-isolation A/B is not evidence that any one optional log
  category is the route boundary. All four arms passed their controls and
  first-origin phases, missed the second origin, and converged on the same
  crash boundary; target-writer sparsity remains an observation, not a reason
  to guard or rewrite a guest store.
- s2196's bounded retail execution samples made the target-origin framebuffer
  arguments look unlike the port's first-origin rows. s2197's same-run
  origin-keyed table shows the target-origin retail pair is
  `(0x8001BE24, 0x0062B800)`; the earlier non-target argument rows were
  outside the discriminator. The old caller/argument mismatch framing is
  superseded and does not explain the missing port second-origin publication.
- s2198's H-CoverageFailure selection was believable because its
  no-alternation port run stopped before a second-origin boundary row and
  later aborted in PI-DMA. s2199's same-built `=1` arm reaches both origins
  with positive controls, so that coverage result is superseded as an
  explanation of the second-origin transition; the remaining question is
  why retail selects the second field.
- s2199's H-ViFieldNotToggled result remains a valid port A/B observation, but
  its causal interpretation as retail field alternation is superseded: s2200
  sampled `osViGetCurrentField` at both retail target origins and observed
  only `v0=0`. The knob proves that selecting the sibling VI descriptor can
  recover the route; it does not identify the retail writer or selector of
  that sibling descriptor.
- s2201's descriptor/source result is valid only at the pre-swap observation
  scope, not as a causal explanation of target origins. The oracle's
  `VI_ORIGIN` value was sampled before `osViSwapBuffer` committed the next
  state; s2202's joined rows now show that the swap framebuffer plus either
  active field origin does not produce the following target origin. The
  remaining source is the later VI context/arbiter producer.
- s2206's H-NonTargetRouteDamage selection was believable because the quiet
  field-1 port arm emitted `0x0066AA00` instead of the logged arms'
  `0x0066A500`, and the required early control was absent in that arm. s2208's
  independent Rice trace observes both origins in the retail sequence, so the
  origin substitution alone is not evidence of route damage. The port-versus-
  retail early context tuple remains open.

## Evidence ledger summary

History through s1879 is in `PROJECT-OVERVIEW.md` §§33–35. The VI-1024 and
spin-yield chain is §36; M5 archives through s2047 are §§37–38; the late
route/fill boundary is §39; s2080–s2108 is §40; B40 is §41; and the
s2113–s2158 contract/MORT/AI/canary archive is §42. The s2164–s2197
pointer, failure, image-DMA, writer-parity, and VI-caller archive is §43;
s2198–s2209's VI-boundary and retail-ground-truth work is recorded in the
ledger.
Exact commands, counts, failed retries, and session headings remain in
`PORTING-STATE.md`.

Selected hypotheses must not be widened from single-source or single-arm
observations. In particular, do not re-flip the image default, S32-address
by guess, NULL-skip, skip/allow `matchKeywordWithPriority` or its loads,
disable `NAN_CHECK`, add a wait/slot guard, or land a copyToRAM/CIMG
writeback guard. Do not treat last-guest-PC `0x8000834c` as the abort site.

## Method and safety rules

- Ask the retail oracle for ground truth before adding an instrument. Arm
  its whole-RDRAM positive control first; watches are physical addresses and
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
- A mitigation is not an explanation. Name the writer, state legitimacy,
  and add an `ORIGIN:` line before landing a skip, allow, guard, or restore.
- Never add a diagnostic field without a whole discriminating table and an
  outcome that selects among hypotheses. Repeated counters are not a work
  unit.
