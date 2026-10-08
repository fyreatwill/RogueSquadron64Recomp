# Next work unit: who writes the hangar's constant DC AI output (s4236)?

HYPOTHESIS-ID: m5-audio-destub-sequence

s4236: hangar AI buffers are one repeated stereo frame (distinct=1 per channel), L/R ramping +0x100 per buffer, ~-12000/-8200; title control wide-band.
Hypotheses: (a) sources silent, DC is filter/accumulator state of the LLE ucode mixing stage; (b) final stage (resample/limiter/DMEM->RDRAM) injects an uninitialised bias; (c) our HLE/stub path writes the output buffer (not the ucode).
Discriminator: in hangar, dump RDRAM mix-bus/intermediate buffers feeding the output (or log writer PC for the output ring 0x80166450..0x80169150 via existing write-watch tooling) in the same run as the title control. Writer = ucode LLE -> (a)/(b) (compare input bus nonzero?); writer = host/stub -> (c).
Recipe: scratch/agent/s4236_hangar_stats.sh (needs ~360 s window to reach hangar). Positive control: title buffers in same run.
