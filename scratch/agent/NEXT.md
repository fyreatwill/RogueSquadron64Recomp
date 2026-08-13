# NEXT work unit (authoritative parser-counter boundary audit)

HYPOTHESIS-ID: m3-e9-parser-counter-boundary

Perform one bounded, read-only source audit of every writer, reset, and scope
boundary for the authoritative parser E9 counter used in `[e9-task-join]`.
Inspect the definitions and callsites for `g_e9prov`,
`g_cumulative_fullsyncs`, the authoritative advance ring, and the code that
computes `parser_delta`. Do not build or rerun the game.

Competing hypotheses:

- H-parser-counter-task-local: parser delta is task-local and the 12-vs-29
  result is a real per-task authoritative loss.
- H-parser-counter-cumulative: parser delta uses a cumulative counter or a
  reset boundary different from the join, so subtraction is invalid.
- H-parser-counter-filtered: parser accounting intentionally excludes some
  legitimate E9 forms.

Discriminating measurement: produce one source-derived table listing every
increment and reset site, the owning counter, and its task/phase lifetime; cite
the exact call path feeding `parser_delta`. An explicit task-local, cumulative,
or filtered classification is required before any new runtime instrumentation.

No build command is expected for this work unit.
