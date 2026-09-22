# Rogue Squadron 64 Recomp — current truth

Compact operational state for [PORTING-STATE.md](../PORTING-STATE.md). Durable
background and closed M3 audits are in [PROJECT-OVERVIEW.md](PROJECT-OVERVIEW.md).
Updated for session 3690 (2026-09-21).

## Current state

The native port boots through attribution, N64 logo, intro cinematic, star
flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar VI 512
(`0x006AB400`) on the validated real-audio/LLE/spin-yield/autopilot route.
Hangar geometry and color artifacts remain. The image task is the qualified
real-audio arm; `ROGUESQ_AUDIO_UCODE=0` / `Broke` is the silent control. Audio
is not production-complete.

The active M5 Step 4 boundary is the image-task source range
`0x1797B0..0x179930`. The port's target handoff performs a zero-fill from
`0x800078EC` (`rs_memset`, commonly `dst=0x801797B0, fill=0, len=0x298`)
followed by zero source-DMA payloads. Retail reaches the same target phase,
writes the watched source span, and repeatedly calls `0x800078E0` with
`a2=0x80` and changing structure pointers from `0x800C825C`; its source
writer is `0x800078EC` before the first target VI. The exact input-DMA ordering
and ownership is now classified: the qualified input-DMA capture joined all
244 absent-generation hangar source rows to an earlier/equal input task
identity, with no later or missing/contradictory joins. The remaining question
is whether that stale input task already carries the zero payload.

Session 3690 added the input-DMA event before output DMAs could overwrite the
thread-local identity. The qualified rerun produced 512 hangar source rows,
2,724 stage rows, and 8,136 input-DMA events; 244/244 absent-generation rows
joined an earlier/equal input task identity. This selects
`H-StaleInputAcrossReuse`. Session 3688's `H-DmaKeyStillUnavailable` result
was limited to the output-DMA boundary.

The current source/stage picture is: title source rows are same-generation;
the hangar minority is generation-absent, uses `0x80171E70`, and later stages
reuse that pointer under a later route generation. Session 3686 classified
244/244 measured absent rows as later-route reuse, with zero same-route,
contradictory, or missing classifications. Sessions 3680–3683 establish that
route publication can lag source reads, while stage callbacks observe the
current publication. Do not infer ownership from pointer identity or host log
order alone.

Do not force the cinematic flag at `0x800B0934`, bypass the state machine, or
rewrite task, audio, PCM, selector, or output state. The default route's null
stage-advancer input is a known route/configuration issue; the validated
real-audio route is the comparison arm.

## Next steps

The backlog is one monotonic sequence. Work only the first applicable item.

1. **M5 Step 4 — identify the stale-input payload boundary.** Add one
   phase-scoped input-DMA record containing the source payload hash/nonzero
   count and task-data pointer, then join it to the source witness and later
   stage row. Competing hypotheses are `H-StaleInputPayload` (the earlier
   task's input is already zero), `H-SourceOverwrittenAfterInput` (RDRAM is
   overwritten after input-DMA selection), and `H-StaleTaskPointerOnly` (the
   pointer is stale but the input belongs to a distinct task). The discriminator
   is one table for every absent-generation hangar row, with title as the
   positive nonzero control. Use the same retail and port controls; do not add
   a mitigation.

   Required commands:

       ./submodule-patches/export.sh
       cmake --build build -j8
       env zsh scratch/agent/run_s3690_m5_stale_input_payload.sh

   Kill both processes with SIGKILL. Keep all arms in one build/run and retain
   positive controls in the same capture.

2. **M3 parked audit — `rs_zcfree` incoming `$a0` at `0x80005268`.** Start
   only when M5 is unavailable or closed. Audit the complete idiom class,
   identify the writer and legitimacy of the value, and land a guard only if
   a concrete invalid writer is found. The closed `rs_free` audits and their
   evidence are archived in PROJECT-OVERVIEW §56; do not re-audit them.

3. **Generated-symbol renaming sweep.** Resume only after M5 is closed and
   M3 has no new discriminator. Use one bounded region/census per session and
   preserve the slug `generated-symbol-renaming-sweep` for that campaign.

