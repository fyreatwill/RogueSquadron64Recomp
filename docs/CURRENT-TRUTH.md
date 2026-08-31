# Rogue Squadron 64 Recomp — current truth

Operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable background
and archived session detail are in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
This file is the compact active-state record; full run logs live under
`scratch/agent/` and the session evidence documents.

Current maintenance marker: Session 3458 (2026-08-31). This record was
compacted during the next maintenance iteration; sessions 3201–3445 remain in
the append-only ledger and overview archive.

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated spin-yield/F5-LLE route. Hangar geometry and
color artifacts remain. Audio is not production-complete: the Factor 5 image
task is the qualified real-audio arm; `musyx_stub`/Broke is the silent control.

The default route returns from the attract viewer and reaches the cinematic
loop, but the stage advancer sees null `0x800B0934`; the initializer at
`0x800A62B4` is skipped while port skip-allow is zero. Retail independently
sets that byte and reaches title. Do not force the flag or bypass state.

M5 is the active engineering thread. The status-03 worker/clear contract,
task ABI, completion/delivery, callback-table, field348 input-to-clear edge,
send/receive zero-message boundary, and first consumer boundary are closed at
their measured scopes. The remaining qualified gap is the first output/state
contract:

- Retail `0x80001CC8` sees varied `v1` values while `s1=0x80194B20`.
- Both port arms reach the same consumer/output controls, but
  `0x80001CB8` sees `0x801Bxxxx` state pointers and `0x80001CC8` returns `2`.
- Earlier hangar-qualified `rs_free` rows still had `s1=0x80194B20`, pointed
  word `0x80194B40`, and `a0=0x801BEEB0`; the repaired title route instead
  shows stable `s1`/pointed-word tuples in the `0x801Bxxxx` state family.
  Retail-equivalence of these contexts remains unqualified.
- The generated host wrapper reports `ra=0`; the exact clobber is unresolved.

The s3449 rerun repaired the state-pointer witness's hard-coded hangar-only
phase gate. Both arms emitted 512 title entry and 1,024 title checkpoint rows
at origin `0x790400`, with no crash; sampled `s1` and pointed-word values
were unchanged from entry through post-receive and pre-consumer in both arms.
The independent retail field watch also observed the matching title tuple
(`s1=0x801B1590`, state pointer `0x801B95F0`) at the consumer site. This
closes the phase-mismatch defect and establishes title pointer parity at the
observed `rs_free` boundary with two evidence lines, but does not locate the
downstream output-contract cause or explain the alternate `0x80194B20` route.

Session 3450's fixed oracle control passed 1,000 whole-RDRAM callbacks,
completed 3,273 VI, and recorded 742/742/742/741 executions at
`0x80001C98`/`0x80001CB8`/`0x80001CC8`/`0x80001F84`; its field tables had
460/511/511/458 unique rows. The port silent and image arms remained mutually
identical, but the oracle fields (`s0`, `s1`, source word, branch selector,
source byte, branch state) are not yet exposed by the port witness, so parity
versus divergence remains unevaluable.

M5 audio source work remains unresolved upstream: qualified port image-stage
rows carry zero source/output PCM, while retail independently writes nonzero
PCM spans. Do not change waits, slots, status handling, consumer dispatch,
clear behavior, or PCM writeback while locating the state-pointer edge.

Session 3451's image-arm zero-row verdict was a stale interpretation of the
retained log. Session 3452's fresh build and two-arm run showed the schema
positive control and all four target-PC buckets in both arms: 2,048 rows per
arm, with target counts 514/510/510/514, plus 512 consumer and 343 output
rows. The retained s3449 logs independently show the same image control. This
closes the image-arm control defect and permits the planned join.

The sequential silent/image rows diverge from ordinal 4, including `s1` and
source fields. That difference is not a contract selection because the arms
run separately through an animating title scene. Output/state parity remains
unevaluable until port rows are joined to retail by phase, PC, and ordinal.

Session 3453 performed that controlled join. At title origin `0x00790400`,
the first joined row diverges in `s0` at all four target PCs for both port
arms; no exact six-field tuple matches in the common prefixes. The port
four-PC control and independent retail whole-RDRAM control both fired, so this
selects a real first output/state-context divergence and rules out an absent
port hook. It does not identify the writer of `s0`; the next probe must trace
the producer feeding the target calls.

Session 3454's corrected thread-local callsite join shows that port `rs_free`
preserves caller `s0` at `0x80001C98` in all 514 captured rows (480 from
caller `0x80005268`). The first divergence is already in the producer/input
register context; wrapper/ABI clobber is ruled out at this boundary.

