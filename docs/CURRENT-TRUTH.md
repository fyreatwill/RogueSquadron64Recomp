# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background is in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md); the audio
inventory and de-stubbing contract are in [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md).
Updated for session 4168 (2026-10-07).

## Current state

The validated native route boots through attribution, N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and
hangar VI 512 (`0x006AB400`) on the qualified real-audio/LLE/ungated/solo/
spin-yield route. Hangar geometry and color artifacts remain. The real audio
path is not production-complete; `ROGUESQ_AUDIO_UCODE=0` is the silent control.

The active M5 boundary is the source payload and its producer context, not
rendering. Qualified retail and port hangar source spans are zero on the port
(`FNV=0x762B22A5`) but nonzero in retail. The port's exact target-span guest
scalar/non-scalar observations show the legitimate later `rs_memset` clear at
`0x800078E0/0x800078EC`; the earlier nonzero state is written by the host ROM
asset path (`pi_rom_to_rdram`) before the clear. No mitigation or guest
behavior change is authorized from this boundary.

Session 4164 independently requalified M5 Step 3. Declared-size staging
(`0x800`, the OSTask-declared span) and legacy staging (`0xF80`) both reached
title and hangar with matching task/SP/route, zero-payload, and downstream
signatures. The declared arm is sufficient at this boundary; legacy staging
adds DMEM writes without a measured downstream benefit. ORIGIN: `rsp.cpp`
staging DMA is the writer and the OSTask declaration is legitimate.

Session 4167 completed a clean canonical same-build real-image/silent port
pair after two route-invalid attempts caused by missing route flags and stale
game child processes. Both clean arms passed the positive controls, reached
title VI 1024 and hangar VI 512, and had live gate/task/SP/PCM instrumentation.
The gate was `0x01` in both arms; hangar PCM source and consumer rows were
present but zero-valued in both (`384` samples, `FNV=0xF59C39C5`, `nz=0`).
The real image completed its DMEM/DMA path (`break_pc=0x1328`, `dma_count=3`)
while the silent arm had `dma_count=0`. No downstream real-versus-silent
divergence was measured, so H-upstream-zero-payload remains selected and no
gate change is authorized.

Session 4168 reproduced the same boundary with a self-cleaning concurrent pair.
Both arms fired the positive control and reached title VI 1024 and hangar VI
512. In hangar, real-image and silent PCM source/consumer rows were both zero
(`384` samples, `FNV=0xF59C39C5`, `nz=0`); the real arm logged 3,846 audio-stage
rows and 3,890 image-queue rows, while the silent arm logged no image-queue
rows. The silent arm later bus-crashed after the target phases, so that crash
does not invalidate the phase result. This independently requalifies
H-upstream-zero-payload and rules out route invalidity for this clean pair; no
gate or consumer change is authorized.

## Next steps

Work only the first applicable item. This backlog is one monotonic sequence.

1. **M5 audio de-stubbing:** advance Step 4 in `docs/M5-AUDIO-PLAN.md` by
   qualifying the port-side `0x800A0F50` writer/value rows against the retail
   writer set, with slot/status and PCM joins kept in the same phase-gated run.
   Retail ground truth is now present: the whole-RDRAM control fired, and the
   gate at `0x800A0F50` has writers `0x8008EA34`, `0x8008EB40`, `0x8008ED48`,
   `0x8008EB7C`, and `0x8008EC88`; the last is the nonzero enable writer.
   Qualify matching port writer/value and downstream slot/PCM joins before
   changing one writer or consumer. Keep the real-audio route; do not use the
   silent control as a production fix.
2. **M3 pre-publication guard runtime qualification** remains blocked on a host
   with `mips64-elf-gcc`/`mips64-elf-ld` and a configured `PatchesLib` target;
   do not spend another host-only iteration.
3. **Generated-symbol renaming sweep.** Parked while M5 has applicable route,
   writer, or audio work. Keep slug `generated-symbol-renaming-sweep` if it
   resumes; mapping-only edits do not reset the engineering-change gate.

## Live hypotheses

