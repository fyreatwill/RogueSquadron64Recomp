# Next work unit (s4450): who produces retail AI buffers?

HYPOTHESIS-ID: m5-ai-event-cadence

Known (s4449): retail pre-title 20 s: 0 exec of 0x80090768 and 0x8008FFAC while AI len nonzero ~1180/1200 VI. Single-source; overlay-alias caveat; control was low-rate.
Hypotheses: (a) retail synth runs in a different function/overlay copy; (b) retail uses RSP audio task only, port's CPU voice render is port-only.
Discriminator: --watch-pc-range over the musyx code span (0x8008F000:0x80092000) for 20 s with a hot-PC control; plus --pc-task-dump on the osSpTaskLoad PC for type-2 audio tasks. Range hits => (a) with entry PC; none + audio tasks present => (b).
