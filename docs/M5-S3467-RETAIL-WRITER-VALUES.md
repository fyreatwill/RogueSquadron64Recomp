# M5 Session 3467 — retail candidate writer values

The independent Rice oracle ran the validated six-Start route for 35 seconds
with whole-RDRAM and physical source-slot positive controls, title phase gates,
the table-entry span `0x001B4AA0:0x001B4B24`, candidate writer PCs, and the
existing load/store execution watches.

The controls fired in the same run: 14,936 whole-RDRAM writes, 1,904
source-slot writes, 533 title VI frames at origin `0x00790400` and 534 at
`0x00790800`, and 3,032 table-span writes. The existing execution watches
recorded 2,610 hits at `0x800644A8`, 7,467 at `0x800644DC`, and 7,171 at
`0x80064524`.

The candidate writer watches fired in the title phase at `0x80064350`
(445 lifetime; 228 at origin `0x00790400`, 217 at `0x00790800`),
`0x80064360` (427; 216/211), `0x80064378` (427; 216/211), and `0x800646D8`
(564; 287/277). Store-field rows tie these PCs to the observed entry span;
for example, `0x80064350` reaches `0x001B4AA0` with pre-store word
`0x801B4F80`, while adjacent writes reach the corresponding entry fields.

The post-value control on the physical source slot sampled 624 words. At the
shared `0x80064524` store it observed 398 nonzero samples, including the
known retail values `0x801B4F00` (327 overall) and `0x801B5E70` (71 overall).
The candidate writer rows themselves report the word before each store, not
the value written afterward. Therefore this run confirms active candidate
writers and legitimate table activity, but does not select
`H-SourceWriterValue` versus `H-TablePointerDivergence`.

Evidence: `scratch/agent/s3467_m5_retail_writer_values/oracle.log`.

ORIGIN: no mitigation or runtime behavior change was added; the observed
state-pointer values are legitimate retail values at the qualified shared
store, while candidate-writer post-store values remain unmeasured.
