# NEXT: distinguish wide guest-layout corruption from frame-specific readback
HYPOTHESIS-ID: g1d-widescreen

s6180 added a phase-4 complete RDP-word census and ran concurrent control/wide
arms. Both arms fired positive controls. The first 2,000 opcodes matched; only
the expected width-dependent scissor and SETCOLORIMAGE words differed, while the
wide guest framebuffer retained the central corruption. The retail oracle cannot
reach phase 4, so it supplies no independent target-phase witness.

Competing hypotheses and discriminator:

- H-guest-layout: identical command structure plus different per-frame guest
  framebuffer writes/readback metadata; the widened framebuffer or stride path
  is wrong.
- H-intermittent-layout: identical command and write/readback metadata on clean
  and corrupt frames; corruption depends on frame-specific producer state.
- H-hidden-width-pass: a later phase-4 submission not captured by the first
  2,000 words writes the damaged rectangle.

Discriminator: one build, both arms, capture a phase-4 frame-scoped census of
every submitted RDP range (not just the first 20,000 words), its CI/scissor
commands, and the raw guest framebuffer hash immediately before each VI dump.
Unexpected extra CI/scissor or a late command selects H-hidden-width-pass;
matching complete command streams with differing hashes selects H-guest-layout;
matching streams and hashes with clean/corrupt frame alternation selects
H-intermittent-layout. The control arm's coherent dump and phase-4 word rows are
the positive controls.

Run after instrumentation:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6181_g1d_frame_census.sh

Keep retail defaults unchanged. Do not add a skip, cull, or width rewrite until
the writer and legitimacy of the corrupt value are established.
