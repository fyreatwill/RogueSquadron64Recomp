# Next work unit (s4453): oracle PC-range probe of retail audio producer

HYPOTHESIS-ID: m5-ai-event-cadence

Context: s4452 closed AI-event cadence as a crash cause (4/4 arms crash, drain does not help). s4449 showed retail executes 0 hits at musyxRenderVoiceSamples 0x80090768 in 20 s pre-title.
Run: rs64_oracle --secs 20 --watch-pc-range 0x8008F000:0x80092000 plus a hot-PC control (a PC known to fire often, e.g. the AI loop 0x8008EE08 region or whole-RDRAM write watch control per tools/oracle/README.md).
Outcomes: range hits with control firing => retail runs MusyX code in range, report which PCs (compare with port); 0 hits with control firing => retail synthesises elsewhere (RSP/other overlay), port render path is port-induced; control silent => instrument invalid, redesign.
Also noted: new crash signature wild jump 0x1859645e8 / last guest pc 0x80001b08 (3/4 arms in s4452) - if it recurs, do an indirect-call idiom-class audit, not a single-site chase.
