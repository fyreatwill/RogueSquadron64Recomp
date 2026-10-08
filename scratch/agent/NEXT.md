# Next work unit: name the writer of the wild pointer at the t~28s fillSampleStreamRange crash (s4253)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4252b: private-DMEM crash B 3/6, silent-ucode C 3/6 -> ucode-independent (c1 refuted). Crashes cluster at 27-28s fillSampleStreamRange (4/4 in one wave, 0/4 in another) plus one RT64 copyToRAM at 15s.
Hypotheses: h-a guest-side sample-stream state (voice array) corrupted by non-audio writer at phase transition; h-b RT64 copyToRAM/vertex cache writes into guest RDRAM (cross-thread); h-c shared timing (wave-level correlation: load on host).
Discriminator: use tools/apply_s4230_listwatch.py / write-watch on the faulting pointer's source in a B arm; also compare crash with ROGUESQ_AUDIO_PRIVATE_DMEM=1 and sample-stream fill disabled entirely (skip fillSampleStreamRange): if crash migrates elsewhere at ~28s, trigger is phase event, not audio.
Harness: env OUTN=c TAG=_N ARMS="B1 B2 C1 C2" zsh scratch/agent/s4252_ab.sh ; python3 tools/s4250_summarize.py ...
