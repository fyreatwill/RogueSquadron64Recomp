# Next work unit: M5 host callback parity boundary

HYPOTHESIS-ID: m5-host-callback-parity

The s3725 Step 1 retry was control-valid. Do not change selector, clear, task,
audio-route, or payload behavior. The next work unit is one bounded host
callback/queue comparison, using an independent ground-truth request before
building any new instrument.

Competing hypotheses:

- `H-CallbackQueueOwnership`: real-only image-stage callbacks are caused by a
  host callback/queue owner or cadence difference.
- `H-GuestContractDownstream`: the real-only rows remain downstream of a
  guest task-contract edge despite matching host queue observations.
- `H-SharedQueueState`: both arms share the relevant callback/queue state and
  the difference is an unmeasured consumer or guest edge.

Discriminator: a single same-build table joined by route ordinal and callback
sequence, with queue owner/thread, enqueue/remaining depth, callback source,
PCM-consumer count, and image-stage order for both arms after VI 512. A
real-only owner/thread or cadence split at matched callback rows selects
`H-CallbackQueueOwnership`; matched queue state with a real-only preceding
guest contract edge selects `H-GuestContractDownstream`; identical joined
queue/callback rows with no contract split selects `H-SharedQueueState`.
Obtain the retail ground-truth request and positive-control design before
adding the instrument.

Exact commands and the ground-truth request are to be written after that
request is answered; do not build first.
