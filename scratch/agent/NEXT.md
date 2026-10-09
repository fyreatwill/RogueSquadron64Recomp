# Next work unit (s4454): per-PC histogram of retail MusyX range vs port

HYPOTHESIS-ID: m5-ai-event-cadence

Context: s4453 showed retail runs 0x80090768-0x80091B3C ~1.65M times/20 s pre-title (control range fired, bisect in PORTING-STATE s4453). s4449's "retail never renders" is overturned.
Work: add `--pc-range-hist` (or reuse exec-prev table sized up) to tools/oracle/rs64_oracle.c giving a per-PC hit count table for a --watch-pc-range at shutdown; run on 0x80090768:0x80091B3C 20 s with control range; then count the port's executions of the same functions (musyxRenderVoiceSamples, KeyOnVoice) per second and compare.
Outcomes: retail rate >> port => port under-drives voices; similar => look at voice-array base (retail voice0 read-watch of 0x801951B8 saw 0 -> retail base likely differs; find it from register dump in hits, e.g. v0=0x801496b0/0x80150000 seen at pc 0x80090e04).
Also noted: wild jump 0x1859645e8 / last guest pc 0x80001b08 -> indirect-call idiom-class audit if it recurs.
