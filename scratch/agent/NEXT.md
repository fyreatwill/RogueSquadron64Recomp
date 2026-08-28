# NEXT work unit (s2869) — M5-new-post-dispatch-angle

HYPOTHESIS-ID: M5-new-post-dispatch-angle

## Work unit

Choose one genuinely new post-dispatch/scheduling discriminator after the
status-table angle failed. First use the retail oracle to identify a concrete
audio-task completion or queue transition and its predecessor; only then add
one batched port counter set and qualify title/hangar in the same run.

## Competing hypotheses and discriminator

- H-retail-post-dispatch: a new retail completion/queue predecessor has a
  phase-qualified transition that can be mapped to a port edge.
- H-route-failure: the whole-RDRAM control passes but title/hangar do not
  qualify, making the downstream comparison unevaluable.
- H-no-edge: title/hangar qualify, but the selected completion/queue event has
  no distinct ordering relation to the audio work.

The discriminator is a same-run table containing the whole-RDRAM positive
control, VI origins, the selected retail event's PC/predecessor and payload,
and the corresponding port marker. A new phase-qualified predecessor or
completion ordering selects H-retail-post-dispatch; missing target phases
select H-route-failure; qualified unchanged ordering selects H-no-edge.

## Exact commands

Before any port build, inspect the oracle's existing execution-watch and task-
dump surfaces and run one positive-control-first retail probe. Do not reuse
the broad `0x8003D000..0x80040000` range or the status-table poll recipe. The
selected address and command must be written here before building.
