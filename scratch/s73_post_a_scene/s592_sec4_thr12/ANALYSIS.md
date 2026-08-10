# s592 post-sec4 thr-12 (item -361)

## Recipe
`PROBE_MODE=start_only HOLD_S=90` +
`ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1` +
`LOG_DL_SYNC LOG_FS_SLOT LOG_RDP_FULLSYNC LOG_AUDIO_DRAIN` (+ hangarbay on r2)

## Runs

| run | hangar peak | case6-force | hangar-sel | inject | recovery@76B768 | post-exit sec4 | thr-11 destroy | thr-12 post-sec4 | crash |
|-----|-------------|-------------|------------|--------|-----------------|----------------|----------------|------------------|-------|
| s589 (prior) | state 5→8 | yes | yes | n=300+ | ×1988 | **yes** | id=11 | **no** (crash pre thr-12) | coalesce/initScene 0x8000247c |
| s591 (prior) | state 5→8 | yes | yes | n=26 | **0** | no | never | no | trackResourceList 0x80065e94 |
| **s592** | state 5→6 n=1020 | **0** | **0** | **0** | **0** | no | thr-10 live | n/a | `reserveAndEmitDLEntry+18192`/`0x8000ce54` hold-iter 2 |
| **s592_r2** | state 5 n=825 | **0** | **0** | **0** | **0** | no | thr-10 live | n/a | `beginFrameDLChunk+46800`/`0x8000afa0` hold-iter 1 (**item -338 4th occ**) |

## H13 discrimination

| H | Verdict this session | Evidence |
|---|----------------------|----------|
| H13a recovery intermittent; retry until sec4 | **SUPPORTED as path-gate** | 0/2 this session reached exit (not even inject). Prior s589 1/N hit thr-11 destroy+sec4. Gate for thr-12 measurement is **pre-exit hangar survival**, not thr-12 itself. |
| H13b thr-12 soon after sec4 | **untested** | no post-exit sec4 |
| H13c initScene systematically blocks thr-12 | **untested** (s589 still single sec4 data point) | need ≥1 more sec4 hold |
| H13d thr-12 independent of thr-11 destroy | **untested** | |

## Positive controls (required for -361; none armed this session)
- case6-force-start — **MISS** both runs
- hangar-sel + state8 — **MISS**
- inject n>0 — **MISS**
- recovery @0x76B768 — **MISS**

## Recharacterization
Item -361 cannot discriminate thr-12 vs initScene until force path reaches post-exit sec4.
s592 2/2 died in hangar at state 5/6 on known intermittent families before ACE94 force site.
Next: multi-retry force soaks (soak_queue) until sec4 lands; then apply thr-12 vs crash gate.

## Item -338 note
s592_r2 is **4th** occurrence of `beginFrameDLChunk`/`0x8000afa0` (s554, s572, s574, s592).
Still do not open reactive chase until exit works; confidence high.
