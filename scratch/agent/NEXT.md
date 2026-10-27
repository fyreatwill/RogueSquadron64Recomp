# NEXT: RUN — independent/reference-RSP comparison for the FD57 ring
HYPOTHESIS-ID: g3c-owner-visual-b

The corrected post-vd replay is complete. Do not rebuild or rerun the game
before this comparison.

Use the corrected route witness:

- `scratch/agent/m6/g1_lvl2s6380long/run.log`
- `scratch/agent/m6/g1_lvl2s6380long/keys.log`
- `scratch/agent/m6/g1_lvl2s6380long/mc_ctl.txt`
- reference: `scratch/agent/m6/g1_lvl2s6378/run.log`

Use the fetched/reference RSP implementation or an existing accurate RSP
emulator on the exact logged FD57 input vectors from
`scratch/agent/m6/g1_lvl2s6380long/run.log`; compare lane outputs and clamp
flags with the 8/8 host replay result. If no reference path can consume these
captured vectors, record that concrete capability failure and use the owner's
`ROGUESQ_CULL_SPIKE` decision as the next gate rather than another game run.
The route audit already passed the positive control: s6380long has 155 FD57
`[spike-st]` rows and 546 FD57 `[spike-vu8]` rows, with `att=1 mission` and the
same VI origins as s6378.

Competing hypotheses:

- H-rsp-emu-clamp: the independent/reference RSP disagrees with the logged lane
  values, selecting an emulation/clamp defect.
- H-clip: the independent/reference RSP agrees and the near-zero-w chain is a
  legitimate saturated clip-path output.
- H-retail: the independent/reference RSP agrees, but only a retail emulator
  frame comparison can establish whether the visible wedge is hardware-faithful.

DISCRIMINATING MEASUREMENT: independent/reference-RSP lane output and clamp
flags for the exact FD57 input vectors. Disagreement selects H-rsp-emu-clamp;
agreement with saturation selects H-clip; agreement without a retail comparison
leaves H-retail open.
