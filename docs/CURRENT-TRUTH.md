# Rogue Squadron 64 Recomp — current truth

Operational state for [`PORTING-STATE.md`](../PORTING-STATE.md). Durable
background is in [`PROJECT-OVERVIEW.md`](PROJECT-OVERVIEW.md); exact run
recipes and evidence remain in the ledger and `scratch/agent/`.

Current maintenance marker: Session 3218 (2026-08-29).

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

1. M5 target-phase qualification remains an open dependency: the current build
   was rechecked with the retained `s2618` route and the eleven-Start route;
   both image arms passed dispatch/host controls but stopped at VI 640
   (`0x0066A500`) with no title or hangar transition. A human-selected route or
   equivalent new retail-grounded boundary is still required. Do not repeat
   either route unchanged.
2. M3 voice-list publication audit is complete: the literal head census found
   only the named insertion/removal/reset family at `0x80098B84`,
   `0x80098D88`, `0x80098E38`, `0x80098F60`, `0x800999B8`, and `0x80099C30`.
   The reaper's `next` walk is null-terminated and finite. No invalid producer
   or ordering edge was identified; retain the existing guard as safety only.
   Evidence: `scratch/agent/s3216_m3_voice_list_publication_bound.md`.
3. The bounded `func_80092F10` live-tail audit is closed as a data-gap
   exclusion: it overlaps the real `packFourLutResampledSamples` entry at
   `0x80092F94`, has no callable body or fan-in, and has no companion semantic
   symbol. No rename was made. Evidence:
   `scratch/agent/s3217_generated_symbol_rename.md`.
4. After a route change, rerun the existing same-build phase-gated pair with
   `ROGUESQ_AUDIO_UCODE=0/1` and `ROGUESQ_LOG_ALL=1`. Require image-arm DMEM,
   DMA, `Broke`/SP completion, service, slot, and PCM joins; retain the silent
   arm as the no-write control.
5. The 43-site `SONGTEMPO_TABLE_GUARD` class has a concrete
   `startSongSequence` writer at `0x80096D88` and is already fully covered; no
   new guard work is authorized.
6. Session 3212 renamed the sole remaining callable generated placeholder
   `static_4_80106C50` to `lvc_registerObjectiveBooleanCounts` in the
   generated declaration/body using a bounded, regeneration-safe tool. The
   body registers objective boolean-count handles and is called from
   `lvc_initializeObjectTracking`; the data-gap/live-tail fragments remain
   unchanged. The follow-up live-tail audit in Session 3217 found no
   additional callable placeholder; resume M3/M5 work after this sweep
   closure.
7. M4 restage destination identity is now known: hangar gfx tasks use
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

Recent evidence includes `scratch/agent/s3218_m4_retail_dest/RESULTS.md`,
`scratch/agent/s3217_generated_symbol_rename.md`,
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
