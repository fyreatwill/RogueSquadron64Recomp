# NEXT (s5668): fold s5667_lat_{a,b} soak results ([lat-in]/[lat-out] in scratch/agent/soak_results/)
Facts (s5667): runVoiceLatticeFilter is pure integer; clamp translation verified correct. Instrument already built and soaks queued.
Hypotheses: H9 coefficients/state garbage (unstable lattice); H10 input samples already garbage/rail (upstream stage-1 decode in renderVoiceAudioBlock); H11 legit clamp (unlikely).
Discriminator: grep '\[lat-' in the logs. Control: >0 [lat-in] lines and some nonrail_nonzero>0. Coef words absurd or state diverging => H9, trace where renderVoiceAudioBlock loads coefs (header from decoded stream). Inputs at rails => H10. Both sane => revisit.
If soaks have not run yet, do an offline read of renderVoiceAudioBlock (0x8009DB44) to find the coefficient/state source while waiting.
HYPOTHESIS-ID: g2-voice-never-requested