Session 3455's independent retail preflight passed 18,497 whole-RDRAM control
callbacks and reached title 1024, with 781 executions of the
`0x80005268 -> 0x80001C98` edge and 2,570 executions each at
`0x80001CB8` and `0x80001CC8`. The batched port run reached title 1024, fired
the four-PC schema control, and emitted 1,024 callsite rows plus 514/514/510
rows at the three target PCs. Caller-side `s0` was varied before the target
calls in the port rows, matching the independently observed retail edge. This
reinforces the upstream producer/input selection, but the callsite witness
still does not attribute the writer of `s0`. Evidence: [M5-S3455-PRODUCER-JOIN.md](M5-S3455-PRODUCER-JOIN.md).

Session 3456's independent Rice-oracle run passed the whole-RDRAM control,
reached title, and observed 3,233 executions of `0x80001C98` from
`0x800645AC`. A new port load witness at `0x800645A8` passed its existing
four-PC schema control and emitted 1,024 rows. The first ordered prefix
diverges at the producer/input value: retail has `s0=0x801B4F00` where the
port loads `0x801B5E70`, while both use source pointer `0x801E8710`; the port
target preserves that value. This selects the upstream producer/input
boundary and rules out wrapper/ABI clobber at this scope. It does not name the
writer of `*(0x801E8710)`. Evidence: [M5-S3456-PRODUCER-INPUT.md](M5-S3456-PRODUCER-INPUT.md).

Session 3457's retail source-slot watch passed the whole-RDRAM control with
11,483 callbacks, recorded 1,483 writes to physical `0x001E8710`, and showed
title-phase writers at `0x800644B0`, `0x80064524`, `0x800078EC`,
`0x80018F5C`, `0x80018F80`, `0x80028F90`, `0x800C871C`, and `0x80006FF4`.
The matching port run passed its four-PC schema control and emitted 1,024
source-writer rows, but only at `0x800644B0` and `0x80064524`. This selects a
retail-side writer/route difference at the observed title boundary and rules
out a port-only writer. The generated parity hook passed zero as its value
argument, so writer-value legitimacy remains unevaluable. Evidence:
[M5-S3457-SOURCE-WRITER.md](M5-S3457-SOURCE-WRITER.md).

Session 3458's retail post-store arm passed the whole-RDRAM control (11,198
callbacks), reached title origin `0x00790400`, and measured the actual source
word: `0x800644B0` stored zero in 807 samples, `0x80064524` stored nonzero in
269, and retail-only writers such as `0x800078EC` and `0x80018F80` also had
nonzero samples. The matching port arm was rebuilt, but the first attempt used
an invalid route and the corrected LLE/spin-yield attempt crashed at startup
(`spTaskSchedulerThread`, guest PC `0x8000834C`) before title, with zero source
rows. Retail value evidence is therefore single-source and the cross-runtime
writer/value join remains unevaluable. Evidence:
[M5-S3458-SOURCE-VALUE.md](M5-S3458-SOURCE-VALUE.md).

Session 3459 rebuilt the prescribed LLE/spin-yield port arm and reached title
origin `0x00790400`, producing 20 title captures. Its parity control fired in
the earlier width-640 phase, but the title-scoped control and source-writer
table both emitted zero rows. The run later changed to width 640 and crashed
in `musyxSynthFrame+4268` (last guest PC `0x80001B08`). Title reachability is
qualified for this arm, but the title writer witness is not; the source-value
join remains unevaluable and no audio behavior is implicated. Evidence:
[M5-S3459-SOURCE-VALUE-PORT.md](M5-S3459-SOURCE-VALUE-PORT.md).

## Next steps

1. Repair or qualify the title-scoped source-writer witness. The current arm
   reaches origin `0x00790400`, but its control remains width-640-only and its
   title source table is empty. First establish why the generated store hook
   does not observe title calls, then run one same-build capture whose control
   and source rows are both title-scoped. Do not alter waits, slots, dispatch,
   clear behavior, or PCM writeback.
2. Keep the controlled phase/PC/ordinal join as the baseline; do not compare
   sequential silent/image rows as an animated A/B.
3. Use the producer join to identify the first output/state contract divergence
   after the qualified title pointer boundary. Matching fields close the
   boundary; the first divergent field selects the missing contract edge.
4. Add one phase-scoped port witness table matching the oracle's
   `(pc,s0,s1,source_word,branch_selector,source_byte,branch_state)` fields at
   all four target PCs, then join it by phase and ordinal to the existing
   consumer/output rows. Matching fields close the boundary; the first
   divergent field selects the missing contract edge; absent ordered rows are
   unevaluable.
