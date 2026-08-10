# s591 thr-11 pipeline (item -360)

## Recipe
`PROBE_MODE=start_only HOLD_S=90` +
`ROGUESQ_FORCE_CASE6_START=5 ROGUESQ_FS_PIPE_INJECT=1` +
`LOG_DL_SYNC LOG_FS_SLOT LOG_HANGARBAY_ENTRY LOG_RDP_FULLSYNC LOG_AUDIO_DRAIN LOG_WAITFORSLOT_GUARD`

Died hold-iter 38; CRASH `trackResourceListWithMappingTables+1228` / `last-guest-pc=0x80065e94`.

## Cross-run thr-11 create→destroy (runner task #)

| run | path | thr-11 Δtasks | thr-11 destroy | post-exit sec4 | thr-12 | sec2 | recovery @0x76B768 |
|-----|------|---------------|----------------|----------------|--------|------|---------------------|
| s577 | natural | **266** | yes | yes | yes | yes | n/a (pre-inject) |
| s589 | force+inject HOLD90 | **2851** | yes | yes | no (crash) | no | **×1988** |
| s590 | case6+inject HOLD60 | never | no | no | no | no | ×3853 then late crash before destroy |
| s591 | case6+inject HOLD90 | never | no | no | no | no | **0** (failed recovery) |

s590 had recovery but thr-11 still alive at crash (findLookupEntry); s591 no recovery, thr-11 alive at crash (0x80065e94).

## Hypotheses (H12)

| H | Verdict | Evidence |
|---|---------|----------|
| H12a thr-11 blocks on mesg forever | **REFUTED as primary** | thr-11 is infinite `recvServiceMessage` loop; destroy is external `stopSaveServiceWorker`/`osDestroyThread`. Audio drain in thr-11 window: none after thr-11 create (s591: last `audio-drain-exit` is thr-10 teardown, iters=1). |
| H12b thr-11 guest crashes before overlay DMA | **partial (noise)** | s590/s591 die with thr-11 still live on known intermittent families; s589 thr-11 completes without thr-11 fault. |
| H12c thr-11 destroy only after RDP/FULL_SYNC healthy window | **SUPPORTED** | Failed recovery (s591: inject n=26 E7 only, trailing `syncs=0`×2086, 0×76B768, fs max 4980) → no thr-11 destroy / no sec4. Successful recovery (s589) → thr-11 destroy + sec4. Natural short thr-11 life (266 tasks) while syncs live. |
| H12d thr-12 needs thr-11 epilogue flag beyond sec4 | **untested** | Only s589 reached post-exit sec4; crashed in `cinematicLoopBody→initSceneForMission→coalesceFreeHeapBlocks` before thr-12 create. |

## Recharacterization

thr-11 is **not** a progress worker that "finishes work." It is a long-lived save service. Section-4 load and thr-11 destroy are co-events of the **scene transition** that only runs after the post-exit cutscene advances. FULL_SYNC starvation freezes that cutscene; thr-11 staying alive is a *symptom* of the freeze, not an independent message-wait bug.

Pipeline remains: thr-11 destroy ↔ sec4 → thr-12 (hud) → sec2. Gate after inject+recovery: survive `initSceneForMission` long enough for thr-12.

## Positive controls (same run)
- `[case6-force-start] n=5` fired
- hangar-sel + state 6→8
- VI 640 origin 0x6A2900
- fs-pipe-inject n=1..26 (E7 sticky cell) then stopped
- audio-drain enter/exit paired (iters=1) at pre-thr-11 service restarts

## Next
Prefer recovery-reliable force hold that reproduces s589 thr-11 destroy+sec4, then measure thr-12 create vs initSceneForMission crash — do not re-open thr-11 as a recv-block.
