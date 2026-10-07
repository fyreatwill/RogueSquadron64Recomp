# Next work unit: M5 Step 4 port writer-path audit

HYPOTHESIS-ID: m5-audio-step4-port-writer-path

Session 4075 qualified retail `0x80094648` as a legitimate nonzero indexed
channel-span writer, but the port's `startSongSequence` witness reached only
entry/branches and no target store. The port reached both target phases, with
positive gate/source/consumer controls and zero PCM payload.

Competing hypotheses:

- H94648-port-store: the port reaches the indexed store after a missing or
  unobserved predecessor; the next capture will show a retail-shaped target
  store destination/value relation.
- H94648-port-branch: a branch/state/input mismatch prevents the target store;
  the full entry-to-branch trace will show the divergent predicate and no
  target store despite valid phase/task controls.
- Hcoverage: the isolated image route loses title/hangar or writer witness
  coverage, making the port null unevaluable.

Discriminating measurement: one same-build retail-gated isolated image capture
with the existing phase-keyed task/PCM joins and the complete port
`startSongSequence` writer trace, including entry/branch/target-store rows.
H94648-port-store requires valid controls plus a target-store row matching the
retail destination/value relation; H94648-port-branch requires valid controls
plus entry/branch rows and zero target stores; Hcoverage is selected by any
missing whole-RDRAM, title, hangar, or isolated-image gate.

Exact implementation: reuse `scratch/agent/run_s4075_m5_step4_94648.sh`, keep
the retail whole-RDRAM/title/hangar and `0x80094648` controls, and add only the
missing port-side target-store fields to the existing generated-function
fixup/instrument. Build once, run once from `build/`, retain
`PROBE_PHASE_WIDTH=1024` and `PROBE_KEYS_FROM_PHASE=1`, and SIGKILL the process
group. Do not change the gate or add a mitigation.
