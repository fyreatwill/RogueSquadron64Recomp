# NEXT work unit — isolate the retail frequency-result writer

HYPOTHESIS-ID: m5-frequency-result-writer

Session 3433 repaired the retail phase signal: the title route alternates
between width-1024 origins `0x00790400` and `0x00790800`, and both phase
buckets contain writes to `0x165ED0`.

Competing hypotheses and the single discriminating measurement:

- `H-Candidate331E0`: `0x800331E0` is the frequency-result writer and its
  execution joins target writes in one corrected title bucket.
- `H-Candidate33420`: `0x80033420` is the frequency-result writer and joins
  target writes instead.
- `H-UnlistedFrequencyWriter`: neither candidate is the writer; the phase
  histogram's remaining PCs contain the responsible store.

Exact work: run one oracle arm with whole-RDRAM control, target
`0x165ED0:0x165ED4`, both phase buckets `0x00790400:1024` and
`0x00790800:1024`, and bounded execution watches for `0x800331E0`,
`0x80033420`, `0x80007670`, and the `osAiSetFrequency` call/return boundary.
A candidate execution joined to target writes in one phase bucket selects that
writer; live target buckets with no candidate join selects an unlisted writer
and makes the phase histogram the enumeration source.
Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
