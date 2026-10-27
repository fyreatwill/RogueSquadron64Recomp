# NEXT: OWNER GATE — decide `ROGUESQ_CULL_SPIKE` after failed reference comparison
HYPOTHESIS-ID: g3c-owner-visual-b

The corrected post-vd replay is complete. Do not rebuild or rerun the game for
this gate. The independent cxd4 RSP source exists at
`/Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-rsp-cxd4`,
but its scalar VU objects segfaulted reproducibly around parsed row 95 in the
offline comparator after 88 rows. The Ares-derived header path is the runtime
implementation and is not independent ground truth.

Session 6387 evidence: the repository remains at the owner gate, with no new
runtime result, no rebuild, and no default-setting change.

Use the corrected route witness:

- `scratch/agent/m6/g1_lvl2s6380long/run.log`
- `scratch/agent/m6/g1_lvl2s6380long/keys.log`
- `scratch/agent/m6/g1_lvl2s6380long/mc_ctl.txt`
- reference: `scratch/agent/m6/g1_lvl2s6378/run.log`

Owner gate: choose whether `ROGUESQ_CULL_SPIKE=1` is acceptable as an opt-in
mitigation while leaving retail defaults unchanged, or provide a reference
RSP/emulator path that can consume the captured vectors. Do not run the game
until that choice is made.
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

DISCRIMINATING MEASUREMENT: an independent/reference-RSP lane comparison. It
was not obtainable this iteration: cxd4 compilation succeeded, but the
comparator crashed at a reproducible row before FD57 evaluation. If a usable
reference is supplied, disagreement selects H-rsp-emu-clamp; agreement with
saturation selects H-clip; agreement without a retail comparison leaves
H-retail open. Otherwise the owner's culling decision is the next gate.
