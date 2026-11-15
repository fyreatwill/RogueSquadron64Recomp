# NEXT (s7379)
HYPOTHESIS-ID: rt64-resize-destroy-vs-present

s7378 closed class AU (SharedQueueResources fields; tools/s7378_shared_res_census.py --check rc 0). It surfaced AU2.

Work unit: class AU2. WorkloadQueue::threadConfigurationUpdate (lib/rt64/src/hle/rt64_workload_queue.cpp ~331-349), on
fbConfigChanged || sizeChanged, waits presented>=available, then under managerMutex ONLY calls renderFramebufferManager->destroyAll(),
targetManager.destroyAll(), fbManager.destroyAllTileCopies(). The present thread (s7377) holds workloadMutex (not managerMutex) from
performOperations through its GPU pass and dereferences RenderTarget* from targetManager. A resize (fullscreen toggle, window move,
ASPECT=auto) makes the present thread set swapChainSizeChanged in threadLoop, then the workload tears down on its next config update
while the next present may be inside threadPresent.
Hypotheses: H-ordered (some handoff already keeps the next threadPresent out: e.g. waitForWorkloadId pairing means the present that
could race waits for this very workload; prove it from the id chain), H-race (present uses a destroyed target: fix = take
workloadMutex around the teardown, lock order configurationMutex -> managerMutex -> workloadMutex must be checked against every
present/workload path, or do the teardown inside threadRenderFrame's workloadMutex scope), H-gfx (State's own targetManager is a
separate object: confirm the destroyed managers are the shared ones).
Discriminator: (1) a lock-order table of every managerMutex/workloadMutex/configurationMutex/interpolatedMutex acquisition with what is
held (extend s7378 census lock tracker); (2) a TSan arm with a resize stress: env knob forcing a swap-chain resize every N s
(SDL_SetWindowSize alternating, or ROGUESQ_FULLSCREEN toggle) during flight, positive control = s7354 CTL + the resize count in log.
Gate if a fix lands: rebuild, smoke `env SECS=260 zsh scratch/s7326/run.zsh s7379_dd8 ''` + old arm, TSan
`zsh tools/build_tsan.sh` + scratch/s7378/tsan_run.zsh copied to scratch/s7379 (480 s), `python3 tools/s7354_tsan_report.py` rc 0.
