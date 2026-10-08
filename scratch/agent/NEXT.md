# Next work unit: power the silent-vs-real private-DMEM comparison (s4252)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4251: private+real audio crashes 3/9 arms (28.2, 28.2, 45.4 s), shared 1/5, private+silent 0/2. c3 (fixed 28 s event) refuted.
Hypotheses: c1 audio-rate-driven race (silent private never crashes); c2 gfx race independent of audio (silent private crashes at similar ~33%).
Discriminator: edit s4251_ab.sh to 3 B + 3 C arms (6 concurrent may slow; check A-free so no starvation control: keep one A as positive control = 7 arms, or run in two waves of 4), 3 repeats => >=9 each. c1 predicted: C 0/9; c2: C ~3/9.
Commands: env TAG=_N zsh scratch/agent/s4251_ab.sh ; python3 tools/s4250_summarize.py scratch/agent/soak_results/s4251_ab_N/arm*.log
If c1: crash frames' writer is guest audio sample-stream; name it with tools/apply_s4230_listwatch.py. If c2: RT64 copyToRAM/vertex cache race — pc-attribute the wild pointer.
