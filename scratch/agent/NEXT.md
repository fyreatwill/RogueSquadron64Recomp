# Next work unit (s4442): writer of the fillSampleStreamRange+15116 fault (m5-ai-event-cadence)

HYPOTHESIS-ID: m5-ai-event-cadence

s4441: 115 Hz vs unset, 2 runs each, all crashed; fillSampleStreamRange+15116 hit in A1 and B1 at the same PC, so cadence is not its cause. Open:
(a) the faulting pointer/stream struct is corrupt (name its WRITER, ORIGIN rule 11) vs (b) a legitimate struct is used before init (audio-disabled degenerate path) vs (c) a port-side DMA/ARAM stub returns bad data.
Discriminator: at the fault, dump the faulting register/base value and the stream struct, then oracle-watch (tools/oracle) the same struct address in retail for the writer PC. Also still pending: mupen CPU Count per submit (781k cycles/VI positive control; ~8.7 ms => retail 115/s).
Templates: scratch/agent/s4441/run.sh (usage: run.sh <label> <hz|none>), all.sh.
