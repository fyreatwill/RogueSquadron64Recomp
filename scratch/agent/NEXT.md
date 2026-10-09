# Next work unit (s4440): is 192 frames/tick constant or derived? (m5-sdl-consume-rate)

HYPOTHESIS-ID: m5-sdl-consume-rate

s4439: oracle AI_LEN reads valid; DAC ~99% busy with submits 0.96/VI @768 B => mupen plays 768 B in ~16.5 ms (expected 8.7 ms). Hypotheses:
(a) mupen AI duration is ~2x slow (get_dma_duration cpu_counts estimate) and game is AI-completion-paced -> real hardware ~115 submits/s;
(b) game derives frames/tick from osAiGetLength/status, so 192 is an adaptive result in both arms;
(c) 192 is a constant in the mixer.
Discriminators (ONE build): in oracle read CPU Count (or use dbg_vi count + AI sample) at each submit to get emulated cycles/submit (a: ~16.5ms => 2x of 8.7ms; confirms mupen timing); statically grep the guest audio task setup (sym for osAiGetLength callers, constant 0xC0/192 near the mixer-frames argument) to split b vs c. Positive control: cycles/VI must equal ~781k (46.875MHz/60).
