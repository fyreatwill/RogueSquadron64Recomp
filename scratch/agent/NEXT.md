# NEXT work unit (s1975) — diagnose frame-freeze at update_screen #2176

HYPOTHESIS-ID: hangar-frame-freeze

## What s1974 settled

Two mission-entry arms ran (extra Starts + A button presses):
- SDL key delivery fails after Start #6 (31s from boot) — macOS focus issue.
- 2 Starts reached the hangar (pad-host n=5, n=6) but no phase change.
- H-start-enters-mission and H-needs-confirm-key (A) both REFUTED.

anyAudioSlotActive spin class fully enumerated (10 sites) and gated.
Census probe: none of the 6 new ROGUESQ_SPIN_YIELD sites fired in 120s.

Frame-counter `fs` freezes at update_screen #2176 in every run (~40s after hangar
entry). Pattern: `pq.wc=0 wq.wc=2` — two threads blocked waiting for a message
that never arrives. The VI is alive (update_screen continues). This is NOT an
anyAudioSlotActive spin. It is a different blocking mechanism in the hangar state
machine.

## Competing hypotheses and discriminator

- H-vi-queue-full: the host VI message queue fills up (producer-side overflow)
  and subsequent retrace messages are dropped. The game's osRecvMesg consumer
  starves because no messages arrive after the queue fills. Evidence for: this
  is the same family as the s1939-s1941 title-screen stall, just a different
  site/phase.
- H-game-recv-blocks: the hangar state machine calls osRecvMesg on a queue that
  never receives (a different queue from the VI retrace one). The VI queue is fine
  but the game thread is waiting on something else.
- H-yield-missing: an unidentified spin (not anyAudioSlotActive) in the hangar
  state machine occupies the CPU and prevents the VI consumer from draining,
  similar to how menuInput spin prevented VI drain in the title screen.

Discriminator: does ROGUESQ_LOG_VI_RECV or the existing vi-enq/vi-deq/recv1
instrumentation show the VI retrace queue state at update_screen #2176? If vi-enq
count increases but vi-deq stops, H-vi-queue-full is supported. If both stop,
H-game-recv-blocks is more likely. If neither changed but the game is CPU-bound,
H-yield-missing is supported.

## Exact commands

Check which recv/enq/deq log flags are available:
```sh
grep -r 'vi-enq\|vi-deq\|recv1\|LOG_VI' /Users/williambuckley/Documents/Tools/RogueSquadron64Recomp/src/ 2>/dev/null | head -20
```

Run a probe with vi-recv-path logging enabled (re-use existing flags from s1940):
```sh
mkdir -p scratch/agent/s1975_freeze_probe
env ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 \
ROGUESQ_STUB_MISSING_FUNCS=1 \
ROGUESQ_LOG_VI_RECV_PATH=1 \
PROBE_PHASE_WIDTH=512 PROBE_PHASE_TIMEOUT=60 PROBE_LEAVE_OK=1 \
PROBE_KEYS='6:start 11:start 16:start 21:start 26:start 31:start 36:start 41:start 46:start 51:start 56:start' \
zsh tools/probe.sh scratch/agent/s1975_freeze_probe 120 2
```

Check the vi-recv state around the freeze (near update_screen #2176):
```sh
grep -E 'vi-enq|vi-deq|vi-recv|recv1' scratch/agent/s1975_freeze_probe/run.log | tail -30
```

If vi-enq/vi-deq logging is not available via env flags, check the s1940 probe setup
in PORTING-STATE.md and replicate the relevant instrumentation.

## Iron rules for this unit

- Do NOT add a mitigation or yield without naming the root cause. The freeze is
  NOT an anyAudioSlotActive spin — don't add more spin gates without evidence.
- Positive control: verify the known spins (menuInit, menuInput, audioDrain) still
  fire in the same run (they should appear before #2176).
- If the recv-path log is not available, check existing ROGUESQ_ env flags to find
  what can observe VI message queue state, then run a census first.
