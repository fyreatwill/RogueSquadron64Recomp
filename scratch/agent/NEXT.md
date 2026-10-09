# Next work unit (s4468): read the s4468_hdr_nested soak, replay [rs-hdr-nested]

HYPOTHESIS-ID: m5-ai-event-cadence

State (s4467): the previous soak (s4467) never launched the game (root-path bug in the recipe, rc=0 was false). Fixed and requeued as s4468_hdr_nested.
Hypotheses: (A) rs_malloc returned an overlapping block: nested headers show hflags=0x0002 (allocated) at the 0xF7C malloc. (B) a free (e.g. coalesceFreeHeapBlocks inside rs_malloc) released them: nested hflags=1.
Step: tail scratch/agent/SOAK-RESULTS.md; first confirm the s4468 line shows non-zero "rs-malloc lines" (otherwise the run is invalid again - check cd/run.log). Then grep rs-hdr-nested in scratch/agent/soak_results/s4468_*/run.log. If no run reached VI 1024, diff the one earlier run (s4466_2) that did against the others.
Outcomes: all nested hflags=2 -> A selected (second source); flag 1 -> B, close lead as benign.
