# Next: expose exact source-DMA ordering

HYPOTHESIS-ID: m5-audio-source-ownership

Session 3670 removed the 290 remaining CPU stores from the object-payload
candidate set: `0x80007670` is `rs_strncpy` zero padding and the smaller sites
populate texture-data records. The next unit is one bounded source-DMA ordering
join, not another CPU-store census.

Competing hypotheses:

- H-DmaConsumesInitializedRecord: each target source-DMA read follows a
  matching initialized record and can be joined to the selected task object.
- H-DmaConsumesZeroFill: source-DMA reads follow the fixed primary zero-fill
  and carry zero payloads despite the earlier record initialization.
- H-DmaObjectInterleave: DMA source/destination pairs alternate with the
  `0x80171E70`/`0x80173CB0` task objects.
- H-CaptureInvalid: any whole-RDRAM, source-span, title, hangar, or type-2
  task control fails; discard the capture.

Discriminating measurement: use the existing port M5 source-DMA and task-row
instrumentation in one run, phase-gated to title and hangar, and emit a joined
sequence table containing DMA source, destination, payload hash/nonzero count,
task data pointer, and route ordinal. Require all five controls above. A
matching nonzero DMA payload tied to a task selects H-DmaConsumesInitialized-
Record; zero payloads after the primary fill select H-DmaConsumesZeroFill;
alternating task/object identities select H-DmaObjectInterleave. A missing
control is capture-invalid, not a null result.

Before building, read the relevant port instrumentation in
`docs/debug-trace-env-vars.md` and the existing M5 source-DMA run script. Build
once, run one 55-second validated real-audio capture from `build/`, and store
the log under `scratch/agent/` with a non-dot final component. No guest-state
rewrite or mitigation is in scope.
