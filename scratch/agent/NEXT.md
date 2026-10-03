# Next work unit: paired target-phase retail/port route parity

HYPOTHESIS-ID: m5-target-phase-route-parity

The standalone s3822 image arm reached title 1024 and hangar 512 with all
controls. Run one same-build paired retail oracle plus port image capture using
the validated route, so retail and port source spans are measured in the same
target-phase qualification.

Competing hypotheses and discriminator:

- H1: both arms reach target phase and their exact source spans match
  (`FNV=0x762B22A5`, `nz=0`); route parity is selected.
- H2: both reach target phase with complete controls, but source-span payloads
  differ; the remaining boundary is a real route/value mismatch.
- H3: either arm lacks a target phase or positive control, so parity is
  unevaluable and the recipe is coverage-invalid.

The discriminator is one same-build paired run. Build with:

    cmake --build build --config Debug --target RogueSquadron64Recomp

Then run a self-contained paired driver, based on the validated s3821 route,
from the repository root:

    python scratch/agent/run_s3823_m5_paired_route_parity.py

The driver must launch the retail oracle and port image arm, use the existing
whole-RDRAM retail control plus port phase/task/route/source controls, save
separate logs under `scratch/agent/s3823_m5_paired_route_parity/`, and SIGKILL
both processes after 120 seconds. Inspect only bounded phase, positive-control,
exact-span snapshot, and crash/abort summaries. H1 requires title 1024 and
hangar 512 in both arms plus matching snapshots; H2 requires the same coverage
but nonmatching snapshots; H3 is any missing control, target phase, or crash
before comparison.
