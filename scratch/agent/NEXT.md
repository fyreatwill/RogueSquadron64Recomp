# Next work unit: verify the queue_samples ^3 fix and the repeated-buffer oddity (s4243)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4242: queue_samples was byte-swapped; fixed. Hypotheses: (a) n=1616/1632 identical RMS = genuine repeat (underrun re-feed or ucode stall); (b) coincidence of steady tone.
Discriminator: run scratch/agent/s4242_stage.sh with per-buffer FNV in [s4242-ctrl] (log every buffer when RMS equal to previous); a repeated FNV on distinct DMA ordinals = stall. Also dump 5s of queued PCM to a WAV (capture path not starting with '.') and check spectrum for speech/music vs noise.
