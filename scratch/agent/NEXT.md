# NEXT work unit (s2656) — trace guest OSTask producer fields

HYPOTHESIS-ID: m5-pcm-publication-edge

## Work unit

Perform one bounded static/runtime census of the guest-side OSTask producer
that feeds `spTaskSchedulerThread`. s2655 passed all title/hangar controls and
showed live image tasks, DMEM changes, DMA ranges, and image completion, but
`output_buff` and `output_buff_size` were zero on every joined task. Locate the
task allocation/copy/store path and capture the producer's source pointer,
task address, and writes to offsets `0x28`/`0x2C` in one build/run. Do not add
writeback, remapping, or a defensive guard.

## Competing hypotheses and discriminator

- `H-ProducerNeverSetsOutput`: no guest store reaches task offsets `0x28` or
  `0x2C` before dispatch; the null contract is constructed upstream.
- `H-ProducerOverwritten`: a nonzero producer store occurs, then another guest
  store clears or replaces it before `osSpTaskStartGo`.
- `H-TaskPointerMismatch`: nonzero fields are written to a different task
  object than the pointer dispatched to `osSpTaskStartGo`.
- `H-HostZeroesTask`: guest writes are absent, but host/runtime task creation
  explicitly supplies or clears the fields.

The discriminator is a same-task timeline keyed by task pointer and ordinal:
all guest writes to `task+0x28`/`task+0x2C`, host task-construction values,
dispatch-time values, and the existing DMA/output rows, separately under the
title and hangar phase controls. A positive whole-RDRAM retail oracle control
and both port phase controls are required; a null without them is unevaluable.

## Exact commands

1. Ask/inspect the retail oracle first for the corresponding OSTask field
   writes if no existing ground-truth watch covers them; do not build a port
   instrument until the oracle control is armed and fires.
2. Grep the generated/runtime sources for OSTask allocation, task copies, and
   offset `0x28`/`0x2C` stores. Batch any needed guest-store and host-create
   logging into one build, preserving `PROBE_PHASE_WIDTH=1` and
   `PROBE_KEYS_FROM_PHASE=1`.
3. Run the qualified image/silent pair from `build/`, with C88=`0` and the
   passive breadcrumb variables. SIGKILL each game process after both title
   and hangar controls or the bounded watchdog timeout.
4. Parse by task pointer and report each hypothesis outcome; retain the
   s2655 artifact as the output-contract baseline.

## Expected outcomes

- No guest offset stores selects `H-ProducerNeverSetsOutput`; next step is the
  allocator/task initialization boundary.
- A nonzero-then-zero timeline selects `H-ProducerOverwritten`; next step is
  the clearing writer and its legitimate contract.
- Stores on another pointer select `H-TaskPointerMismatch`; next step is the
  task pointer handoff/copy.
- Host-only clearing selects `H-HostZeroesTask`; next step is the runtime task
  constructor, with no guest writeback.
