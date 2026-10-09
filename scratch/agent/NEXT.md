# Next work unit (s4452): fold s4452 replicate soak

HYPOTHESIS-ID: m5-ai-event-cadence

Read SOAK-RESULTS s4452 lines (arms drain, vi, drain2, vi2). Outcomes: vi arms crash (fillSampleStreamRange+15116) and drain arms clean => cadence matters, consider default-on; all four crash => cadence closed, return to oracle PC-range probe (--watch-pc-range 0x8008F000:0x80092000, hot-PC control); all four clean => baseline irreproducible; diff this recipe vs s4441's (env, keys, phase) and re-run with s4441's exact recipe; drain-only crash => poller/queue-depth bug.
