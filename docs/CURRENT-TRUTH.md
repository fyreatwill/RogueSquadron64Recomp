# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4062 (2026-10-04).

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
empty-queue tail state, expansion ownership, the active sentinel's
predecessor, and full free-chain/active-queue disjointness. The ordinary Debug
target builds. Runtime qualification is
blocked because this host has neither `mips64-elf-gcc` nor `mips64-elf-ld`, so
CMake still omits `PatchesLib` after the cross-platform discovery repair. The
installed Clang also has no MIPS backend, and local filesystem checks found no
toolchain or rebuildable source tree. The sentinel guard's ORIGIN is
`heap_tail_loc` and the active-queue append stores; a predecessor on the
sentinel path is not legitimate ownership state.

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
- Session 4047 qualified the sentinel guard only at source/host-build scope;
  session 4049 repaired cross-platform discovery but still found no MIPS
  toolchain. `PatchesLib` was absent and no runtime behavior was inferred.
- Session 4050 reconfigured on macOS, confirmed no `mips64-elf-gcc` or
  `mips64-elf-ld` on PATH, observed the expected CMake skip and missing
  `PatchesLib` target, and rebuilt the ordinary target successfully. Runtime
  qualification remains unevaluable on this host.
- Session 4051 repeated the M3 discriminator: both MIPS tools remain absent,
  `PatchesLib` remains absent, and the ordinary target builds. This is a
  prerequisite block, not runtime evidence; do not repeat until a toolchain or
  another qualified host is available.
- Session 4052 tested the block's alternate routes. `clang --target=mips`
  failed with no compatible target; its assembler also rejected MIPS. No
  MIPS GCC/LD, MIPS Linux cross tools, or generated patch artifacts were found
  locally. The M3 dependency remains external; work is re-scoped to the M5
  route discriminator until a qualified MIPS host is supplied.
- Session 4053 ran a new reversed launch order with 7-second inter-arm gaps.
  The retail oracle positive control fired and reached title 1024 and hangar
  512. All three port arms failed before title 1024: declared-real and
  legacy-real crashed in the scheduler path, while declared-silent reached
  only a 640-width phase. This selects H3 for this schedule; its source-writer
  nulls are unevaluable and do not advance the writer census.
- Session 4054 ran one same-build sequential arm-isolation matrix while the
  retail oracle remained active. Retail passed the whole-RDRAM control and
  reached title 1024 and hangar 512. Isolated declared-real reached both
  targets and reproduced the zero-payload image signature
  (`FNV=0x762B22A5`, nonzero=0); isolated declared-silent and legacy-real both
  crashed in `spTaskSchedulerThread` before target phases. This qualifies the
  declared-real route for the `0x800052C4` census, while the other two arms
  remain unevaluable.
- Session 4055 ran the qualified declared-real route with the retail oracle and
  all three candidate callsites (`0x800052C4/8/CC`) armed together. Retail
  passed the whole-RDRAM control and reached title 1024 and hangar 512, but
  every candidate reported `seen=0`, `n=0`, and no phase-gated store row.
  Declared-real reached both target phases and again produced
  `FNV=0x762B22A5`, nonzero=0. The candidate class is therefore H3/
  unevaluable as a source-writer class, not H1 or H2.
- Session 4056 ran a new same-build concurrent process-topology matrix with
  the retail oracle and declared-real, declared-silent, and legacy-real arms
  active together. Retail passed the whole-RDRAM control and reached title 1024
  and hangar 512. Both declared arms reached both target phases; legacy-real
  again crashed in `spTaskSchedulerThread` before them. This selects H1 for
  the startup-dependency hypothesis: process topology changes which arms
  qualify. It does not qualify a source-writer null for legacy-real.
- Session 4057 ran the next retail-grounded predecessor batch with the
  whole-RDRAM/title/hangar controls and declared-real port arm. Retail passed
  all controls and both target phases; the port reached both target phases and
  retained `FNV=0x762B22A5`, nonzero=0. `0x800C825C` had zero target-phase
  rows, selecting H3/unevaluable for that predecessor. The paired
  `0x800078E0/EC` target summaries were also zero, while `0x800078EC`
  independently had 816 scalar source-span stores, all zero with mismatch=0.
  This does not identify the upstream zero producer.
