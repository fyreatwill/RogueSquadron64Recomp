# s76 — 60s hangar-flight hold + stick (start_only path)

## Run

| | |
|---|---|
| tag | `hold60/` |
| mode | `PROBE_MODE=start_only HOLD_S=60` (leave-confirm 5s then hold_NN + sticks) |
| stick schedule | `10:sr 25:sl 40:su` (400 ms hold) — **never fired** (death at hold-iter 7) |
| schedule | phase-gated 1024: `3:start 25:start 40:start 60:a` then STABLE_S=12 |
| env | LLE_FORCE+UNGATED+SOLO+STUB_MISSING, LOG_RUNNER_ALL, LOG_THREAD_RESUME, LOG_OST_WB |
| console | `hold60_console.txt` |

Phase 1024 @45.0 s; process **abort** during hold; wall ~27 s post-`a`. Script: `run_mission_keys.sh` (HOLD_S path added this session).

## Positive controls

| control | result |
|---------|--------|
| SELECT pre-leave | craft_stable / pre_p1_start title-yellow **13040** — SELECT YOUR CRAFT visual |
| leave | yel 13041 → 0 by after_p1_start_04; hangar-flight X-wing airborne (no menu) |
| thr-resume bad=1 | **0** (s72 writeback still holds) |
| exit=2 ImemOverrun | **0** |
| missing-func / UnhandledJump | **0** |
| ost-wb SKIP_WIDTH/OOB | 15 / 7 (gate active) |

## Timeline (post-Start leave)

| frame | +s (approx) | yel | size | visual |
|-------|-------------|-----|------|--------|
| pre_p1_start | 0 | 13041 | 894k | SELECT YOUR CRAFT |
| after_p1_start_02 | 2 | 395 | 890k | leaving |
| after_p1_start_04–05 | 4–5 | 0 | 982k–1.1M | hangar-flight content |
| hold_01–02 | ~6–7 | 0 | 1.2M | hangar-flight, camera still moving |
| hold_03 | ~8 | 0 | 60k | near-black capture |
| hold_04 | ~9 | 0 | 1.4M | content again |
| hold_05–06 | ~10–11 | 0 | 44k | black |
| hold-iter 7 | ~12 | — | — | **process gone** |

Stick marks at hold 10/25/40 never reached → **H4 inconclusive**.

## Discriminating outcome

| ID | Claim | Result |
|----|--------|--------|
| H1 | 60s content hold if we wait | **Refuted.** Dead at ~7 s into hold (~12 s post-Start leave). |
| H2 | `fs` freezes ~6–10s; black; process may live | **Partial.** fs last advances at update_screen **#7872 → fs=3364**, plateaus through #8128; black snaps appear before death. Process does **not** stay alive this run. |
| H3 | Process dies before 60s | **Supported.** CRASH=1, signal **6** (Abort trap). |
| H4 | Stick changes craft pose | **No data** — death before first stick. |

## Death class (this soak)

```
Assertion failed: (fbIt != framebuffers.end()), function createTileCopyRecord,
  file rt64_framebuffer_manager.cpp, line 190.
```

Stack: `WorkloadQueue::threadRenderFrame` → `FramebufferManager::recordOperations` → `createTileCopyRecord`.

Immediate pre-assert log:

- `[last-drawn] #2060/#2063 0xE00000 -> 0xA6FFFF w=4007 siz=0` (wild CIMG cluster; 113/1314 last-drawn have w>1280)
- `[rt64] loadDrawState: copy-mode draw with undefined tile 7, marking invalid`
- trailing runner tasks #4329–4332: **syncs=0** with tris≈566–599 (prior tasks had syncs=1)

**Not** the keys2 `plume::MetalFramebuffer` SIGSEGV and **not** s72 OSThread writeback (bad=0). Same present/RT64 family as keys2 residual; new assert site.

## Stability counters (summary)

- lle tasks: 4333
- exit=1 (Broke): 4475 · exit=2: 0
- fs max: 3364 (frozen)
- CRASH: 1

## Files

- `scratch/s73_post_a_scene/hold60/` (snaps + run.log)
- `scratch/s73_post_a_scene/hold60_console.txt`
- `scratch/s73_post_a_scene/run_mission_keys.sh` (HOLD_S + stick schedule)