## Active hypothesis table

| Hypothesis | Status and discriminating evidence |
|---|---|
| `H-LaterRouteOwnsInput` | Refuted for 244/244 measured absent rows at s3690; no input-DMA key joined the later task. |
| `H-StaleInputAcrossReuse` | Selected at s3690: 244/244 absent-generation hangar rows joined an earlier/equal input task identity. |
| `H-InputDmaKeyStillUnavailable` | Selected only at the output-DMA boundary by s3688; superseded by the input-DMA key. |
| `H-SourceBeforePublish` | Selected for 778/1,024 source rows at s3680; source reads can precede route publication. |
| `H-SourceSameGeneration` | Selected for the generation-joinable stage class at s3682 and title source rows at s3683. |
| `H-LaterRouteReuse` | Selected at s3686 for 244/244 measured absent-generation hangar rows. |
| `H-AbsentDistinctTask` | Refuted at pointer level by s3684; absent rows used `0x80171E70`, also present in the stage stream. |
| `H-SelectorInterleave` | Selected at s3666; selector publication matches each task object, including alternating hangar objects. |
| `H-PrimaryInitialization` | Selected single-source at s3669; `0x800078EC` is fixed zero-fill initialization, not object payload ownership. |
| `H-PayloadBeforeSelector` | Selected at s3667; watched-span writes preceded title and hangar VI phases. |

## Recent evidence ledger

- **3690 — input-DMA ownership boundary:** 244/244 absent-generation hangar
  source rows joined an earlier/equal input task identity; none joined a
  later task and none was missing or contradictory. See
  [M5-S3690-INPUT-DMA-OWNERSHIP.md](M5-S3690-INPUT-DMA-OWNERSHIP.md).
- **3688 — keyed per-range DMA boundary:** source event, task generation, and
  route publication fields fired in output-DMA rows, but 257/258 absent-source
  rows lacked a same-event range and one was contradictory. Input-DMA identity
  remains the next boundary. See [M5-S3688-KEYED-DMA-EMISSION.md](M5-S3688-KEYED-DMA-EMISSION.md).
- **3687 — absent-source DMA ownership join:** the prior output-DMA record had
  no stable join key. This motivated the s3688 field-carrying change. See
  [M5-S3687-ABSENT-DMA-OWNER-JOIN.md](M5-S3687-ABSENT-DMA-OWNER-JOIN.md).
- **3686 — absent-source route join:** 244/244 absent-generation rows advanced
  to a later route ordinal/row; 0 stayed on the source route and 0 were
  contradictory or missing. See [M5-S3686-ABSENT-ROUTE-JOIN.md](M5-S3686-ABSENT-ROUTE-JOIN.md).
- **3685 — absent-source publication join:** all 236 measured absent rows had
  a later same-pointer stage generation. See [M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md).
- **3684 — absent-source task join:** all 220 measured absent rows used
  `0x80171E70`, also present in the stage stream. See [M5-S3684-ABSENT-SOURCE-DMA-JOIN.md](M5-S3684-ABSENT-SOURCE-DMA-JOIN.md).
- **3683 — source-centric generation census:** title was 512/512 same
  generation; hangar was 282/512 same-generation, 230 absent, 0 reversed.
  See [M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md](M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md).
- **3680–3682 — publication and generation joins:** stage rows matched the
  latest published route; source rows split exact-route and route-lagged
  classes; generation-first matching found source-before-stage ordering for
  the joinable class. See [M5-S3680-PUBLICATION-ROUTE-JOIN.md](M5-S3680-PUBLICATION-ROUTE-JOIN.md),
  [M5-S3681-SOURCE-PUBLICATION-ORDER.md](M5-S3681-SOURCE-PUBLICATION-ORDER.md), and
  [M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md](M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md).
- **3677–3679 — key boundary corrections:** pointer-only and exact
  route/task joins failed; generation and thread keys exposed publication
  timing, and s3680 corrected the route sample to actual publication.
- **3667–3676 — source and stage boundary:** source writes preceded target
  phases; the primary writer is fixed initialization; remaining writer sites
  are padding/table initialization; input reads were nonzero in title and
  zero in hangar; source/stage route ordinals did not align.
