# Next work unit (s4451): fold s4450 drain-event soak

HYPOTHESIS-ID: m5-ai-event-cadence

Read SOAK-RESULTS s4450 lines (arms drain vs vi). Outcomes: drain clean + vi crash => cadence matters, consider default-on; both crash same PC => cadence closed, return to s4449 oracle PC-range probe (--watch-pc-range 0x8008F000:0x80092000 w/ hot-PC control); drain crashes only => bug in poller/queue depth.
