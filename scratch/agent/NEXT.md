# NEXT: attribute the first corrupt wide title framebuffer producer
HYPOTHESIS-ID: g1d-widescreen

s6173 validated the new join but did not reproduce the corruption: at phase 4,
frame 500, control joined VI 1024/title 0xB90400/CI 512 and wide joined VI
1024/title 0xB52200/CI 796; the wide dump was coherent by row uniqueness. The
next run must capture every title frame so an intermittent first-bad frame is
not hidden by the old every-500 dump interval. This remains diagnostic, not
endurance.

Competing hypotheses and discriminator:

- H-early-producer: an earlier title display-list or asset producer still
  assumes a 512-wide stride/address. A first-bad framebuffer join keyed by
  phase, CI address, VI origin, and source display-list identifies it; a
  controlled opt-in rewrite of that producer makes the first title dump
  coherent.
- H-early-rt64: the guest RDP/VI join and guest dump are coherent, but RT64's
  readback/present interpretation corrupts only the window. This is proven
  only if guest bytes/hash are coherent while an activated-window capture is
  corrupt; it is refuted if the guest dump is already scanline-corrupt.
- H-unrewritten-secondary: the bad dump is from a 320/640 secondary pass or
  another framebuffer not covered by the current 512-dimension hook. The
  first bad dump's CI width/address and the immediately preceding video-state
  call distinguish this from an asset producer.

Discriminator: rerun the same build with `FBD_EVERY_V=1` and compare every
phase-4 title dump, its `[g1d-join]` row, and the preceding `[rdp-route]` CI
records. A coherent guest dump plus bad window selects H-early-rt64; a corrupt
guest dump with a 320/640 or uncovered buffer selects H-unrewritten-secondary;
a corrupt guest dump whose source display list is otherwise valid selects
H-early-producer. If all per-frame guest dumps are coherent, the corruption is
intermittent and the next lead is the first frame whose CI/list join changes,
not a width patch. The positive control is the control arm's matching phase-4
frame and join row in the same run.

Run from the repo root after implementing the bounded hook:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    # launch control and wide concurrently with the existing g1 coverage
    # harness, using OSMEM=12 and title origins 0x00790400/0x00752200;
    # set FBD_EVERY_V=1 and arm ROGUESQ_LOG_VI_WRITERS=1,
    # ROGUESQ_LOG_FB_ALLOC=1, ROGUESQ_LOG_RDP_ROUTE=1, and
    # ROGUESQ_FB_DUMP_VI=1.

Do not change retail defaults or add a cull/skip. If the writer is named,
make the smallest opt-in fix and rerun the paired capture in this iteration.
