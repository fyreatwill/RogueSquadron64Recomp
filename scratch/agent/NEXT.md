# NEXT work unit — discriminate vi-commit absence vs. slot-pool exhaustion blocking hangar

HYPOTHESIS-ID: m5-step1-slot-status-consumer

Session 3328 found the port image arm stuck at VI-1024 with two candidate blockers:
(a) the M5 route vi-commit for 1024 is absent — all 7,796 phase-4 route-prepare
    rows show commit_width=640/key_match=0;
(b) the audio slot-pool count grows monotonically 4→1578 with no slot freeing.

These must be discriminated in one instrument before adding a slot/status probe.
Do not add a behavior change or mitigation.

## Competing hypotheses

- `H-VICommitAbsent`: the M5 route vi-commit for VI-1024 never fires because the
  port's applyPendingViChanges / viRetraceHandlerThread does not call the route
  commit path during the 1024 transition; the slot-pool growth is downstream.
- `H-SlotPoolExhausted`: the audio slot pool leaks from the title phase onward
  (1578 slots, no freeing), causing the game to stall in a waitForAnyAudioSlot
  spin before advancing to hangar; the vi-commit absence is a consequence.
- `H-BothIndependent`: vi-commit absence and slot-pool exhaustion are independent
  bugs; the game is stuck at 1024 because of whichever fires first.
- `H-PortHangarReachable`: the game can reach hangar 512 with corrected autopilot
  timing or a longer watchdog; the blocker is purely the autopilot schedule.

## Discriminator

Design ONE instrument covering all four discriminators in one build/run:

1. Log the M5 vi-commit callers in the port (add `ROGUESQ_LOG_M5_VI_COMMIT=1` or
   read the existing route-transition log more carefully): does a vi-commit for
   1024 ever fire, or is the vi-commit path not reached during 1024?
2. Log the slot-pool free path: does any slot get freed after being allocated in
   the title phase? If slot count is strictly increasing, slot freeing is broken.
3. Test autopilot timing: extend the schedule to 60 s post-1024 (60:start,
   90:start, 120:start) to rule out `H-PortHangarReachable` without a rebuild.

The discriminating outcome:
- vi-commit for 1024 fires → H-VICommitAbsent refuted; focus on slot-pool.
- slot-pool count plateaus or decreases → H-SlotPoolExhausted refuted; focus on
  vi-commit.
- vi-commit absent AND slot-pool strictly increasing AND longer autopilot also
  fails → both are real blockers; address vi-commit first (upstream).
- longer autopilot reaches 512 → H-PortHangarReachable; run the slot/status
  qualification with that schedule.

## Exact starting checks

```sh
# Check what the vi-commit path logs
grep 'm5-route-transition.*vi-commit' scratch/agent/s3327_m5_slot_status_port/image.log
# Check the slot-pool count trend (done: 4→1578 monotonically)
grep 'slot-pool count' scratch/agent/s3327_m5_slot_status_port/image.log | tail -20
# Check if any existing slot-free logging exists
grep -n 'slot.*free\|free.*slot\|ROGUESQ_LOG_M5_SLOT' src/main/main.cpp | head -20
```

If the source has a slot-free logging flag, enable it in the script.
If the vi-commit log already shows no 1024 commit (confirmed in s3328), then
the next instrument should add a slot-free probe and extend the autopilot schedule.

Use the existing Debug binary (no rebuild needed unless new probes require it).
Watchdog: 240 s. Phase-gate on VI-1024. SIGKILL. No behavior change.
