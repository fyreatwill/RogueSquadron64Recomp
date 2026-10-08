# Next work unit: name the ~50 tracked framebuffers behind the RT64 stall (s4269)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4268: stall = State::checkRDRAM hashing (XXH3) a framebuffer set that grows 3 -> 56 (1.8 MB -> 13 MB/call). Not audio.
Hypotheses: (A) bogus color-image sets from the LLE stream at wild addresses create entries (cf. 0x1F0D74 width 1161); (B) legit per-effect framebuffers that retail also tracks but never prunes; (C) entries are depth/aux buffers duplicated per address alias.
Discriminator: one-shot dump at ~28 s of framebuffers map (address, width, height, RAMBytes, lastWriteFmt) via ROGUESQ_S4268 extension at framebuffer_manager.cpp:95 creation site (log creation with address/width/size/DL), single run; then compare to expected 2-3 color + depth. Positive control: creation log must show the initial 3 entries at t~3 s.
Decision: if A, name the writer (ORIGIN) in the LLE color-image path; if B, add prune in lib/rt64 (export.sh + commit).
Then resume re-ranking M5 steps (docs/M5-AUDIO-PLAN.md).