5. Locate the first output/state contract divergence after the now-qualified
   title pointer boundary. Join the retail `0x80001CB8`/`0x80001CC8` rows to
   output value and state-word fields, then compare the existing port rows;
   a matching pointer but divergent output selects the output contract, while
   a missing ordered join remains unevaluable.
6. Keep M5 Step 3 gated until that output comparison names one missing
   image-task/output contract edge. The M5 design inventory is complete in
   [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md). Configured-host PatchesLib validation
   is an external dependency; this Unix checkout lacks its MIPS toolchain and
   generated patch input.
7. After M5 closes or a new discriminator is found, resume only systematic M3
   idiom-class audits. Keep external retail-entry, hangar `0x8000`
   Y/accumulator arithmetic, and SP-yield/MORT publication threads parked.
   Generated-symbol renaming is last priority and remains closed at its
   measured scope.

Closed or parked boundaries include the task-start guest-pointer guard, the
`0x800919D4 -> 0x800919EC -> 0x80007910` callback chain, the B1C source census,
the generated free-list-walk class, direct `setDisplayMode` count boundary,
direct `initN64RspMixer` boundary, and corrected MORT descriptor edge `+0x190`
to `dmaVoiceSampleAndSignal`.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control, a
phase-scoped budget, and two independent evidence lines before promotion.
Phase-gate animated comparisons on VI transitions. Batch all A/B arms in one
build and run. A null without a positive control is worthless.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py -> CMake`.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
run `./submodule-patches/export.sh` and commit refreshed patches in the same
iteration. Never run submodule update, checkout, clean, or hard reset commands.
Kill runs with SIGKILL and run from `build/`. A mitigation-shaped change needs
an `ORIGIN:` line naming the writer and stating whether its value is legitimate.

CMake's `RECOMP_FUNCS_DIR` is `../N64Recomp/RecompiledFuncs`. The strong
SP-task override and completion-aware `osSpTaskYielded` contract are current
defaults; request-only behavior is superseded. Static boundary-only symbol
classifications are not renames without defensible semantic evidence.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain from sessions 3288–3302 describes
only the old diagnostic arm; completion-aware default behavior in s3304
returns the viewer. The old interpretation of the 1,578-entry cinematic pool
as an audio-slot pool was superseded by the MusyX voice-table measurement.

The s3402 claim that `0x8002BEEC` was the retail JAL dispatch to `0x800078EC`
is not a current oracle target. Later same-route adjacent-PC captures found
zero at both addresses while `0x800078EC` was live; the earlier attribution is
route-dependent and unreconciled. Do not treat it as a writer without a new
independent discriminator.

## Evidence index

Latest state-pointer/output evidence:

- [M5-S3445-STATE-POINTER-ENTRY.md](M5-S3445-STATE-POINTER-ENTRY.md)
- [M5-S3448-STATE-POINTER-PHASE.md](M5-S3448-STATE-POINTER-PHASE.md)
- [M5-S3447-STATE-POINTER-CHECKPOINT.md](M5-S3447-STATE-POINTER-CHECKPOINT.md)
- [M5-S3444-STATE-POINTER-PRODUCER.md](M5-S3444-STATE-POINTER-PRODUCER.md)
- [M5-S3443-FREQUENCY-OUTPUT-JOIN.md](M5-S3443-FREQUENCY-OUTPUT-JOIN.md)
- [M5-S3442-FREQUENCY-OUTPUT-USE.md](M5-S3442-FREQUENCY-OUTPUT-USE.md)
- [M5-S3441-FREQUENCY-CONSUMER.md](M5-S3441-FREQUENCY-CONSUMER.md)
- [M5-S3440-SEND-RECEIVE-JOIN.md](M5-S3440-SEND-RECEIVE-JOIN.md)
- [M5-S3438-FREQUENCY-CALLERS.md](M5-S3438-FREQUENCY-CALLERS.md)
- [M5-S3437-FREQUENCY-ENTRY.md](M5-S3437-FREQUENCY-ENTRY.md)
- [M5-S3410-FIELD348-INPUT.md](M5-S3410-FIELD348-INPUT.md)
- [M5-S3400-FIELD348-PRODUCER.md](M5-S3400-FIELD348-PRODUCER.md)
- [M5-S3398-STAGE3-DESTINATION.md](M5-S3398-STAGE3-DESTINATION.md)
- [M5-S3376-ZERO-PCM-SOURCE.md](M5-S3376-ZERO-PCM-SOURCE.md)

Earlier detail is preserved in the ledger and the M5 archive sections of
[PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md). Use bounded `grep`/`sed` windows
for `PORTING-STATE.md`; never read it wholesale. The soak queue is consumed by
automation; fold only new tail lines into the next audit.
