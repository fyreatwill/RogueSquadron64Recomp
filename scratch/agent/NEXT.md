# Next work unit: decide whether the 16-buffer periodicity in audible PCM is a genuine musical loop (s4244)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4243: no consecutive repeats (stall refuted); identical FNV recur at 16/32-buffer spacing at the same ring address; PCM at scratch/agent/soak_results/s4243_stage/pcm.raw (stereo s16 LE).
Hypotheses: (a) legit loop/sequencer repeat; (b) stale ring contents re-DMA'd because ucode did not rewrite a ring slot.
Discriminator: log, per ring slot, whether ucode wrote it between consecutive queue calls (compare FNV of ring slot at queue time vs. FNV at previous queue of same slot AND the AI-DMA ordinal); same-run control = slots known to change. Also compare against retail oracle if reachable.
Run: zsh scratch/agent/s4243_stage.sh (flags in main.cpp queue_samples under ROGUESQ_S4242_CTRL).
