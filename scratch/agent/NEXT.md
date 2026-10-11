# NEXT: close or widen the words-0..7 read watch
HYPOTHESIS-ID: m5-audio-destub
Established (s4575): in the 4 hooked functions no genuine load touches chunk-2+ voice-record words 0..7 (hits were dest==base hook artifacts). Residue looks inert there.
Hypotheses: H-inert (no consumer anywhere reads words 0..7), H-other-reader (a function outside the hooked four, or an LH/LB/LWL load, reads them).
Discriminator (one bounded change): fix tools/apply_s4307_synth_read_join.py to capture the address before the load, extend to all funcs_24.c audio functions and LH/LB/LWL/LWU forms, then rerun s4575_loadwatch.sh (copy to s4576). Positive control: chunk2+ word 18 loads must print. If still zero loads of words 0..7: close the thread and return to docs/M5-AUDIO-PLAN.md step execution.
