# NEXT work unit — M3: VI_FULLSYNC decision after post-leave SYNC_FULL loss

s79: S1 supported (100% trailing `syncs=0` from #4252; fs plateaus ~#4254 at
3297). S2/S3-primary refuted. Detail:
`scratch/s73_post_a_scene/SYNCS0_ANALYSIS.md`.

## Competing hypotheses (why fs stops after one more advance)

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| V1 | `pending.fbPairCount==0` after onset → synthetic never fires | `[vi-fs-decision] SKIP pair=0` dominates freeze window; addressChanged still true on VI swaps |
| V2 | Synthetic fires but `fullSync()` early-outs / does not advance `fs` | `FIRE` lines continue while `fs` stuck; pair skip / workload counters rise |
| V3 | `addressChanged` false and `stalled` false (VI path not entering condition) | SKIP reason=no-trigger; origins not changing and wall clock <100ms between checks (unlikely at freeze) |
| V4 | `g_rs64FullSyncSeen` stuck true without real SYNC_FULL | SKIP reason=seen; runner still shows syncs=0 (instrument bug or unexpected setter) |

## Discriminating measurement (ONE build, ONE soak)

Add always-on rate-limited log in `rt64_state.cpp` VI_FULLSYNC block (not
behind `ROGUESQ_LOG_ALLOC`):

```
[vi-fs-decision] #N fire|skip reason=... seen= fsSeen addrCh= stalled= pairs=N vi=0x.. fs=N
```

Batch optional: post-onset CIMG target class counter (sane 512 @0x656/0x6AB vs
wild/refused) if cheap on the same edit.

```bash
# after build:
env PROBE_MODE=start_only HOLD_S=20 \
  zsh scratch/s73_post_a_scene/run_mission_keys.sh vifs1 0 12
# offline:
#   first decision after last runner syncs>=1 high-tri
#   FIRE vs SKIP counts while fs plateaus
#   pairs distribution in freeze window
#   export submodule-patches if lib/rt64 edited
```

### Outcomes

- **V1:** next = why hangar-flight DLs / refuse path produce zero pairs (CIMG targets).
- **V2:** next = fullSync early-out / pair skip after s78 gate.
- **V3/V4:** fix VI_FULLSYNC trigger or FullSyncSeen lifetime.

## Do not

- Re-open S2 (syncs emitted but skipped) — s79 refuted.
- Chase UnhandledJump 0x0231 as primary present fix.
- Sampled `ROGUESQ_LOG_RUNNER` for single-task questions.
- Re-run fbgate3-class soak without the new decision log.
