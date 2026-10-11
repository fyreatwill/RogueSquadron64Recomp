# NEXT: resume docs/M5-AUDIO-PLAN.md step execution
HYPOTHESIS-ID: m5-audio-destub
Closed (s4576): voice-record words 0..7 residue is never read by any funcs_24.c load (3 arms, control present). Do not revisit.
Work unit: open docs/M5-AUDIO-PLAN.md, find the first de-stub step without a validation soak verdict, write its competing hypotheses + discriminator here, implement it (one bounded change), enqueue a soak in scratch/agent/soak_queue/. Note scratch/agent/SOAK-RESULTS.md shows earlier m5 step soaks failed rc=1/127 (s2328, s2680, s4104) - check whether those scripts are still valid first.
