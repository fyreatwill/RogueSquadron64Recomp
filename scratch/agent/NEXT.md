# NEXT: census title phases 2-3 for the intermittent wide title corruption
HYPOTHESIS-ID: g1d-widescreen

s6177 closed the hidden-secondary hypothesis for phase 4: all 160 sampled
phase-4 wide frames had exactly three repeated `796@0xB51E00` submissions and
no alternate CI. The wide frame-408 guest dump was coherent in this capture,
so the s6172 corruption remains intermittent.

Competing hypotheses and discriminator:

- H-early-phase: the corrupt title frame is produced in phase 2 or 3, before
  the phase-4 stream; a complete per-swap census there will show a non-796 CI
  or alternate target associated with the bad dump.
- H-phase4-producer: phases 2-3 are also width-consistent, and a wide guest
  dump is corrupt while every CI is `796@0xB51E00`; the remaining writer is
  inside that valid game list.
- H-intermittent-layout: all sampled CIs are width-consistent and guest dumps
  are coherent, so the defect is frame-specific and needs a capture that
  catches the corruption before attribution.

Discriminator: use the existing per-frame CI census and per-VI dump in one
paired control/wide run, but classify phases 2 and 3 separately. A non-796 or
alternate-address CI selects H-early-phase; a corrupt guest dump with only
796 CIs selects H-phase4-producer; coherent dumps with only 796 CIs selects
H-intermittent-layout. Positive controls are the 842 join rows and the control
phase-2/3 dumps in the same run.

Run from the repo root:

    cmake --build build --config Debug --target RogueSquadron64Recomp -j4
    zsh scratch/agent/s6177_g1d_ci_census.sh

Keep the retail default unchanged. Do not add a cull or skip until a writer
and value legitimacy are established.
