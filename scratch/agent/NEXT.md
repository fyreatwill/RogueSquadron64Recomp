# NEXT work unit — identify the writer that leaves hangar pre-clear bytes

HYPOTHESIS-ID: m5-output-preclear-writer-attribution

Session 3543 established that the hangar `rs_memset` clear enters with
`pre_nz=344`, while title enters zero. The port writer identity is still open.

Do exactly one bounded work unit: extend the existing source-range writer
census to capture the entire run before the target phase, then join the last
nonzero writer to the hangar `rs_memset` entry. Keep the same real-audio
LLE/spin-yield/autopilot route and do not alter audio, PCM, or output state.

Competing hypotheses and discriminator:

- `H-PortPrephaseCPU`: a generated CPU store before VI 1024/512 establishes
  the nonzero hangar bytes; its PC and payload precede the hangar entry.
- `H-PortPrephaseDMA`: a RDRAM writeback/DMA before the target phase establishes
  them; the DMA destination, length, and nonzero hash precede the entry.
- `H-CarriedInitialState`: no port writer establishes the bytes in this run;
  the span is already nonzero when the route becomes observable.
- `H-CaptureInvalid`: the whole-RDRAM/phase controls or writer hooks do not
  fire, so no writer conclusion is admissible.

The discriminating table must include every overlapping scalar/vector/RDRAM
writer event from process start through the hangar clear, with phase/VI
identity, PC or DMA source, destination, length, payload FNV/nonzero count,
and the `rs_memset` ordinal. A nonzero CPU event selects `H-PortPrephaseCPU`;
a nonzero DMA event selects `H-PortPrephaseDMA`; no writer with a live source
control and nonzero pre-clear snapshot selects `H-CarriedInitialState`; missing
controls select `H-CaptureInvalid`.

Before building, retain the retail ground-truth result from
`scratch/agent/retail_preclear_groundtruth.log`. Then update the
regeneration-safe generated-function injection and run:

    python3 tools/apply_s3543_m5_preclear.py
    cmake --build build --config Debug --target RogueSquadron64Recomp -j8
    env ROGUESQ_AUDIO_UCODE=1 ROGUESQ_LLE_FORCE=1 ROGUESQ_SPIN_YIELD=1 ROGUESQ_LLE_UNGATED=1 ROGUESQ_LLE_SOLO=1 ... zsh tools/probe.sh scratch/agent/s3544_m5_preclear_writer 55 0.5

Use SIGKILL cleanup and phase-gate on VI transitions. Do not repeat the
closed `rs_memset` identity probe without the pre-phase writer census.
