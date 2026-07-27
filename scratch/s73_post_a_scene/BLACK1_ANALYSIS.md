# s81 — B1–B4: intermittent black after leave (offline, vifs1)

Source: **no new build**. Offline re-analysis of s80 soak
`scratch/s73_post_a_scene/vifs1/` (run.log + snaps). Work unit from
CURRENT-TRUTH next-step #1 / NEXT.md B1–B4.

## Positive controls (same artifact set)

| control | result |
|---------|--------|
| Capture pipeline works | hold_09 / hold_15 rich (124k / 120k colours); craft_stable content |
| Pure-black class is real | hold_01/08/11/14, after_p1_start_05, stable_02: **byte-identical** hash `7ff2aeb67038`, meanL=4.5, uniq=194 (chrome-only yellow residual) |
| Instruments live through freeze | last-drawn, present-1024, vi-follow-draw, vi-fs-decision all fire post-leave |
| s80 FIRE after rdpFs plateau | still true; not re-litigated |

A null "black because capture broken" is ruled out: same window id produces
rich and black snaps interleaved.

## Snap timeline (game t ≈ 47.6 + mtime_rel; 1024 phase @44.6 + key@3)

| snap | ~t | class | notes |
|------|-----|-------|-------|
| craft_stable | 122.8 | content | SELECT YOUR CRAFT |
| after_p1_start_05 | 128.6 | **BLACK** | identical black hash |
| hold_01–08 | 129.7–137.5 | **BLACK** | identical black hash |
| hold_09 | 138.7 | **RICH** | hangar-flight, ≠ craft_stable (mean abs ~73) |
| hold_10_sr | 140.4 | partial | stick mark |
| hold_11–14 | 141.5–144.8 | **BLACK** | same hash as hold_01 |
| hold_15 | 146.0 | **RICH** | different from hold_09 (mean abs ~18) |
| death | ~150 | | phase →640, unaligned do_rom_read |

rdpFs plateau first FIRE #7717 ≈ **128.6 s** — co-timed with leave/black onset
(S1 restated; not re-tested).

## Critical instrument readings

### `present-1024 empty=0` is not continuous health

Log only fires when `g_rs64_last_drawn_fb` **address changes**
(`s_lastLogDrawn` in `rt64_present_queue.cpp`). During black windows the flip
rate collapses, so `empty=0` is a **stale transition sample**, not proof that
presents stay non-black. s80 V2 "empty=0 throughout" over-read this.

### last-drawn flip rate (512-wide alternation)

| window | last-drawn log rate | targets |
|--------|--------------------:|---------|
| craft-stable [122,128) | ~27/s | 0x656/0x6AB healthy |
| black hold [129,137) | ~3.6/s then gaps | pollution + collapse |
| mid freeze [138,145) | ~0 logged sane flips | last-drawn stuck / wild |
| hold_15 recovery [146,147) | resumes 0x656/0x6AB | content returns |

last-drawn only logs on **address change** (and width filter). Collapse =
flip death or non-512 flips, not a full draw census — still discriminating
when paired with vi-follow-draw.

### Smoking gun: mode-3 presents wild last-drawn

Default `ROGUESQ_VI_FOLLOW_DRAW=3` presents `g_rs64_last_drawn_fb`. Same run:

```
[last-drawn] #2393 0x6AB000 -> 0x001940 w=1185 siz=3
[vi-follow-draw mode=3] #4800 viAddr=0x006AB000 viW=512 -> last drawn 0x003FFFFF w=21
[vi-follow-draw mode=3] REGISTER #5 0x00020000 w=1 h=480
[vi-follow-draw mode=3] #4830 ... -> last drawn 0x00020000 w=1
[vi-follow-draw mode=3] #4890 ... -> last drawn 0x00002EA0 w=257
[vi-follow-draw mode=3] #4920 ... -> last drawn 0x0039FFFF w=11
[last-drawn] #2456 0x02FFFF -> 0x000000 w=1169
[last-drawn] #2486 0x0DFFFF -> 0x656000 w=512   ← recovery ~ hold_15
```

Whole-run vi-follow logs: **79 sane-width / 13 wild-width**. REGISTER
events: **6/7 wild** (w=1,1,1,1,48,59) + one sane 0x656000 w=512.

s78 refuse gate is `width > 1280` or OOB past 8MB. Widths **1..1185 pass**,
get registered, and mode-3 **presents them** → black (or empty RT).

When last-drawn becomes **0** (#2456), mode-3 skips override
(`if (drawn != 0)`) and falls through to stock VI — can briefly show real
content (hold_09 RICH while drawn stuck at 0).

## B1–B4 verdicts

| ID | Claim | Verdict | Evidence |
|----|--------|---------|----------|
| **B1** | Game intentionally clears colour FB | **WEAKENED** | Pure-black snaps are one chrome-only surface (incl. craft-select flash stable_02); last-drawn collapses into **wild** targets rather than steady clear-draws to 0x656/0x6AB. Does not rule out game-side clear as *one* contributor, but not the present mechanism. |
| **B2** | Present shows stale/wrong buffer | **SUPPORTED** (two lines) | (1) vi-follow-draw mode=3 logs **presenting w=1..257 last-drawn** during black window. (2) Code: mode-3 follows last-drawn; refuse only >1280. hold_09 RICH with last-drawn=0 = VI fallback; hold_15 recovers with sane 512 flips. |
| **B3** | Black = real in-game fade/loading | **PARTIAL only** | Content returns without port change (true). Black is **byte-identical port black** across menu + hangar-flight, not a progressive fade. Craft response still untested. |
| **B4** | Geometry to refused/wild CIMG | **SUPPORTED as B2 feed** | last-drawn set from wild RegularRect keys (w=1169/1185, addr 0x1940/0); FIRE lastCimg also wild in freeze — but wild FIRE cimg alone does not split black vs hold_09 (both wild). The **present** damage is last-drawn → mode-3. |

## What s80 misread

- `present-1024 empty=0` ≠ continuous non-black presents (transition-only).
- Intermittent black is not "mystery despite healthy present" — present is
  **explicitly following garbage last-drawn** for stretches of the freeze.

## Next probe (highest information)

**Gate last-drawn updates and/or mode-3 present** to sane widths only
(e.g. `{320,512,640,1024}` or `320≤w≤1024` with siz∈{2,3} and non-zero addr
aligned). Positive control: log `[last-drawn-skip]` when rejecting wild;
craft-select + hangar-flight content must still flip 0x656/0x6AB.

Expected:
- If black duty-cycle collapses → B2 confirmed causal; M3 hold becomes usable.
- If black unchanged with skip firing → B1/B3 need RDRAM/present-luma.
