# Next work unit: M5 Step 10 - re-validate audio with the fresh (7f) save

HYPOTHESIS-ID: m5-audio-destub-sequence

s4224 closed the zero-volume chain: stale build/saves poisoned volume bytes. Fresh save -> cmd 0x15 a0=0x7F.

Hypotheses:
- H-audio-now-mixes: with volume 0x7F the RSP audio path produces nonzero PCM samples at the host output and some crash families change.
- H-other-zero-gate: another gate (voice-array / key-on) still yields silence despite nonzero volume.
Discriminator: run the s4224_eep_fresh recipe (scratch/agent/s4224_eep_fresh.sh, delete build/saves first) with the PCM/host-output census flag (grep docs/M5-AUDIO-PLAN.md for the output-sample census env), same run reports max |sample|. Positive control: a mark-everything / synthetic tone if available. Nonzero -> H-audio-now-mixes: run a 300 s soak and compare crash family counts.
