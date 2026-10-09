# Next work unit (s4435): does the queued title PCM reach the SDL device intact?

HYPOTHESIS-ID: m5-pcm-nonzero-source

s4434: nonzero PCM (rms 2-6k) reaches queue_samples in title; counts setnext==queue.
Hypotheses:
- H-sdl-drop: SDL_QueueAudio/device drops or underruns (queued size, device format/freq mismatch vs osAiSetFrequency).
- H-content-wrong: PCM nonzero but differs from retail (wrong voice/instrument data).
- H-audible-ok: device path fine; M5 title audio works.
Discriminator: one run, same recipe as scratch/agent/s4434_port/run.sh, logging SDL_GetQueuedAudioSize before/after each queue, device spec (freq/format) vs ai freq, and dump 5 s of PCM via ROGUESQ_S4243_PCM for spectral sanity; oracle arm for content if driveable.
