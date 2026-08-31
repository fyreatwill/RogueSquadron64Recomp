# NEXT work unit — attribute the exact retail frequency-result writer

HYPOTHESIS-ID: m5-frequency-result-writer

Session 3431 showed that port's `0x5622` is the post-`osAiSetFrequency`
frequency result, reloaded at `0x8009192C` before the allocate call. Retail's
independent oracle wrote the corresponding physical result address in the
title phase, but the broad writer histogram did not isolate the exact edge.

Competing hypotheses and the single discriminating measurement:

- `H-RetailFrequencyResultDiffers`: retail's exact frequency-result writer
  stores a value different from port's `0x5622`.
- `H-RetailFrequencyResultMatches`: retail stores `0x5622` at the same edge,
  so the remaining gap is downstream of this count.
- `H-RetailWriterIsOtherState`: the watched address is written by unrelated
  state traffic and is not the frequency result on the driven route.

Exact work: run the oracle first with whole-RDRAM plus
`0x165ED0:0x165ED4`, post-value sampling, title and hangar buckets, and the
candidate writer PC `0x800331E0` as execution control. In the same run retain
the target writer histogram. Then run the existing port pair with
`ROGUESQ_LOG_INIT_VOICE_SAMPLE=1` and the three reapply boundaries. A matching
retail value selects `H-RetailFrequencyResultMatches`; a different value from
the same writer selects `H-RetailFrequencyResultDiffers`; unrelated writers
select `H-RetailWriterIsOtherState`.
Do not change waits, slots, dispatch, clear behavior, or PCM writeback.
