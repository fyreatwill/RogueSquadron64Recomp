# Next work unit: M5 port callback parity table

HYPOTHESIS-ID: m5-host-callback-parity

The s3726 retail ground-truth request was control-valid: it reached both target
origins and showed active audio task paths, but cannot expose host callback
threads or SDL queue ownership. Build one diagnostic-only port table. Do not
change selector, clear, task, audio-route, or payload behavior.

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
Build/run: use the existing validated real-vs-silent pair recipe and add the
full callback table in the same build; phase-gate on VI 512 and retain all
RSP/task/SP positive controls. Capture both arms concurrently, kill both with
SIGKILL, and write the bounded comparison to a new `docs/M5-S3727-*.md`
evidence note.
