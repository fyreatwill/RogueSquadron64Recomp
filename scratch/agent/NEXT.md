# NEXT: resume the G1d complete phase-4 frame census
HYPOTHESIS-ID: g1d-widescreen

RESUME checkpoint (Session 6181): do not rerun the prior probe unchanged. The
last run established that the first 2,000 phase-4 RDP words match between 4:3
control and 16:9 wide apart from expected scissor/SETCOLORIMAGE fields, while
the wide guest framebuffer can still be corrupt. Artifacts are the committed
`src/main/rt64_render_context.cpp` diagnostic and prior outputs under
`scratch/agent/soak_results/s6179/`.

Competing hypotheses and discriminator:

- H-hidden-width-pass: a later command range or CI/scissor pass writes the
  damaged region. A late unexpected CI/scissor selects it.
- H-guest-layout: the complete command stream matches but the wide guest
  framebuffer hash differs before VI dump. That selects a guest write/stride
  or layout defect.
- H-intermittent-layout: complete streams and framebuffer metadata match while
  clean and corrupt frames alternate. That selects frame-specific state.

Restore/extend the census so it records every phase-4 submitted RDP range,
every CI/scissor command, and the raw guest framebuffer hash immediately before
each VI dump, then run both arms:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6179_g1d_rdp_words.sh

Preserve the existing 4:3 control and 16:9/12 MB wide recipes and positive
controls. Do not add a skip, cull, or width rewrite until the writer and value
legitimacy are established.
