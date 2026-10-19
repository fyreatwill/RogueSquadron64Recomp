# Next work unit: read s5481_mode_after_end (scratch/agent/m6/s5481_mode_after_end, SOAK-RESULTS.md)
Question: after requestMissionTransitionMode sets 0x10C9E0=4 (s5480), what writes that word next (MODE_WP watch, bt in lldb_att1.log) and what is on screen?
Hypotheses: (A) mode advances 4->N = results/debrief flow; read the writer. (B) stays 4 with a presenting loop = idle post-mission loop; find the consumer of mode 4 in runInMissionFrame. (C) watch never fires (control: counter wp must still fire).
HYPOTHESIS-ID: m6-mission-end-trigger
