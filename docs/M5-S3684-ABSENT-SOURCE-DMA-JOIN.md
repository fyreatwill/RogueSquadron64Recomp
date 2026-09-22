# M5 s3684 — generation-absent source/DMA join

The reconstructed qualified concurrent runner passed the retail whole-RDRAM,
descriptor, source-span, title, hangar, and type-2 controls. The port reached
both target phases and emitted the source, stage, ABI, and DMA controls. No
crash or abort marker appeared.

The hangar source census recorded 512 input-DMA rows. Of these, 220 had no
matching stage generation; the remaining 292 were generation-matched in this
capture. Every one of the 220 generation-absent rows carried source task
pointer `0x80171E70`, and that pointer was present in the hangar stage stream.
Thus the absent rows do not select a distinct task object by the measured task
pointer. They are source input-DMA records with a generation mismatch despite
the same logical task pointer. The run does not establish whether they are
later-publication rows or records consumed without a stage callback.

This refutes `H-AbsentDistinctTask` as a task-pointer distinction and leaves
`H-AbsentNoStageConsumer` versus `H-AbsentPublicationGap` unresolved. The
result is single-source port evidence for generation/task-pointer identity;
retail independently supplied the reachability and positive controls.

ORIGIN: diagnostic source/DMA/task join; no guest-state rewrite or mitigation.
