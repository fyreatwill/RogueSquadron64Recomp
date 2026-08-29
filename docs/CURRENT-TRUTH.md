# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and evidence remain in the ledger and `scratch/agent/`.

Current maintenance marker: Session 3233 (2026-08-29).

## Current state

The native port builds and boots through attribution, the N64 logo, intro
cinematic, star flare, Factor 5 logo, title VI 1024 (`0x00790400`), and hangar
VI 512 (`0x006AB400`) on the validated spin-yield/F5-LLE route. Hangar visuals
still have geometry/color artifacts. Audio is not production-complete: the
Factor 5 image task is the qualified real-audio arm and `musyx_stub`/Broke is
the silent control.

The latest same-build M5 image-versus-silent qualification (Session 3192)
passed dispatch controls in both arms but reached only pre-title VI 640
(`0x0066A500`). Independent retail controls reached title and hangar. Thus all
target-phase audio/task/DMA/service/slot/voice/MORT/PCM nulls are unevaluable;
no audio, route, VI, gate, wait, voice, destination, or output change is
authorized without a named legitimate writer and ordering edge. Do not remove
the status-03 wait hatch.

## Next steps

Priority is maintenance, M5 de-stubbing, systematic M3, then generated-symbol
renaming. M5 design is complete in `docs/M5-AUDIO-PLAN.md`.

1. M5 target-phase qualification is no longer blocked on route selection.
   Session 3233 repaired the retail oracle join: the prior implementation
   silently discarded the target route's following 640-to-1024 transition
   because it accepted only the attract origins `0x00696100/0x00696600`.
   With an any-next-VI diagnostic arm, the positive-controlled run produced
   two joins, including pre/next origin `0x00790A00`; the route `$a0` was
   `0x8014090E` (physical `0x0014090E`), not a framebuffer. This validates
   route execution and join ordering but does not select a legitimate writer
   or port origin-selection hypothesis. Next, use a target-phase join that
   captures the actual VI context/framebuffer fields, not route `$a0`.
   Session 3232's independent retail runs passed the whole-RDRAM control,
   reached title and hangar, and fired all four established route PCs at the
   `0x00790A00` transition. The `osViSwapBuffer` phase join returned
   `latched=0, joined=0` in both full-schedule captures, so the
   writer-to-swap discriminator is unevaluable. A shorter retry took a direct
   `0x0066A500 -> 0x00790400` route and its zero route counts are unevaluable.
   Do not infer a legitimate writer or port origin-selection defect from
   these runs; repair the oracle join around a route execution PC before
   adding port counters.
   Session 3231 changed `get_rsp_microcode` to read `ROGUESQ_AUDIO_UCODE`
   per `M_AUDTASK` instead of caching the first task's arm. Same-build image
   and silent smoke controls produced 46/45 dispatch rows and 552 SP-return
   rows respectively, with every row on its requested arm and no crash or
   abort. This closes the stale-selector hypothesis at the dispatch boundary
   only; both runs stopped before title, so downstream audio/task/DMA/service/
   slot/voice/MORT/PCM conclusions remain unevaluable. The next work unit
   returns to the independent retail VI-swap/origin attribution below.
   Session 3230's same-build silent/image capture selected
   `H-PhaseDifferentEdge`: both port arms reached 640/origin `0x0066A500`
   and emitted the same live VI-commit and audio-return rows, while retail's
   four watched route PCs occur at 640/origin `0x00790A00` before title. This
   closes the exact-origin alias join and does not establish a missing port
   sequence. The next work unit is a ground-truth retail VI-swap/commit
   attribution at the `0x00790A00` transition, with a whole-RDRAM control, to
   identify the legitimate origin writer and compare its physical buffer to
   the port's `0x0066A500` commit before adding more port counters.
   Session 3229 watched retail caller, reapply entry, reapply call, and return
   branch in one run. The whole-RDRAM control reached 10,000 callbacks; all
   four watches fired once in order at 640 origin `0x00790A00`, then retail
   reached title 1024. The caller and return values match the port's
   `audio-return` row at `0x0066A500` with `target=0`. This refutes an absent
   retail caller and gives no evidence of a wrong value or local ordering
   defect, but it is not a like-for-like port comparison because the phase
   origins differ. The next work unit is to redesign the phase join around the
   observed transition, not add another return-branch field.
   Session 3227 proved the retail `reapplyDisplayMode` entry/call edge is
   live, with two calls at 640 origins `0x00696100` and `0x00790500` before
   title 1024; no call occurred at the port's `0x0066A500` stop. The
   whole-RDRAM positive control and title gate passed, so this is a valid
   phase-boundary correction, not a null instrument. It does not yet select
   writer-absent, wrong-value, or ordering. The next discriminator is the
   return branch at `0x8008EBC8`, watched with the two corrected 640 origins,
   then aligned to the port's phase-3 route and phase-4 audio-return rows.
   If alignment remains impossible, redesign the boundary before adding
   instrumentation.
   Session 3226 closed the first concrete field candidate: retail writes to
   `0x80141AD0/1` and `0x8013B038` are early `setDisplayMode`/
   `reapplyDisplayMode` configuration stores, not the missing pre-title route
   publication. The positive-control oracle reached title 1024, and the
   static port audit matched the writer PCs, so no value or ordering change is
   authorized from this field class. The actual route consumer boundary
   remains open. Session 3225 independently revalidated the locally available,
   retail-qualified phase-relative route
   `3:start,7:start,11:start,15:a,30:start,45:start,60:a,75:start,90:a`:
   retail passed the whole-RDRAM positive control and reached title 1024,
   while the same-build port silent/image pair stopped at VI 640 origin
   `0x0066A500`. Matching input edges and continued recv progress, alongside
   identical route-state output with `target=0`, select `H-PortStateBoundary`
   over input or scheduler stall. The next work unit is a bounded audit of the
   pre-title route-state writer/publication edge, not another audio null.
   The next discriminator is an oracle execution watch on
   `reapplyDisplayMode` entry/call (`0x8008EB5C`, `0x8008EBC0`) with the same
   whole-RDRAM positive control, then a bounded comparison of its live
   arguments and return branch against the port.
