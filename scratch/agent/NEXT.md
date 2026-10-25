# RESUME: census every phase-4 title CI before attributing the corrupt producer
HYPOTHESIS-ID: g1d-widescreen

s6176 reached phase-4 frames 417-488 in the wide arm. After fixing the dump
stride, the guest image is coherent around a horizontally corrupted central
rectangle. The current join reports only the last CI, so it cannot say whether
an earlier secondary pass wrote the bad region.

Competing hypotheses and discriminator:

- H-secondary: a phase-4 frame contains an earlier 320/512/640 CI or a second
  framebuffer write before the final 796 CI; its width/address and list range
  identify the missed pass.
- H-producer: every phase-4 CI is 796-wide and targets `0xB51E00`, yet the
  guest dump still has the central rectangle; the remaining writer is a game
  asset/layout producer inside that valid list.
- H-rt64: all guest bytes are coherent but the activated window is corrupt.
  This is now disfavored by the fixed dump, and is closed if the same-frame
  guest dump remains corrupted while the route census is complete.

Discriminator: extend the existing join in one build to retain every CI
width/address/list range per phase-4 frame, not only the last CI. Run paired
control and wide arms with `FBD_EVERY_V=1`, `ROGUESQ_FB_WIDTH=796` on wide,
`ROGUESQ_FB_DUMP_VI=1`, `ROGUESQ_LOG_RDP_ROUTE=1`, and the existing writer and
allocation logs. A 320/512/640 or alternate-address CI before a corrupt wide
dump selects H-secondary; an all-796 census with a corrupt guest dump selects
H-producer; coherent guest bytes plus only a bad window selects H-rt64. The
control arm's phase-4 dump and full CI census are the positive control in the
same run.

Resume from the repo root:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    # launch control and wide concurrently with the existing g1 coverage
    # harness, using OSMEM=12 and title origins 0x00790400/0x00752200;
    # set FBD_EVERY_V=1, ROGUESQ_FB_WIDTH=796 on wide, and arm
    # ROGUESQ_LOG_VI_WRITERS=1, ROGUESQ_LOG_FB_ALLOC=1,
    # ROGUESQ_LOG_RDP_ROUTE=1, and ROGUESQ_FB_DUMP_VI=1.

Do not change retail defaults or add a cull/skip. If the writer is named,
make the smallest opt-in fix and rerun the paired capture in this iteration.
