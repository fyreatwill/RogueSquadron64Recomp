# M5 s3681 — source-read publication order

The qualified concurrent capture added a publication snapshot to every
source-span input-DMA row. Retail passed the whole-RDRAM, descriptor, title,
hangar, and type-2 task controls. The port reached both target phases and
passed phase, source-hook, ABI, DMA, source, and stage controls; it emitted
1,024 source rows, 3,903 stage rows, 1,973 ABI/DMA rows, and no crash or abort.

| Source rows | Count |
|---|---:|
| Current task generation | 1,024 |
| Route current at source read | 240 |
| Route publication lagged | 784 |

For the 784 route-lagged rows, the source event preceded the first stage event
with the same task generation. No source event was observed after that stage.
The remaining 240 rows had no same-generation stage row in the bounded census;
the existing diagnostic fallback matched their stages to older source records,
so they do not establish a different-task owner. The join report had zero
ordering violations.

This selects `H-SourceBeforePublish` for the route-lagged majority and rejects
the measured form of `H-DmaPublicationRace` (reversed source/stage order).
`H-SourceWrongTask` remains open for the 240 unmatched rows. The ordering and
ownership result is single-source port evidence; retail independently validates
that the watched source, descriptors, title, hangar, and audio-task activity
are live on the qualified route.

ORIGIN: diagnostic-only publication and event-order witness; no guest value was
skipped, rewritten, or guarded.
