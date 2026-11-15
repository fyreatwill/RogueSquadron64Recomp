# NEXT (s7378)
HYPOTHESIS-ID: rt64-shared-resources-census

s7377 closed class AT (present-thread map reads; workloadMutex now held for the whole present lookup + GPU pass,
ROGUESQ_S7377_EARLYLOCK=0 = old). It showed a whole struct is shared across three threads with mixed guards: AT only covered the maps.

Work unit: class AU. Census every field of RT64::SharedQueueResources (lib/rt64/src/hle/rt64_shared_queue_resources.h:
swapChainWidth/Height/Rate, resolutionScale, targetRate, userConfig/enhancementConfig/emulatorConfig, the *Changed flags,
newConfigValidated, viOriginalRate, colorImageAddressSet, interpolatedColorTargets, interpolatedFrames[2].{presented,available,count,
skipped}, interpolatedFramesIndex) across ALL of lib/rt64/src and src/ (grep `sharedResources->` and `ext.sharedResources->`).
One tool tools/s7378_shared_res_census.py: per access file:line, field, R/W, thread (State=gfx thread, WorkloadQueue=rt64 render,
PresentQueue=present, Application/main=main; reuse the s7375 walker's file->thread map), mutex held (configurationMutex /
managerMutex / interpolatedMutex / workloadMutex, lexical like s7377), and a --check vs a reviewed TSV.
Per field verdict: GUARDED (one mutex on every write and cross-thread read) / BENIGN (aligned word hint, document) / RACE (fix).
Known leads: present_queue reads frameCounters.count (written workload_queue.cpp:1251, no lock) and interpolatedFramesIndex unlocked;
targetRate/viOriginalRate written by the workload thread - check under which lock.
Hypotheses: H-guarded (every cross-thread field already sits under configurationMutex/interpolatedMutex: 0 fixes),
H-hint-only (unguarded fields are all aligned single-word hints: BENIGN rows only), H-race (a multi-word field, e.g. resolutionScale
float2 or a config struct copy, is read torn across threads: fix with the existing mutex).
Positive control: the tool must mark swapChainRate writes (setSwapChainRate) GUARDED by configurationMutex and the s7377 snapshot of
colorImageAddressVector MGR-LOCKED; s7354 TSan report's swapChainRate BENIGN row must match a census row.
Gate if a fix lands: rebuild, smoke `env SECS=260 zsh scratch/s7326/run.zsh s7378_dd8 ''` + old arm, TSan `zsh tools/build_tsan.sh`
+ copy scratch/s7377/tsan_run.zsh to scratch/s7378 (480 s, foreground), `python3 tools/s7354_tsan_report.py ...` rc 0, CTL fires.
