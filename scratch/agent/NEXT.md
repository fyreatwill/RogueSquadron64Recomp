# NEXT work unit — M3: diagnose hangar-flight createTileCopyRecord death

s76: start_only leave works; 60s hold fails. Process aborts ~12s post-leave in
`FramebufferManager::createTileCopyRecord` (`assert(fbIt != framebuffers.end())`,
`lib/rt64/src/hle/rt64_framebuffer_manager.cpp:190`) after wild last-drawn (w=4007)
and `fs` freeze at 3364. Stick never fired. Detail: `HOLD60_ANALYSIS.md`.

## Competing hypotheses

| ID | Claim | If true, we will see… |
|----|--------|------------------------|
| D1 | Assert is hit only for garbage FB addresses (wild last-drawn / OOB CIMG) | createTileCopy log: missing-fb ops all have w>1280 or addr outside known pair; good 512-wide ops always find fbIt |
| D2 | Assert is a race / storage lifetime: FB was registered then dropped mid-workload | missing-fb on legitimate 512/0x6AB400 addresses that earlier ops in the same task found |
| D3 | Trailing `syncs=0` tasks starve fullSync so present state desyncs → assert | post-leave: first syncs=0 task coincides with fs plateau; forcing VI_FULLSYNC path (already default-on) still leaves syncs=0 population |
| D4 | Same root as keys2 MetalFramebuffer SIGSEGV (resource create after bad FB key) | same last-drawn wild cluster precedes both death classes; fixing garbage FB registration stops both |

## Discriminating measurement (one build, one soak)

Batch into RT64 (or existing last-drawn path) **scoped after hangar-flight leave**
(gate on first post-leave content or a sticky "in_flight" after probe Start):

1. At createTileCopyRecord entry: log addr, width, found/missing (rate-limit but
   **must log every missing** + first N found as positive control).
2. Keep LOG_RUNNER_ALL + thr-resume + ost-wb (already on).
3. Re-run start_only with HOLD_S=20 (enough to hit death window; no stick needed).

```bash
# after instrument + cmake --build build -j8:
env PROBE_MODE=start_only HOLD_S=20 zsh scratch/s73_post_a_scene/run_mission_keys.sh tilecopy 0 12
# offline:
#   grep -c '\[tilecopy\].*found=1' / found=0  — control: found>0 same run
#   missing rows: all wild? any legitimate 512?
#   thr-resume bad still 0; death site still assert or skipped
```

### Outcomes

- **D1:** convert missing-fb to skip (or extend writeback-style width gate upstream so
  garbage never becomes a FramebufferOperation). Re-soak for 60s hold.
- **D2:** lifetime/registration bug — different fix in FramebufferStorage.
- **D3:** investigate why hangar-flight DLs stop emitting SYNC_FULL (runner hist).
- **D4 supported by shared pre-pattern:** prioritize filtering wild last-drawn/CIMG
  before either crash site.

## Do not

- Re-isolate Start leave path (closed s75/s76).
- Re-open s72 OSThread writeback unless thr-resume bad=1.
- Cross-run A/B on animating hangar-flight visuals.
- Claim a skip-assert fix without same-run found=1 control.
