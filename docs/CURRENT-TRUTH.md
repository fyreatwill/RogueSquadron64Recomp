# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4048 (2026-10-04).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the qualified real-audio/LLE/spin-yield route.
Hangar geometry and color artifacts remain. `ROGUESQ_AUDIO_UCODE=0` is the
silent `Broke` control; real audio is not production-complete.

The active M5 boundary is source payload, not rendering. Qualified retail and
port hangar-phase source spans are zero (`FNV=0x762B22A5`); retail's
phase-gated hangar snapshot is 408 bytes with nonzero=0. The port descriptor
`0x1798B0 -> DMEM 0xCB0` is written by legitimate zero-valued
`0x800078EC` fill activity. No nonzero hangar producer is established.

The task-contract consumer boundary is closed at the measured scope: declared
and legacy real-audio arms reached both target phases with matching zero
payload consumer signatures, while the silent arm remained a valid control.
The old declared-size/legacy crash split is schedule-sensitive and is not an
audio-staging explanation. The legitimate legacy staging writer is still
`0xF80`; declared-size staging is `0x800`.

M3 has landed regeneration-safe ownership guards in `patches/heap_guards.c`
for free-list span/reciprocal links, active-queue reachability and aliasing,
empty-queue tail state, expansion ownership, and the active sentinel's
predecessor. The ordinary Debug target builds. Runtime qualification is
blocked because the configured build graph has no `PatchesLib` target; the
last attempt failed before compilation with `No rule to make target
'PatchesLib'`. The sentinel guard's ORIGIN is `heap_tail_loc` and the
active-queue append stores; a predecessor on the sentinel path is not
legitimate ownership state.

## Recent qualified evidence

- Retail oracle whole-RDRAM, title-VI, and hangar-VI positive controls are
  required and have passed on qualified captures. A candidate null is valid
  only when the paired port also reaches both target phases.
- Candidate writer classes through `0x8000529C` have been qualified in
  adjacent batches where the port completed; candidate PCs had no target or
  post-target evidence. The `0x800052C4` class is not qualified: recent route
  permutations (sessions 4043–4046) left no arm reaching both target phases.
- Route permutations through sessions 4030–4032 and 4034, 4039, 4042–4046
  changed which port arm failed or qualified. This confirms a schedule/route
  discriminator is needed; it does not identify the missing source writer.
- Session 4047 qualified the sentinel guard only at source/host-build scope:
  ordinary Debug succeeded, `PatchesLib` was absent, and no runtime behavior
  was inferred.

Detailed counts and every failed or superseded run remain in the append-only
ledger. Use bounded `grep`/`sed` windows for that file; never read it whole.

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **Restore M3 patch integration.** On a host with the MIPS toolchain,
   restore the `PatchesLib` target and runtime-qualify the active-sentinel
   predecessor guard. The source and ordinary host target already pass; do
   not infer runtime behavior from that build alone.
2. **Requalify the M5 route.** Run one genuinely new same-build launch-order
   or gap table. Retail controls and all three port-arm target-phase controls
   must qualify; classify any pre-target failure as H3, never as writer
   absence. Do not repeat the already-tested one-, two-, three-, or
   four-second permutations without a new discriminator.
3. **Resume the retail-grounded source-writer census.** Only after step 2
   qualifies, measure the `0x800052C4` class and then choose the next bounded
   class. Keep the positive controls and phase-scoped budgets in the same run.
4. **M5 de-stubbing.** After the current route/source discriminator is closed,
   follow the incremental validation sequence in `M5-AUDIO-PLAN.md`; do not
   treat the silent control as real-audio evidence.
5. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
   writer, or audio work. Keep slug `generated-symbol-renaming-sweep` if it
   resumes; mapping-only edits do not reset the engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 producer absent | Selected only for measured pre-input/source classes; not global. |
| M5 clear is expected | Selected for clear witness `0x8008F2CC` writing object `0x801797B0`, length `0x298`. |
| M5 consumer disconnected | Selected at the measured task/output scope; upstream zero payload remains open. |
| M5 route failure | Active H3: recent port arms fail before target phases under some schedules. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime unqualified. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| Generated symbol sweep | Parked until higher-priority M5/M3 work is inapplicable. |

## Durable evidence boundary

Retail reaches title/hangar and can attribute relevant writer PCs. The paired
port can reach image-DMA joins when its arm completes. The port task
`0x80171E70`, size 1, joins the exact input DMA at matching generations, but
payloads are zero; separate writeback joins are real. The s3891 image arm
proves the RSP task and two output-DMA edges execute; zero payload does not
identify the missing upstream writer.

The qualified consumer comparison used same-build declared/real,
declared/silent, and legacy/real arms. It found no declared-only post-`0x800`
marker and matching phase-5 zero-payload signatures. The candidate census is
qualified only through the latest completed class; route failure invalidates a
null, rather than proving absence.

## Superseded conclusions

The overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input
and wait-return explanations, global-zero image-DMA theory, route-wide PCM-gap
theory, and force-zero default policy are superseded at their measured
scopes. They were plausible before qualified routes, same-build controls, or
independent retail attribution existed.

The early s4009/s4010 staging-based route explanation is superseded by later
same-build route tables: launch order and timing change the qualifying arm,
but neither staging size nor real-audio mode is sufficient as a causal
explanation. The s3579–s3584 stored-value inference is unsupported because a
retail byte store was compared with an aligned word containing neighboring
bytes. Request-only SP-yield conclusions are limited to the old diagnostic
arm.

## Durable operating rules

Use [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard F3DEX
assumptions. The qualified graphics path is LLE-only. Interpreter limits,
null-GBI guards, and similar defenses are safety mechanisms, not explanations.
MusyX/MORT audio remains partially stubbed; MusyX data must not be sent to
stock `aspMain`.

Every instrument needs independent ground truth, a same-run positive control,
a phase-scoped budget, and two evidence lines before its result becomes truth.
Phase-gate animated comparisons on VI transitions and batch A/B arms in one
build/run. A counter proving a branch ran is not a positive control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Evidence index

See [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md),
[M5-S3801-IMAGE-STAGE-BOUNDARY.md](M5-S3801-IMAGE-STAGE-BOUNDARY.md),
[M5-S3802-SOURCE-WRITER-CENSUS.md](M5-S3802-SOURCE-WRITER-CENSUS.md), and
[M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md](M5-S3824-FAMILY-ROUTE-OBJECT-JOIN.md).
Durable background migrated to `PROJECT-OVERVIEW.md`; detailed counts and
session-specific notes remain in `PORTING-STATE.md`.
