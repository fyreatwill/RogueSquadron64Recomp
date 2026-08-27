# NEXT work unit (s2742) — audit M5 CPU-side MORT PCM publication

HYPOTHESIS-ID: m5-mort-pcm-publication

## Work unit

Perform one bounded static audit of the unresolved CPU-side MORT publication
boundary, starting from the known renderer output in the voice object and the
known AI worker/source spans. Enumerate every caller, callee, store/copy,
queue/service handoff, and destination in the contiguous post-mix path that
can connect those two contracts. Do not add runtime instrumentation or a
writeback/remap.

## Competing hypotheses and discriminator

- H-publish-edge-found: the static path contains a complete renderer/output
  writer to AI-source destination edge with ordering and ownership.
- H-publish-edge-partial: a candidate copy or handoff exists, but its source,
  destination, or ordering cannot be proven legitimate from static evidence.
- H-publish-edge-absent: the bounded post-mix path contains no candidate edge;
  the next discriminator must move to the remaining indirect/data-driven
  boundary rather than add another watch to known sites.

The discriminator is a complete source/destination table for the bounded path:
each possible result identifies a full edge, a partial edge, or no edge. This
is static evidence only; no runtime legitimacy or payload conclusion follows
without the retail oracle.

## Exact commands

```sh
rg -n "renderVoiceAudioBlock|audioMixStereoBlock8|osAiSetNextBuffer|copy|memcpy|bcopy|submitDmaRequestBatch|sendServiceMessage|piDmaWorker|801496B0|166450|1B4A00" \
  /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs \
  > scratch/agent/s2742_mort_publication_census.txt
rg -n "renderVoiceAudioBlock|audioMixStereoBlock8|osAiSetNextBuffer|submitDmaRequestBatch|sendServiceMessage|piDmaWorker" \
  /Users/williambuckley/Documents/Tools/rogue_squadron64
```
