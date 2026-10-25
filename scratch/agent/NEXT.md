# NEXT: reproduce the intermittent wide title corruption with the phase-4 census
HYPOTHESIS-ID: g1d-widescreen

s6178 ran the corrected paired census successfully. The control and wide arms
had identical phase-2/3 CI targets (320-wide phase 2; 640-wide phase 3), while
phase 4 was consistently 512-wide control versus 796-wide wide. The bad wide
guest framebuffer did not recur, so no writer or mitigation is justified.

Competing hypotheses and discriminator:

- H-in-list-producer: a corrupt wide guest dump recurs while the complete
  phase-4 census remains only `796@0xB51E00`; the defect is inside the valid
  game-produced list or its guest framebuffer writes.
- H-intermittent-layout: another clean wide run has only the expected CIs and
  coherent guest dumps; the s6172 corruption is frame-specific and needs a
  producer/layout capture that catches the event.
- H-early-phase: an unexpected CI or target appears before phase 4 and is
  temporally associated with a later corrupt dump; this remains possible only
  if a future run catches such a frame, since s6178 found no aspect-specific
  phase-2/3 target.

Discriminator: rerun the existing paired census unchanged. A corrupt wide
  dump with only `796@0xB51E00` selects H-in-list-producer; a clean run with
  the same CI census strengthens H-intermittent-layout; an alternate early CI
  selects H-early-phase. Positive controls are the 842 joins and phase-2/3
  control dumps in the same run.

Run from the repo root:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6177_g1d_ci_census.sh

Keep the retail default unchanged. Do not add a cull, skip, or width rewrite
until a writer and value legitimacy are established.
