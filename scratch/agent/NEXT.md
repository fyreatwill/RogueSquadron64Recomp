# Next work unit: qualify paired-arm startup stability with the probe driver

HYPOTHESIS-ID: m5-paired-arm-stability

s3803 validated the independent retail control but could not validate the
paired port census. The oracle whole-RDRAM control fired, retail reached title
`0x00790400` and hangar `0x006AB400`, and shut down naturally after 45 seconds.
Across same-build port variants, the second-launched arm crashed 36 times at
guest PC `0x8000834C`; another run crashed the first arm before title. The
image arm produced 256 source-range rows only when it survived. No source
writer conclusion is allowed from these runs.

Competing hypotheses and discriminator:

- H1: the direct executable wrapper is causing startup/window contention;
  launching each arm through `tools/probe.sh` produces both target VIs with
  zero crash markers and preserves the M5 positive controls.
- H2: two port instances genuinely contend in the scheduler; the probe-driver
  launch still has one arm die at `0x8000834C` before target phase.
- H3: the M5 diagnostic load itself destabilizes the arm; the probe-driver
  pair reaches target only when the source-census variables are removed, while
  the full census arm fails.

The discriminating measurement is one same-build pair using the established
`tools/probe.sh` launch/window path, with the full M5 census variables and the
retail oracle kept in the same recipe. H1 predicts two valid port arms and a
complete paired census; H2 predicts a repeatable one-arm `0x8000834C` crash;
H3 predicts stability only in a no-census control, which must be run in the
same batch if needed. Whole-RDRAM and both retail target-VI controls must fire.

Commands:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_m5_source_input_writer.sh

Before running, replace only the direct port launches in that recipe with
`tools/probe.sh` invocations, keeping the same environment, oracle watches,
phase gate, and SIGKILL cleanup. If both arms qualify, resume the upstream
zero-DMEM producer census. If either arm still crashes, stop repeating launch
order and record the paired arm as unevaluable; choose a new single-arm
ground-truth discriminator or ask for a human decision.
