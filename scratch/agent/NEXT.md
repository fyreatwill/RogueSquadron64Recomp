# NEXT work unit (s2657) — trace OSTask allocation/initialization boundary

HYPOTHESIS-ID: m5-pcm-publication-edge

## Work unit

Perform one bounded static/runtime census of the allocator or generic copy that
creates the audio task at `0x80149470`. s2656 passed the retail and port
positive controls and found no direct guest `OSTask+0x28/+0x2C` stores; the
same task pointer remained zero at `osSpTaskLoad` and `osSpTaskStartGo` in both
image and silent arms. Locate the initialization source and capture its source
pointer, destination task pointer, copy length, and post-copy fields in one
build/run. Do not add writeback, remapping, or a defensive guard.

## Competing hypotheses and discriminator

- `H-GenericCopyInitializesZero`: a guest copy/clear initializes the dispatched
  task, and the source already has zero fields.
- `H-ProducerOverwritten`: a nonzero producer store occurs, then another guest
  store clears or replaces it before `osSpTaskStartGo`.
- `H-TaskPointerMismatch`: nonzero fields are written to a different task
  object than the pointer dispatched to `osSpTaskStartGo`.
- `H-HostZeroesTask`: the guest task is nonzero or unspecified, but host/runtime
  construction explicitly clears the fields.

The discriminator is a same-task timeline keyed by task pointer and ordinal:
allocator/copy source and length, values at source/destination offsets
`0x28`/`0x2C`, host task-construction values, dispatch-time values, and the
existing DMA/output rows, separately under title and hangar controls. A
positive whole-RDRAM retail oracle control and both port phase controls are
required; a null without them is unevaluable.

## Exact commands

1. Ask/inspect the retail oracle first for the corresponding task-field
   control; reuse the s2656 oracle artifact only if the command is unchanged.
2. Grep generated/runtime sources for allocator, `memcpy`/copy, and task
   construction paths. Batch source/destination field logging and host-create
   logging into one build, preserving phase gating.
3. Run the qualified image/silent pair from `build/`, with C88=`0` and passive
   breadcrumb variables. SIGKILL each game process after both title and hangar
   controls or the bounded watchdog timeout.
4. Parse by task pointer and ordinal. A zero-valued generic copy selects
   `H-GenericCopyInitializesZero`; nonzero source/copy followed by zero
   destination selects overwrite or host clearing; a different destination
   selects pointer mismatch. Retain the s2656 artifact as baseline.

## Expected outcomes

- A zero-valued generic copy selects `H-GenericCopyInitializesZero`; next step
  is the copy source producer.
- A nonzero-then-zero timeline selects `H-ProducerOverwritten`; next step is
  the clearing writer and its legitimate contract.
- Stores on another pointer select `H-TaskPointerMismatch`; next step is the
  task pointer handoff/copy.
- Host-only clearing selects `H-HostZeroesTask`; next step is the runtime task
  constructor, with no guest writeback.
