# Next work unit: M5 exact candidate load census

HYPOTHESIS-ID: m5-route-state-not-source

Resolve whether exact fields `0x128C92` and `0x128CD0..0x128CD3` are image
source state or only route/control metadata. s3750 showed the prior
`0x80019CD8`/`osRecvMesg` hook was not an exact-field read; do not repeat it
and do not alter `0x800078EC`.

Competing hypotheses:

- `H-RouteStateNotSource`: none of the candidate loads uses base `0x80128C70`
  in target phases, so the fields are not on the source route.
- `H-RouteStateSourceKey`: a candidate load with base `0x80128C70` reads one
  exact field and is followed by the qualified source DMA.
- `H-RouteStateStale`: a candidate load with base `0x80128C70` reads zero/stale
  state, but its value is not joined to the source DMA.

Discriminator: one build must hook exactly `0x800A5E00`, `0x800B4B08`,
`0x80065854`, `0x8007BEEC`, `0x8008F548`, `0x8008F5F0`, `0x8008F640`,
`0x800D989C`, and `0x800E8064`, record only rows whose effective base is
`0x80128C70`, and join each to the next source-DMA row. A same-run positive
control must fire for the hook mechanism, while independent retail exact-field
watches remain armed. A joined read selects `H-RouteStateSourceKey`; no
candidate rows selects `H-RouteStateNotSource`; zero/stale candidate rows with
no source effect selects `H-RouteStateStale`. Missing controls or either target
phase is unevaluable.

Ground truth before building: inspect each candidate's surrounding function
and effective-base semantics, then add only those bounded hooks through the
regeneration-safe fixup script. Batch all candidates in one real/silent
qualified run plus the oracle control. Kill every arm with SIGKILL from
`build/`.