2. A12's `0x8014974C` publication class is closed by Session 3221: the only
   guest stores are `setupSongRenderBuffers` zero-init, `musyxSynthFrame`
   terminal clear, and its fixed-one pre-callback publication. The waiters
   remain safety-only; no timeout, force-clear, or new guard is authorized.
3. After a route-boundary change, rerun the existing same-build phase-gated
   pair with `ROGUESQ_AUDIO_UCODE=0/1` and `ROGUESQ_LOG_ALL=1`. Require image-
   arm DMEM, DMA, `Broke`/SP completion, service, slot, and PCM joins; retain
   the silent arm as the no-write control.
4. Closed static M3 publication classes, retain existing traps/guards as
   safety only: A8 `musyxKeyOnVoice` divide/overflow has one live cmd-list
   divisor store (`musyxRenderVoiceSamples` at `0x80090768`, constant
   `0xC0`); the four `break 6` sites are unreachable after `lhu +0x60`; the
   four `break 7` sites are the game's own divide-by-zero handler
   (evidence: `scratch/agent/s3220_m3_keyon_divisor_descriptor.md`). A12's
   flag census is recorded in
   `scratch/agent/s3221_m3_a12_flag_publication_census.md`. A9
   voice-array base (`D_801496F8`) has one store at `0x8008F0EC` in
   `allocateSongChannelArray` (evidence:
   `scratch/agent/s3219_m3_voice_array_base_publication.md`); A10 3D
   voice-list head (`0x80153414`) has only the named insertion/removal/reset
   family (evidence: `scratch/agent/s3216_m3_voice_list_publication_bound.md`);
   the 43-site `SONGTEMPO_TABLE_GUARD` class has writer `startSongSequence` at
   `0x80096D88`. No new guard work is authorized on these classes.
5. Generated-symbol sweep remains closed at the evidence boundary (Sessions
   3210/3212/3217). `static_4_80106C50` was renamed to
   `lvc_registerObjectiveBooleanCounts`; `func_80092F10` is a data-gap
   exclusion overlapping `packFourLutResampledSamples` at `0x80092F94`.
