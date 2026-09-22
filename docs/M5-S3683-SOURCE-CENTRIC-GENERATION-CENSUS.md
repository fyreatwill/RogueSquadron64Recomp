# M5 s3683 — source-centric generation census

The prescribed s3683 runner was absent, so the qualified s3682 concurrent
oracle/port recipe was rerun after adding a source-centric census to the
existing generation/stage join. The change was diagnostic-only and did not
alter guest state.

The retail arm passed the whole-RDRAM, descriptor, source-span, title, hangar,
and type-2 task controls. The port reached title and hangar and emitted the
existing source, stage, ABI, and DMA controls. No crash or abort marker
appeared.

The census classified source rows by phase and task generation. Title ended
with 512 source rows: 512 had a same-generation stage record with the stage
event at or after the source event, 0 were reversed, and 0 lacked a matching
generation. Hangar ended with 512 source rows: 282 same-generation, 0
reversed, and 230 generation-absent. The intermediate 256-row hangar census
showed 146 same-generation and 110 absent, consistent with the final counts.

This selects `H-SourceWrongTask` for the measured 230-row hangar minority over
`H-SourcePublicationRace`; it also extends `H-SourceSameGeneration` to the
282-row hangar majority. The result is single-source port evidence: the
independent retail arm proves phase/task reachability and the positive
controls, but cannot observe the host generation census. A missing generation
match still does not identify which guest object or producer owns those source
bytes; exact input-DMA ownership remains open.

ORIGIN: diagnostic source-generation census; no mitigation or guest-value
rewrite was added.
