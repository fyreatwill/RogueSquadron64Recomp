# NEXT (s7541)
HYPOTHESIS-ID: class-gb-device-done-before-read

s7540 landed ROGUESQ_RDP_NODRAIN=3 (reads-wait; PORTING-STATE s7540): every texture-source load now precedes dp_complete (0 late
loads L1/L4/L12, same-run nodrain 43-196 torn). Still AFTER the post under =3 (rt64_state.cpp State::fullSync, after the
rs64_s7540_reads_done() call): the final renderAndSynchronize -> (1) fb read-ins workload.fbStorage.store(..., &RDRAM[storageAddress],
readFbBytes) (~2685/2783, a guest-RAM READ), (2) copyNativeToRAM writebacks (~2957/2975/3035/3040, RDRAM WRITES that can clobber a
guest write made after the post), (3) framebufferManager.hashTracking(RDRAM) (~3171, READ: a guest write to a tracked fb after the post
changes what RT64 decides). First check the soak result s7540_rwait_cost in SOAK-RESULTS (fold fps per arm, g1e_level_fps.py).

Work unit: ONE instrument over all three, ONE build, same-run arms via NODRAIN=4 (as=2 drained = control where all happen before
the post; as=4 reads-wait = test). Reuse the s7539 snapshot (gb::at_exit snaps [0,16 MB) at the post):
- read-ins / hashTracking: compare the read span vs the task's snapshot (like rs64_s7539_load) -> diff bytes = guest wrote after post.
- writebacks: before copyNativeToRAM, compare the target span vs the snapshot: bytes the guest changed after the post that the
  writeback is about to overwrite (clobber count), and count spans/bytes written after the post at all.
- Controls: planted flip as in s7539; real-world = the same spans vs the older snapshot; for writebacks, a drained-task (as=2)
  clobber count must be 0 by construction (positive structural control) and a planted guest-write (flip a snapshot byte) caught.
Hypotheses / outcomes:
- H-none: post-signal read-ins/writebacks ~0 (s7391: the guest never loads a live colour image) -> =3 is complete; close GB.
- H-readin-torn: read-in spans differ from the snapshot -> extend reads_wait to the end of the last read-in (signal after the
  last fbStorage.store) and re-measure cost.
- H-clobber: writebacks overwrite post-signal guest writes -> name the guest writer (ROGUESQ_STORE_WATCH on that span) and decide
  whether the writeback must precede the post.
Battery note: on battery (clk ~1.5) timing arms need ALLOW_SLOW=1 and are only comparable within the same run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
