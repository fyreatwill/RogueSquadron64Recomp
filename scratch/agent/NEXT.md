# NEXT: attribute the first corrupt wide title framebuffer producer
HYPOTHESIS-ID: g1d-widescreen

s6172 narrowed the defect. A same-build paired run positively fired all
diagnostics: the control's first 512-wide title dump is coherent, while the
wide arm's matching 512-wide dump is horizontal scanline corruption. Both
arms logged the same early video-state dimensions; the wide arm already
rewrites 512x340 and 512x448, and its later phase-4 RDP route is coherent at
796 pixels. The concurrent harness did not satisfy the title gate on its
retries, so do not call the next run a clean endurance result.

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

Discriminator: add one regeneration-safe, phase-scoped join at the first
pre-phase-5 bad dump (not a run-lifetime counter), recording the framebuffer
dump ordinal, current VI origin/width, every CI width/address, RDP list start,
and the video-state call dimensions immediately before that frame. The same
single build must carry control and wide arms. A coherent guest dump plus bad
window selects H-early-rt64; a corrupt guest dump with a 320/640 or uncovered
buffer selects H-unrewritten-secondary; a corrupt guest dump whose source
display list is otherwise valid selects H-early-producer. The positive control
is the control's matching title dump and its route/join row in the same run.

Run from the repo root after implementing the bounded hook:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    # launch control and wide concurrently with the existing g1 coverage
    # harness, using OSMEM=12 and title origins 0x00790400/0x00752200;
    # arm ROGUESQ_LOG_VI_WRITERS=1, ROGUESQ_LOG_FB_ALLOC=1,
    # ROGUESQ_LOG_RDP_ROUTE=1, and ROGUESQ_FB_DUMP_VI=1.

Do not change retail defaults or add a cull/skip. If the writer is named,
make the smallest opt-in fix and rerun the paired capture in this iteration.