| Hypothesis | Status |
|---|---|
| M5 producer absent | Hangar source-span census is closed as retail parity at the measured boundary. The missing port nonzero payload is upstream/earlier provenance, not an established missing guest store. |
| M5 pre-clear provenance | H-host-ROM-writer selected at s4163: `pi_rom_to_rdram` writes legitimate nonzero target bytes before the later guest clear; generated guest scalar and non-scalar target rows are zero-valued at the clear. |
| M5 source setup state | H-shared-source-state selected at s4150: independent retail and port setup tuples match for the title clear and dominant hangar source-construction calls. The setup boundary is not the measured explanation for the later zero producer payload. |
| M5 producer caller state | H-caller-state-split selected at s4152, with s4153 selecting H-entry-body-shared: retail preserves producer object/state into `0x800078EC`, while port context differs earlier. Generated port `ra=0` is an instrument limitation, not guest evidence. |
| M5 Step 3 declared audio staging | H-step3-equivalent independently requalified at s4164: declared `0x800` and legacy `0xF80` arms match at the measured downstream contract. Semantic irrelevance outside that contract is unproven. |
| M5 Step 4 retail gate ground truth | H-retail-gate-writers selected at s4166: the independent oracle whole-RDRAM control fired in both target phases; `0x800A0F50` was written 14 times by five PCs, with `0x8008EC88` producing the observed nonzero value. The watched `0x80094648`, `0x80090AAC`, and `0x80090BA4` words had zero writes in this retail route. This selects the port parity measurement, not a gate change. |
| M5 Step 4 port parity | H-upstream-zero-payload selected at s4167: the clean canonical pair reached title/hangar and live gate/task/PCM controls. Both arms had gate `0x01` and zero-valued hangar PCM source/consumer rows; only the real image's DMEM/DMA activity differed. The initial route-invalid attempts are excluded because they stopped at VI 640 or crashed with stale game children present. |
| M5 task contract | H-contract-gap selected at s4128: image task handoff/completion is live, but image and silent controls both have zero measured PCM payload at the tested scope. |
| M5 consumer disconnected | Selected at the measured task/output scope; upstream zero payload remains open. |
| M5 title host sink | H-play selected at s4065: device 2 opens, host queue calls are positive, and drain depth advances. Native device callback/output behavior remains open. |
| M5 image zero boundary | H-guest-zero-producer selected at s4112: qualified port arms recorded zero-valued `0x800078EC` stores into the source span before zero image reads; host writeback is downstream zero data. |
| M5 gate value | Selected at measured scope: retail gate writes were zero-byte pre-target activity. |
| M5 descriptor selector writer | H-port-writer-live selected at s4100: port witness rows fire and `0x80090AAC` has retail-matching selector values; `0x80090BA4` has no port rows. |
| M5 key-on early returns | H-returns-dead/H-guard-valid selected at s4101: valid divisors, normal tails, and slot transitions; no guard relaxation authorized. |
| M5 drain-tick policy | H-Drain-Changes-Ordering remains qualified at s4103/s4114. Tick-required behavior is not established because the reverse-order arm was route-invalid. |
| M5 status-03 reaping | H-status03-after-return selected by qualified port ordering at s4136: service entry, read, `03 -> 00` store, and exit are ordered after the observed shutdown return. No force-clear or wait change is authorized. |
| M5 A10/A9/A8 guards | A10 and A9 guards are not suppressing measured valid work; A8 trap PCs are live but do not fire on qualified retail/port routes. No relaxation is authorized. |
| M5 A11 wait terminal transition | H-target-phase-absent-both selected at s4145: target-phase wait/post-wait terminal rows were absent in both qualified arms. This is not a safety proof. |
| M3 sentinel ownership | H1 selected at source/host-build scope; runtime remains unqualified because this macOS graph lacks the MIPS toolchain and `PatchesLib` target. |
| Generated symbols | Parked until higher-priority M5/M3 work is inapplicable. |

## Durable evidence boundary

Retail reaches title/hangar and can attribute relevant writer PCs. The paired
port can reach image-DMA joins when its arm completes. The port task
`0x80171E70`, size 1, joins the exact input DMA at matching generations, but
payloads are zero; separate writeback joins are real. The task and output edges
therefore execute, but zero payload does not identify the missing upstream
writer.

The qualified consumer comparison used same-build declared/real,
declared/silent, and legacy/real arms. It found matching phase-5 zero-payload
signatures. A route failure invalidates a null; it never proves absence.

Session 4166 supplied the independent retail line for Step 4. The oracle's
whole-RDRAM watch reached its 10,000-callback positive-control threshold and
the driven route reached title `1024 @ 0x00790400` and hangar `512 @
0x006AB400`. Its narrow gate watch recorded 14 writes: the writer set was
`0x8008EA34`, `0x8008EB40`, `0x8008ED48`, `0x8008EB7C`, and `0x8008EC88`;
post-store samples were zero for the `ED48`/`EB7C` rows and nonzero for the
`EC88` row. The three candidate consumer/selector watches had no writes.
This is independent retail evidence only; port parity and downstream joins
remain open.

The title playback/drain capture is independently controlled by retail
whole-RDRAM and title/hangar AI-output witnesses. On the paired port,
declared-real reaches both phase gates and host enqueue/raw drain rows are
positive in both phases. This closes immediate queue-drain starvation at the
measured SDL queue boundary, not device delivery to audible output.

## Superseded conclusions

The overlay/menu-only explanation, intrinsic VI-640 flakiness, missing-input
and wait-return explanations, global-zero image-DMA theory, route-wide PCM-gap
theory, and force-zero default policy are superseded at their measured scopes.
They were plausible before qualified routes, same-build controls, or
independent retail attribution existed.

The early staging-based route explanation is superseded by same-build route
tables: launch order and timing affect qualification, but neither staging size
nor real-audio mode alone explains the measured boundary. The s3579–s3584
stored-value inference is unsupported because a retail byte store was compared
with an aligned word containing neighboring bytes.

The s4075 missing-store inference is superseded by the source audit: the
generated source contained the store and the fixup had silently omitted its
witness. The s4088 detail-hook conclusion is superseded by s4089, where a
corrected callsite fired the positive control. The s4149 setup/state
route-invalid conclusion is superseded by s4150's route-stable retail match.

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
Detailed counts and session-specific notes remain in `PORTING-STATE.md`.
