# NEXT: capture valid phase-4 list contents on a corrupt wide frame
HYPOTHESIS-ID: g1d-widescreen

s6179 reproduced the corruption. Each arm had 160 phase-4 joins; every control
join was `512@0xB90000` and every wide join was only `796@0xB51E00`. The wide
guest dump at frame 500 has the corrupted central rectangle; the paired control
dump is coherent. This is a guest-frame defect, not presentation-only, but the
writer inside the valid list is not yet named.

Competing hypotheses and discriminator:

- H-list-command: the corrupt frame's valid phase-4 RDP words differ from a
  coherent frame in a way that identifies a game-side command/writer.
- H-guest-layout: RDP words match a coherent frame, but guest framebuffer
  writes/readback differ; the writer is a framebuffer layout or stride path.
- H-intermittent-layout: the same valid list and framebuffer path produce one
  clean and one corrupt frame; the defect is frame-specific.

Discriminator: add one phase-4, frame-gated dump of complete RDP command words
plus framebuffer write/readback metadata, then run both arms together. A
differing command stream selects H-list-command; identical commands with
differing guest writes selects H-guest-layout; identical commands and writes
with one clean and one corrupt frame selects H-intermittent-layout. Positive
controls are the phase-2/3 CIs and coherent control frame.

Run from the repo root:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6179_g1d_rdp_words.sh

Keep the retail default unchanged. Do not add a cull, skip, or width rewrite
until a writer and value legitimacy are established. Preserve the s6177 runner
fixes (`BUILD=$PWD/build`, `HOLD=90`, and the 240-second window).
