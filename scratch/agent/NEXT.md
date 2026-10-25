# NEXT: attribute the phase-4 guest framebuffer write/layout
HYPOTHESIS-ID: g1d-widescreen

Session 6182 result: the corrected 12 MB-origin run reached phase 4 in both
arms. Each arm had 160 joined frames and 1,440 phase-4 route records. Control
was uniformly CI 512 at 0xB90000; wide was uniformly CI 796 at 0xB51E00,
with matching scissor streams and no hidden late CI. Wide framebuffer hashes
still differed. The run used `MISSION_RE=ZZZ`, so its `nomission` status is
expected and is not a mission failure. Logs are in
`scratch/agent/m6/g1_lvl1_{ctl,wide}/run.log`.

Competing hypotheses and discriminator:

- H-guest-layout (leading): a write/stride trace names a guest PC or row/byte
  range that targets the damaged central rectangle only in the wide arm.
- H-intermittent-layout: the same write ranges and PC sequence occur in clean
  and corrupt phase-4 frames; this selects frame-specific state instead.
- H-renderer-readback: guest writes are identical, but the first host readback
  bytes differ before VI. This selects RT64 readback/layout, not a guest writer.

Discriminator: arm one phase-4 write/read trace in both arms, keyed by the
joined framebuffer address and VI frame. The positive controls are the existing
phase-4 route rows and the known changing framebuffer hash; an observed write
to the central damaged range must fire. Compare writer PC, destination offset,
row stride, and first host readback bytes. Do not add a skip or clamp until the
writer and value legitimacy are named.

First inspect the existing memory-write/HWBP path and the RDRAM readback hook;
if neither can cover a row range, add one phase-scoped bounded trace in the
existing runtime path. Then build and run both arms with the corrected 12 MB
origins:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6179_g1d_rdp_words.sh

Preserve the existing 4:3 control and 16:9/12 MB wide recipes and positive
controls. Do not rerun the completed census unchanged and do not widen the
mission route until this writer/readback discriminator is designed.
