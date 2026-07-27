# s79 — D3: high-tri `syncs=0` / FULL_SYNC starvation discrimination

Source: **same-run offline re-analysis of s78 `fbgate3/run.log`** (already
had `ROGUESQ_LOG_RUNNER_ALL=1`; no new build). Capture-once / analyze-many.
Positive control: 5165 `[runner]` lines (every task), 1133 `[last-drawn]`,
899 `Unhandled jump target 0x0231` — instruments visibly fire.

## Transition (hard edge)

| task# | exit | tris | tex | fill | syncs | depth | note |
|------:|-----:|-----:|----:|-----:|------:|------:|------|
| 4248–4250 | 1 | ~1122 | 57 | 1 | **1** | 1 | steady SELECT YOUR CRAFT-class |
| **4251** | 1 | 1122 | 57 | 1 | **1** | 1 | **LAST** high-tri with syncs≥1 (2385-task streak) |
| **4252** | 1 | 587 | **0** | **0** | **0** | 2 | **ONSET** — DL shape changes |
| 4253–4264 | 1 | ~590 | 0 | 0 | 0 | 2 | 13 healthy RSP exits, still no FULL_SYNC |
| **4265** | **3** | 320 | 0 | 0 | 0 | 2 | first UnhandledJump 0x0231 |
| 4266–5165 | 3 | ~170 | 0 | 0 | 0 | 2 | 901× exit=3; **never** syncs≥1 again |

After onset: **914/914** high-tri tasks have `syncs=0`. Recoveries: **0**.

## Hypotheses

| ID | Claim | Verdict | Evidence |
|----|--------|---------|----------|
| **S1** | Trailing hangar-flight tasks emit 0 SYNC_FULL; VI_FULLSYNC is the only remaining frame boundary and stops matching | **SUPPORTED** | 100% syncs=0 from #4252; last `fs` increase ≈ task **#4254** (`fs=3297`); 30 update_screen samples stuck at 3297 while ~900 more tasks run |
| **S2** | Tasks still emit SYNC_FULL but fullSync is skipped (pair/path gate) | **REFUTED** | 0 high-tri with `syncs≥1` after onset — nothing for a pair-gate to skip |
| **S3** | UnhandledJump 0x0231 aborts tasks *before* SYNC_FULL (causes onset) | **REFUTED as primary** | Jump starts **#4265**, 13 tasks *after* onset; gap is 13× `exit=1` with tris>0 and syncs=0 (RSP Broke healthy). Jump is a **secondary** hangar-flight failure, not the FULL_SYNC loss |
| **S4** | Present follows a dead last-drawn while geometry lands in a live FB | **PARTIAL / weak** | last-drawn goes **wild at #4251** (`0x002340 w=1121`) on the last good-sync task, then wild/sane interleaved through #4265; `present-1024` still reports `empty=0` on `0x6AB000`/`0x656000` at #4263/#4265 then stops. Pixel freeze is byte-identical `craft_stable`…`hold_10_sr` (md5 `09d7963e9fd2`) — present frozen, but geometry-on-sane-FB after freeze is not proven by this log alone |

## VI_FULLSYNC interaction (single-source from code + fs counter)

Synthetic path (`rt64_state.cpp`) fires only when
`!g_rs64FullSyncSeen && (addressChanged || stalled) && pending.fbPairCount > 0`.
Post-onset, real FULL_SYNC never sets `g_rs64FullSyncSeen`. VI origin still
alternates `0x656400`/`0x6AB400` after the plateau (addressChanged should be
true). **`fs` only advances once more after the last real SYNC_FULL**, then
stalls — so either `fbPairCount==0` on the pending workload, or `fullSync()`
runs without incrementing the observed counter. Discriminate next unit with
an always-on rate-limited decision log (not gated on `ROGUESQ_LOG_ALLOC`).

## Secondary: UnhandledJump 0x0231

- 899 log lines; first at runner #4265; 100% of remaining tasks `exit=3`.
- Source: `factor5_ucode_recompiled.c:217` → target `0x0231`.
- Parked as **M3 secondary** after present/FULL_SYNC is restored (or in
  parallel only if a probe shows it *prevents* pair accumulation).

## Positive control

| instrument | fired |
|------------|------:|
| `[runner]` every task | 5165 |
| `[last-drawn]` | 1133 |
| Unhandled jump | 899 |
| `[fb-get] REFUSE` | 40 (rate-limit) |
| tilecopy found=1 (640 only) | ≥6000 (s78) |

## Next (from S1)

Instrument VI_FULLSYNC **decision** (fire / skip reasons: `FullSyncSeen`,
`addressChanged`, `stalled`, `fbPairCount`) always-on, rate-limited, same
start_only hold soak. Discriminate empty pending pairs vs synthetic not
called vs fullSync no-op. Optional batch: count post-onset CIMG targets
(sane 0x656/0x6AB vs refused wild) on the same build.
