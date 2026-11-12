# NEXT: M6 boot freeze, forced-state discriminator (CURRENT-TRUTH item 1)
HYPOTHESIS-ID: m6-boot-freeze-loop
State (s7191): static census done. Every live CF0 (0x80128CF0) receiver is balanced; the frozen dump state (retrace on CF0 full-send
list, valid 1, vflag 0, no receiver) needs a receiver that took a message, lost the CPU >=2 VIs before its `vflag=0`, and then
waited somewhere other than CF0. [stall-wait]/[stall-cf0] rows now ride in every [stall-dump] (default on, control PASS
scratch/s7191/ctl2.log). Fold scratch/agent/soak_queue/s7190_bootloop_d first (its SOAK-RESULTS line; rc=1 + FROZEN means read
the [stall-wait] IN rows: the receiver tid's IN mq + caller IS the second wait -> name it, fix the dependency).
If d is clean (55 boots, 0 freezes): build ONE forced-state arm instead of more identical hunts.
  Instrument: ROGUESQ_CF0_DELAY_TEST=<k> in osRecvMesg_recomp (src/main/upstream_compat.cpp, next to Rs64WaitScope): on the k-th
  CF0 recv that returns, before returning to guest code, block that guest thread ~40 ms on a private OSMesgQueue fed by
  osSetTimer (cooperative, so the retrace thread runs 2+ VIs with vflag still 1). That forces exactly the s6993 pre-state.
  Arms (one build, same run order): k=600 delay 40 ms; k=600 delay 100 ms; control k=0. 5 boots each via boot_freeze_hunt HUNT_ENV.
Hypotheses and outcomes:
  H-stale-heals: forced state appears in [stall-cf0] (S with fullq=8011CD28) and heals within a frame -> the freeze needs a second,
    independent wait; stop chasing CF0 and wait passively for [stall-wait] on a real recurrence.
  H-stale-freezes: forced state freezes the boot (FROZEN) -> reproduced on demand; [stall-wait] names the second wait; fix it
    (candidate: retrace's CF0 post is a doorbell, so a NOBLOCK post when full loses nothing; qualify with the same forced arm).
  H-no-form: the [stall-cf0] ring never shows retrace on fullq even with the delay -> the dump state forms another way; re-derive.
Positive control: the forced arm must print a [stall-cf0] S row with valid=1 at entry (the second post) or the arm is void.
