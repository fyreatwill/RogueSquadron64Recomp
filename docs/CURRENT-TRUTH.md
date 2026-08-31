# Rogue Squadron 64 Recomp — current truth

Operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable background
and archived session detail are in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
This file is the compact active-state record; full run logs live under
`scratch/agent/` and the session evidence documents.

Current maintenance marker: Session 3447 (2026-08-31). This record was
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
- At `rs_free` entry both port arms still have retail-shaped `s1=0x80194B20`,
  pointed word `0x80194B40`, and `a0=0x801BEEB0`; the first divergence is
  therefore after that entry and before the consumer witness.
- The generated host wrapper reports `ra=0`; the exact clobber is unresolved.

The s3447 ordered checkpoint is positive only for hangar-512 calls: both arms
retain `s1=0x80194B20`, pointed word `0x80194B40`, and state `0x801BEEB0`
after receive and before the consumer witness. Existing consumer rows are
title-1024 calls with `0x801BBD..` state pointers, so this run has no ordered
join across the suspected boundary. `H-PortStatePointerClobber` remains open
at title 1024; the 512 parity result must not be generalized.

M5 audio source work remains unresolved upstream: qualified port image-stage
rows carry zero source/output PCM, while retail independently writes nonzero
PCM spans. Do not change waits, slots, status handling, consumer dispatch,
clear behavior, or PCM writeback while locating the state-pointer edge.

## Next steps

1. Repeat the state-pointer checkpoint with the title-1024 gate: ask the
   retail oracle first for `0x80001C98`/`0x80001CB8`/`0x80001CC8` rows in
   origins `0x00790400`/`0x00790800`, then gate port witnesses on those origins
   as well as the existing hangar controls. Join post-receive, pre-consumer,
   and consumer rows by phase and ordinal in one silent/image build.
   Title-1024 parity closes the clobber at this scope; a first port-only
   change selects it; missing joins remain unevaluable.
2. Keep M5 Step 3 gated until a like-for-like target row names one missing
   image-task/output contract edge. The M5 design inventory is complete in
   [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md). Configured-host PatchesLib validation
   is an external dependency; this Unix checkout lacks its MIPS toolchain and
   generated patch input.
3. After M5 closes or a new discriminator is found, resume only systematic M3
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