- **3659–3666 — task and selector ownership:** scalar stores were zero;
  target descriptors use a shared writer family but phase-specific task
  objects; selector publication interleaves those objects.

Earlier M3 class closeouts (sessions 3586–3658) are archived in
PROJECT-OVERVIEW §56. Earlier M5 boundary notes remain in `docs/` and the
append-only ledger; only live transitions are repeated here.

## Durable boundaries and operating rules

Factor 5 uses [F5-UCODE-REFERENCE.md](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is sufficient for the validated route.

MusyX/MORT audio remains partially stubbed. MusyX task data cannot be sent to
stock `aspMain`; the silent arm returns `RspExitReason::Broke`. Do not infer
audio behavior from a route that fails to reach the target phase.

Every instrument needs an independent ground-truth request, a same-run
positive control, a phase-scoped budget, and two evidence lines before its
result becomes current truth. Phase-gate animated comparisons on VI
transitions. Batch A/B arms in one build and run. A counter is not a control.

Regeneration order is `make_elf.py -> N64Recomp -> fixup_game_funcs.py ->
CMake`. Never hand-edit generated functions for behavior changes. If `lib/`
changes, run `./submodule-patches/export.sh` and commit refreshed patches.
Never run submodule update, checkout, clean, or hard reset commands. Kill runs
with SIGKILL and run from `build/`. A mitigation-shaped change needs an
`ORIGIN:` line naming the writer and stating whether its value is legitimate.

## Superseded conclusions

The s3579–s3584 inference of a retail-versus-port stored-value divergence at
`0x800078EC` is unsupported: retail executes `sb $a1, 0($v0)`, while the
oracle read an aligned word containing neighboring bytes. Scalar-store samples
measured zero bytes with zero mismatches.

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed.

The request-only SP-yield/viewer-stall chain describes only the old diagnostic
arm. The old interpretation of the cinematic pool as an audio-slot pool was
superseded by the MusyX voice-table measurement.

The claim that `0x8002BEEC` is the retail JAL dispatch to `0x800078EC` is
route-dependent and unreconciled. Do not treat it as a writer without a new
independent discriminator.

Sessions 3512/3516 selected non-observable predecessor watches; their positive
controls remain useful, but absent predecessor rows do not establish parity,
divergence, or mutation. The s3585 standalone-slot interpretation of
`voice_record+0x64` was superseded by s3586's packed-handle audit.

## Evidence index

- [M5-S3688-KEYED-DMA-EMISSION.md](M5-S3688-KEYED-DMA-EMISSION.md)
- [M5-S3687-ABSENT-DMA-OWNER-JOIN.md](M5-S3687-ABSENT-DMA-OWNER-JOIN.md)
- [M5-S3686-ABSENT-ROUTE-JOIN.md](M5-S3686-ABSENT-ROUTE-JOIN.md)
- [M5-S3685-ABSENT-PUBLICATION-JOIN.md](M5-S3685-ABSENT-PUBLICATION-JOIN.md)
- [M5-S3684-ABSENT-SOURCE-DMA-JOIN.md](M5-S3684-ABSENT-SOURCE-DMA-JOIN.md)
- [M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md](M5-S3683-SOURCE-CENTRIC-GENERATION-CENSUS.md)
- [M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md](M5-S3682-GENERATION-FIRST-SOURCE-STAGE-JOIN.md)
- [M5-S3681-SOURCE-PUBLICATION-ORDER.md](M5-S3681-SOURCE-PUBLICATION-ORDER.md)
- [M5-S3680-PUBLICATION-ROUTE-JOIN.md](M5-S3680-PUBLICATION-ROUTE-JOIN.md)
- [M5-S3669-PRIMARY-STORE-CONTEXT.md](M5-S3669-PRIMARY-STORE-CONTEXT.md)
- [M5-S3667-PAYLOAD-ORDER.md](M5-S3667-PAYLOAD-ORDER.md)
- [M5-AUDIO-PLAN.md](M5-AUDIO-PLAN.md)

Sessions 1–3688 remain in the append-only ledger. Use bounded `grep`/`sed`
windows for `PORTING-STATE.md`, never read it whole.
