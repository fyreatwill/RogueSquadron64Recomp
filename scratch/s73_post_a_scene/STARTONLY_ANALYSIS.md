# s75 — single-Start isolation from SELECT YOUR CRAFT

## Run

| | |
|---|---|
| tag | `startonly/` |
| mode | `PROBE_MODE=start_only` → one Start, 15s after-frames, 20s grace |
| schedule | phase-gated 1024: `3:start 25:start 40:start 60:a` then STABLE_S=12 |
| env | LLE_FORCE+UNGATED+SOLO+STUB_MISSING, LOG_RUNNER_ALL, LOG_THREAD_RESUME, LOG_OST_WB |
| console | `startonly_console.txt` |

Phase 1024 @44.7s; process alive through full wall (~54s post-`a`); SIGKILL at end. CRASH=0.

## Positive control (instrument)

Title-yellow = count of `r>150 g>90 b<100` in crop `(0,64)–(896,208)` on 1280×1024 captures
(recovered to match keys2 craft_stable = 15639).

| frame | yel | visual |
|-------|-----|--------|
| stable_01 / stable_12 / craft_stable | 12.3k–13.1k | SELECT YOUR CRAFT (full HUD) |
| pre_p1_start | 13074 | still SELECT — pre-press control |

SELECT signature present before the probe Start. (Absolute yel ~13k vs keys2 ~15.6k:
same crop/threshold; likely camera/angle or partial anti-alias of the title glyph.)

## Discriminating series (one Start after craft_stable)

| frame | +s | yel | visual |
|-------|----|-----|--------|
| post_p1_start | 0.6 | 13045 | SELECT |
| after_p1_start_01 | 1 | 10321 | SELECT, HUD still |
| after_p1_start_02 | 2 | 488 | HUD fading (title ghost) |
| after_p1_start_03 | 3 | 1458 | leaving |
| after_p1_start_04 | 4 | 0 | **hangar-flight** — airborne X-wing, no menu |
| after_p1_start_05–06,09 | 5–9 | 0 | hangar-flight + multi-hue floor garbage |
| after_p1_start_07–08,10–15 | — | 0 | mostly black captures (~44 KB) |
| grace_01–20 | — | 0 | all black captures |

## Hypotheses

| ID | Claim | Result |
|----|--------|--------|
| S1 | Single Start enough once craft-select stable | **Supported.** Leave by +2–4s; hangar-flight with content through ~+6–9s. |
| S2 | Double Start required | **Refuted this run.** Only one post-stable Start fired. |
| S3 | Start only works after `a` | **Refuted this run.** Probe sequence was Start-only (schedule `a` was the earlier AVAILABLE CRAFT → craft-select transition, not a craft-select description press). |
| S4 | First Start often dropped | **Not required to explain leave.** This Start delivered. s74 "first +3s still SELECT" likely snap-overwrite and/or short 3s window / intermittent drop — not a hard double-Start rule. |

## Stability (controls)

- thr-resume bad=1: **0**
- exit=2 / ImemOverrun: **0**
- missing-func / UnhandledJump: **0**
- CRASH lines: **0** (process survived grace; no MetalFramebuffer SIGSEGV this soak)
- ost-wb SKIP_WIDTH=14 SKIP_OOB=8 (gate still active)
- fs max=3360 then **frozen** (last advance before freeze ~#7808 fs=3356 → #7872 fs=3360 holds to #9600)
- VI stays 512 + 0x6AB400/0x656400 pair through hangar-flight

## Residual (next unit, not S1–S4)

Hangar-flight **presents content for only ~6–9s** post-leave, then captures go black while the process stays alive and `fs` is frozen. keys2 instead SIGSEGV'd MetalFramebuffer ~10s post-leave. Both are the sustained-hold problem for M3's 60s requirement — separate from the leave-key question, which is closed for the default path.

## Files

- `scratch/s73_post_a_scene/startonly/` (snaps + run.log)
- `scratch/s73_post_a_scene/startonly_console.txt`
- unique tags `pre_p1_start` / `after_p1_start_NN` (s74 overwrite bug fixed in script)
