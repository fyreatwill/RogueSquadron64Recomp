# NEXT: distinguish the wide RDP producer from RT64 resolve layout
HYPOTHESIS-ID: g1d-widescreen

Session 6188 completed the corrected paired run. The 600-second runner reached
phase 4 in both arms: 160 joins, 400 full-frame copy traces, and 80,000 bounded
`[g1d-word]` records per arm. The source targets and copy extents were correct
(`0xB90000`, 512x447, control; `0xB51E00`, 796x447, wide), so the first
240-second attempt was discarded as a phase-3 route miss.

Competing hypotheses:

- H-rdp-producer: wide-only RDP commands rasterize the central rectangle.
- H-resolve-layout: RT64 allocates/resolves a target or resolved texture with a
  wrong extent or stale view despite the correct source identity reported by
  copyToRAM.
- H-copy-layout: copyToNative uses a wrong row origin/extent or stale target;
  current full-row, matching-width evidence weakens this.

Discriminator: use the captured phase-4 records to compare the first complete
control/wide RDP command stream at matched frame ordinals, classifying every
SETSCISSOR, SETCOLORIMAGE, TEXRECT/TEXRECTFLIP, and draw command that covers
the central rectangle; pair that with an explicit RT64 target/resolve texture
dimension log for the same frame. A wide-only central-covering command selects
H-rdp-producer. A correct command stream but mismatched target/resolved
dimensions selects H-resolve-layout. Correct dimensions and no producer
difference leave only a copy/readback ordering defect, which must then be
traced before any mitigation.

Exact next work unit: add the target/resolve dimension fields and the
central-covering command classification to the existing phase-4 instrument in
one build, then run the paired route:

    ./submodule-patches/export.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6179_g1d_rdp_words.sh

Retain the route positive controls (160 joins and 400 copies per arm). Do not
add a clamp, cull, skip, or other mitigation until the writer and legitimacy
of the wide pixels are named.
