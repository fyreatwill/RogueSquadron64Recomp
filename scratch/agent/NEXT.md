# NEXT: identify the RT64 render-target source/layout writer
HYPOTHESIS-ID: g1d-widescreen

Session 6185's batched source/readback trace ran the preserved 4:3 control and
16:9/12 MB arm in one build and run. Both arms had 160 phase-4 joins, 1,440
route rows, and 400 copy traces. Control used source target/address
0xB90000, 512x447; wide used 0xB51E00, 796x447. For all 399 consecutive
transitions in both arms, center and outer hashes in the guest destination
matched the preceding host readback hashes. The changing wide central
rectangle is therefore already present at the RT64 readback source boundary;
there was no intervening guest write and no source-hash alternation in this
capture.

Competing hypotheses and discriminator:

- H-resolve-layout: the wide `RenderTarget` allocation, resize, resolve, or
  framebuffer view has a bad source extent/stride that creates the rectangle.
- H-rdp-producer: the wide RDP commands rasterize the rectangle into the RT64
  target before resolve.
- H-copy-layout: `copyToNative` uses a wrong row origin/extent or stale target
  for the wide target even though the target identity is correct.

Discriminator: add one phase-4, budgeted trace at the RT64 target/resolve path
that records the source target identity, texture/resolved-texture dimensions,
`copyToNative` rowWidth/rowStart/rowEnd, and the RDP draw/resolve ordering for
the same frame. A target or resolved texture whose dimensions/identity do not
match 796x448 selects H-resolve-layout; a correct target with a new
wide-only draw command covering the damaged center selects H-rdp-producer; a
correct target and command stream with a mismatched copy extent/origin selects
H-copy-layout. Keep the control and wide arms together and retain the 160-join
and 400-copy positive controls. Do not add a clamp/cull/skip until the writer
and legitimacy of the source pixels are named.

Exact work:

    ./submodule-patches/export.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6179_g1d_rdp_words.sh

Use the existing phase-4 route and dump artifacts; do not rerun the completed
source-hash census unchanged.
