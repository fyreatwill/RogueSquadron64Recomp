# NEXT work unit — bounded audio-task descriptor lifetime/reuse measurement

HYPOTHESIS-ID: m5-route-task-lifetime

Perform one bounded measurement of whether the guest `OSTask` descriptor is
mutated or reused after `osSpTaskStartGo` submits its pointer and before the SP
task thread reaches `run_task`. Ask independent retail ground truth first;
only then add one batched, phase-gated same-build probe if the oracle can name
the relevant task/PC boundary. Do not change behavior from pointer lifetime
concern alone.

Competing hypotheses and the discriminator:

- H-DescriptorImmutable: the descriptor fields are unchanged between submit
  and consume; pointer transport is correct and the route failure is elsewhere.
- H-DescriptorReused: the game reuses or rewrites the RDRAM descriptor before
  consumption; the observed task is not the submitted task.
- H-DescriptorOrdering: the pointer is stable but a producer/consumer memory
  ordering edge is insufficient for descriptor contents.
- H-MeasurementInsufficient: the oracle cannot attribute the target task, so
  no port conclusion is justified.

The single discriminator is a submit-to-consume identity table keyed by the
retail-grounded target transition: submitted task pointer, task fields at
submit, first consumer pointer/fields, and any intervening guest writes. A
stable pointer and fields select H-DescriptorImmutable; changed fields or
pointer select H-DescriptorReused; stable fields with a visibility mismatch
select H-DescriptorOrdering; absent retail attribution selects
H-MeasurementInsufficient. Do not infer audio behavior from VI-640
`accepted=0`.

Exact commands from the repo root:

    sed -n '1,220p' tools/oracle/README.md
    rg -n -C 25 'osSpTaskStartGo|osSpTaskLoad|M_AUDTASK|audio task|task_ptr' tools/oracle /Users/williambuckley/Documents/Tools/rogue_squadron64
    git diff -- src lib syms tools

Record the complete table and decision in
`scratch/agent/s3045_m5_task_lifetime/`.