- Session 4058 audited the free/active ownership idiom and found the existing
  `free_chain_disjoint_from_active_tail` check did not reject an alias at an
  earlier active-queue node. Added a bounded whole-active-chain comparison in
  `patches/heap_guards.c`, with ORIGIN comments naming `heap_free_head` and
  `heap_other_listhead` as the separate guest owners. The ordinary Debug target
  built successfully; MIPS runtime qualification remains unavailable.
- Session 4059 rebuilt the ordinary Debug target after the overlap-guard commit,
  passed `git diff --check`, and confirmed that `PatchesLib` has no generated
  build target on this host. This is a host-build qualification only; it adds
  no runtime evidence and does not reopen the M3 toolchain prerequisite.
- Session 4060 ran the prescribed same-build retail-oracle/declared-real capture.
  Retail passed the whole-RDRAM positive control and both title/hangar phase
  controls; the port also reached both phases with `FNV=0x762B22A5` and
  nonzero=0. Exact hangar-phase post-target attribution produced zero rows for
  `0x800C825C`, `0x800078E0`, and `0x800078EC`. The oracle did record 816
  scalar-zero stores from `0x800078EC`, but those requested-PC rows were tagged
  to transition state `origin=0x006AB800`, width 1024, not the exact hangar
  bucket; mismatch=0. This rules out treating `0x800078EC` as the exact
  hangar-phase writer, but does not identify a replacement producer.
- Session 4061 repeated the immediate-writer capture with explicit transition
  and hangar buckets in one run. Retail passed the whole-RDRAM positive control
  and reached title `0x00790400/1024` and hangar `0x006AB400/512`; the port
  reached both phases with no crash/abort and retained `FNV=0x762B22A5`,
  nonzero=0. Retail recorded 816 mismatch-free zero scalar stores from
  `0x800078EC`, but its detailed rows were in the `0x006AB800` transition
  (live width 512) or a width-1024 `0x006AB400` phase; the exact
  `0x006AB400:512` bucket had no candidate rows. H2 is selected: this
  zero-fill is not the exact hangar writer, so a different producer or an
  absent producer remains open.
- Session 4062 qualified the next source-span class with the same retail and
  port controls. `0x80007670` executed 1,563 times while the retail exact-
  hangar source-range watch was active, but its exact `0x006AB400:512` target
  rows were zero; no mismatch-free scalar sample attributed a target write to
  this PC. H2 is selected for this class, so the ranked census advances to its
  adjacent `0x800076A0` class.

Detailed counts and every failed or superseded run remain in the append-only
ledger. Use bounded `grep`/`sed` windows for that file; never read it whole.

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **Title-music AI parity (operator redirect 2026-10-04).** The hangar
   source-writer census is CLOSED, not paused: retail's own hangar source span
   is zero (s3820, 408 bytes, `FNV=0x762B22A5`), so the port's zero span is
   parity, not a missing writer. Do not arm further candidate PCs against it.
   Instead compare retail vs declared-real port AI output (`osAiSetNextBuffer`
   address/length plus PCM FNV/nonzero count) per VI phase, starting at title
   VI 1024 where music is audible, and walk back one hop at a time from the
   first phase where retail PCM is nonzero. Slug `m5-title-music-ai-parity`;
   full discriminator in `scratch/agent/NEXT.md`.
2. **Qualify M3 patch integration (external dependency).** On a host with the MIPS toolchain, use
   the repaired discovery path to build `PatchesLib` and runtime-qualify the
   active-sentinel predecessor guard. The source and ordinary host target
   already pass; do not infer runtime behavior from that build alone. This
   macOS host is blocked on installing/providing `mips64-elf-gcc` and
   `mips64-elf-ld` or using another host with them.
3. **Requalify the M5 route.** Legacy-real remains pre-target under both
   sequential isolation and concurrent topology; revisit only with a new
   startup dependency that can explain the legacy arm.
4. **M5 de-stubbing.** After the current route/source discriminator is closed,
   follow the incremental validation sequence in `M5-AUDIO-PLAN.md`; do not
   treat the silent control as real-audio evidence.
5. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
   writer, or audio work. Keep slug `generated-symbol-renaming-sweep` if it
   resumes; mapping-only edits do not reset the engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 producer absent | Hangar span closed as retail parity (s3820). Title-phase AI output open: Next steps 1. |
| M5 clear is expected | Selected for clear witness `0x8008F2CC` writing object `0x801797B0`, length `0x298`. |
| M5 consumer disconnected | Selected at the measured task/output scope; upstream zero payload remains open. |
| M5 route failure | Active H1: process topology changes which audio arms reach target phases; legacy-real remains pre-target. |
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
