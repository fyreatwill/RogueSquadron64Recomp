# Next work unit: qualify ROGUESQ_DPC_WRAP_FLUSH to hangar, phase-gated (s4274)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4273: backward-END ("wrap") bumps are dropped by default (4.8M/45 s); deferred ranges are read at commit, so ring laps lose lap-1 heads. ROGUESQ_DPC_WRAP_FLUSH=1 (default OFF) flushes pending ranges at the lap. Single-run: ODD 12.4%->8.6%, sane cimgs 2426->5116, VI 640 only.
Hypotheses: W1 flush fixes real loss (frames/ODD improve at hangar); W2 flush duplicates draws (visual regression); W3 neutral.
Discriminator (one run per arm, extend sleep to reach hangar ~ t=26 s + autopilot, gate counts on VI 512 transition): ODD/sane ratio in hangar phase per arm + frame dumps of each arm; fix flush-shadow (don't clear g_s4272_sh at flush; compare per-range) so the late-write diff is valid in arm1. Positive control: arm0 must show wrapBumps>0 and arm1 flushes>0 (both seen s4273).
Script: scratch/agent/s4273_ab.sh (raise sleep to ~70 s). Then crash soak for default decision.
