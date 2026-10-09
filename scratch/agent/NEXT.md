# Next work unit (s4467): get a VI-1024 run with the header dump, replay [rs-hdr-nested]

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4466): hook built and control-validated; the VI-1024 0xF7C malloc (0x801931F0) did not occur in 0/4 runs.
Hypotheses: (A) rs_malloc returned an overlapping block: nested headers show hflags=0x0002 (allocated) at the 0xF7C malloc. (B) a free (e.g. coalesceFreeHeapBlocks inside rs_malloc) released them: nested headers show flag 1.
Step: read scratch/agent/SOAK-RESULTS.md for the queued s4467_hdr_nested soak; grep `rs-hdr-nested` in its logs. If none reached VI 1024, find what differs in the one earlier run (s4466_2) that did, rather than re-running blind.
Outcomes: all nested hflags=2 -> A selected (second source); flag 1 -> B, close the lead as benign.
