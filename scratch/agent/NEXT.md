# NEXT (s5672): host-sink check for the residual fuzz (H-c2a)
Facts (s5671): retail oracle AI PCM hf_ratio (title med 0.200, hangar 0.156) matches port AI PCM (0.20-0.24 / 0.185); fuzz is not in the ucode PCM spectrum.
Hypotheses: H-c2a port AI frequency / SDL device rate or format differs from retail dacrate (resample artifacts); H-c2b host sink fine, fuzz was the pre-s5669 rail clipping (owner listen needed); H-c2c SDL queue underruns/crackle (callback starvation).
Discriminator: oracle `[ai-dacrate]` lines in scratch/agent/soak_results/s5671_hf/oracle.log vs port AI rate/SDL obtained spec + underrun count in one title-phase run. Equal rate and zero underruns => H-c2b (ask owner to listen).
HYPOTHESIS-ID: g2-speech-audible