6. M4 restage destination identity is now known: hangar gfx tasks use
   `gspTask` (`0x800377C8`) with physical `output_buff` `0x0075C000` /
   `0x00781800`, not the port runtime dest `0x4B7800` and not DMEM `0x670`.
   Keep the external retail-entry boundary, hangar `0x8000` Y / accumulator
   arithmetic, and M5 SP-yield/MORT publication threads parked pending a
   new target-phase discriminator. The corrected MORT descriptor edge is
   `+0x190` to `dmaVoiceSampleAndSignal`; `+0x194` is the speech source.

## Durable boundaries and operating rules

Factor 5 uses [`F5-UCODE-REFERENCE.md`](F5-UCODE-REFERENCE.md), not standard
F3DEX assumptions. The qualified graphics path is LLE-only. Interpreter
limits, null-GBI guards, and similar defenses are safety mechanisms, not
explanations. Overlay dispatch is fixed enough for the validated route.

Ask the independent retail oracle for ground truth before adding port
instrumentation. Every instrument needs a same-run positive control,
phase-scoped budgets, and two independent lines of evidence before promotion.
Phase-gate animated comparisons on VI transitions and build every A/B arm
together. A null without a positive control is worthless.

Regeneration order is `make_elf.py` → N64Recomp → `fixup_game_funcs.py` → CMake.
Never hand-edit generated functions for behavior changes. If `lib/` changes,
export submodule patches in the same iteration. Never run `git submodule update`,
`git checkout -- lib/...`, `git clean`, or `git reset --hard`. Kill runs with
SIGKILL and run from `build/`. A mitigation-shaped change requires an `ORIGIN:`
line naming the writer and stating whether the value is legitimate.

## Superseded conclusions

The original overlay/menu-only explanation, intrinsic VI-640 flakiness,
missing-input and wait-return explanations, global-zero image-DMA theory,
route-wide PCM-gap theory, and force-zero default policy are superseded at
their measured scopes. They were believable before qualified routes,
same-build controls, or independent retail attribution existed. Full failed
experiments remain in the ledger and archived overview.

Static boundary-only symbol classifications remain non-renames when companion
symbols, source/m2c, callers, and local semantics do not provide a defensible
name. Stable companion duplicate-prefix and preamble mappings belong in
`tools/rename/build_redefs.py`.

## Evidence index

Recent evidence includes
`scratch/agent/s3226_m5_route_writer_oracle/RESULTS.md`,
`scratch/agent/s3220_m3_keyon_divisor_descriptor.md`,
`scratch/agent/s3225_m5_route_boundary.md`,
`scratch/agent/s3219_m3_voice_array_base_publication.md`,
`scratch/agent/s3218_m4_retail_dest/RESULTS.md`,
`scratch/agent/s3217_generated_symbol_rename.md`,
`scratch/agent/s3216_m3_voice_list_publication_bound.md`,
`scratch/agent/s3213_m3_voice_list_table_audit.md`,
`scratch/agent/s3209_generated_symbol_rename.md`,
`scratch/agent/s3208_generated_symbol_rename.md`,
`scratch/agent/s3207_generated_symbol_rename.md`,
`scratch/agent/s3205_generated_symbol_rename.md`,
`scratch/agent/s3204_generated_symbol_rename.md`,
`scratch/agent/s3203_generated_symbol_rename.md`,
`scratch/agent/s3202_generated_symbol_rename.md`,
`scratch/agent/s3192_m5_step1_contract_pair.md`,
`scratch/agent/s3185_retail_producer_wait/RESULTS.md`, and generated-symbol
reports `scratch/agent/s3197_generated_symbol_rename.md` through
`scratch/agent/s3203_generated_symbol_rename.md`. Use `grep -n` plus a bounded
`sed` window for `PORTING-STATE.md`; never read that multi-megabyte ledger
wholesale. The soak queue is consumed by automation; fold only new tail lines
into the next audit. Session 3210 closes the generated-symbol sweep; see
`scratch/agent/s3210_generated_symbol_rename.md`.
