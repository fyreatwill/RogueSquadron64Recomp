# NEXT: isolate the RT64 readback source region for the phase-4 defect
HYPOTHESIS-ID: g1d-widescreen

Session 6184 result: the phase-4 `copyToRAM` trace fired 400 times in each
arm. Control copied 512x448 into guest physical 0xB90000; wide copied 796x448
into 0xB51E00. In both arms, all 399 consecutive destination `before` hashes
equalled the preceding host readback hash. The route positive controls remained
160 joins and 1,440 route rows per arm. This selects the readback-copy boundary
as the immediate writer of the changing framebuffer bytes, but does not name
the RT64 render/readback source of the wide central rectangle.

Competing hypotheses and discriminator:

- H-rt64-source-region: an RT64 source-target/row layout produces the damaged
  central rectangle only for the 796-wide target.
- H-guest-layout: the guest framebuffer is already wrong before the RT64 copy
  boundary on a fresh destination range.
- H-intermittent-readback: source-region hashes alternate between clean and
  corrupt phase-4 frames while CI/route metadata stays fixed.

Discriminator: add one phase-scoped trace at the RT64 `copyToNative`/readback
source boundary recording source target identity, rowStart/rowEnd, rowWidth,
and bounded hashes for central damaged columns versus outer columns. Compare
those source hashes with the paired guest destination ranges. A wide-only
anomalous source central hash selects H-rt64-source-region; an anomalous fresh
destination before copy selects H-guest-layout; alternating source hashes with
fixed CI/route selects H-intermittent-readback. Keep both arms in one build/run
and retain the phase-4 route positive controls. Do not add a skip or clamp until
the writer and value legitimacy are named.

Build/run after adding the source-region trace:

    ./submodule-patches/export.sh
    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6179_g1d_rdp_words.sh

Preserve the existing 4:3 control and 16:9/12 MB wide recipes. Do not rerun
the completed census unchanged or widen the mission route until this
source-region discriminator is run.
