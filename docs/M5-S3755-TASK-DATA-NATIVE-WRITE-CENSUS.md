# M5 s3755 — task-data native-write census

The independent retail oracle was rerun with a whole-RDRAM positive control,
the physical task-data watch `0x171E70..0x171F70`, and the source watch. The
control fired and the task-data watch fired in the title and hangar phases;
hangar writer PCs again included the retail `0x80090A..0x800911` family.

The paired port build added a phase-armed native page-fault watch for the task
data page. The first page fault is the positive control; the watch is writable
before the target VI transition so it does not perturb boot. With identical
LLE/autopilot settings, both real and silent arms reached title and hangar.
The real arm recorded 39 target-range native faults and 1,024 source-reader
rows; silent recorded 33 target-range native faults and no source-reader rows,
the expected no-source control. The native fault PCs symbolized into generated
game functions (for example `submitSceneNodeRender` and
`lvhBindObjectiveVoiceLinesAndStart`), not PI/RSP/zmemcpy callbacks.

This proves that a direct/native generated-code write path touches the task
data span in both arms, but the page-fault witness does not capture the value
being stored. It therefore refutes `H-TaskDataNonScalarAbsent` as a statement
about all host-side activity, while leaving the required nonzero-value
producer question open. The native writer may be a legitimate zero-valued
store; no mitigation or value interpretation is justified yet.

ORIGIN: diagnostic-only page protection and fault logging. The writer is the
generated game code at the symbolized host PCs; whether its stored value is
legitimate remains unevaluated.

Evidence: `scratch/agent/s3755_oracle_groundtruth/oracle.log`,
`scratch/agent/s3755_m5_taskdata_native_pair/real.log`, and
`scratch/agent/s3755_m5_taskdata_native_pair/silent.log`.
