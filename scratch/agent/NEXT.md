# Next work unit (s4377): bounded upstream caller audit

HYPOTHESIS-ID: m5-selector-decode-boundary

The s4376 qualified retail capture directly joined `0x80019DEC ->
0x80033FCC`: 3,452 caller executions were immediately followed by the task
publication, and paired rows carried the same task pointer/publication fields.
The remaining question is upstream selector/decode input, not a missing task
publication boundary. Do not repeat the caller census, direct publication
join, or closed first-eight payload comparison.

Competing hypotheses:

- H-upstream-selector: a bounded predecessor/caller writes or supplies the
  selector/decode input that becomes the phase-specific published payload.
- H-payload-overwrite: direct publication is correct, but a later writer
  changes the payload before consumption.
- H-input-watch-gap: the chosen upstream PCs are not on the title path while
  the whole-RDRAM, VI, and task controls remain live.

Discriminating measurement: first audit the existing generated-function
listing for every `jal 0x80033FCC` in the caller function and its immediate
predecessors, then choose one bounded oracle run that watches all identified
upstream PCs plus one post-publication payload range. A title upstream row
whose source fields predict the published family selects H-upstream-selector;
a phase-matched writer after `0x80033FCC` selects H-payload-overwrite; no title
upstream rows with live controls selects H-input-watch-gap. A null without the
whole-RDRAM positive control, all three VI buckets, and at least 1,000 valid
type-2 rows is invalid.

Exact audit command (no build or run before this audit):

    rg -n -C 8 'jal +0x80033FCC|osSpTask(StartGo|Load)_recomp|0x80019D' scratch/agent/s389_verify/before_current_applied/funcs_4.c

Then run exactly one batched oracle capture from the repo root, using the
audited PC list in one `--watch-pc` argument, `--pc-field-dump` for every
audited upstream PC, `--watch-write` for the published payload range, the
`0x80033FCC` typed task dump/join, `--watch-write 0x0:0x800000`, all three
`--pc-phase-log-width` buckets, Rice, and the established Start schedule.
