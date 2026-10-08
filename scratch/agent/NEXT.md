# Next work unit: phase-split RT64 send_dl (s4267)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4266: single-arm run reproduces the send_dl stall (t=20–26 s, 0.15–0.9 s/task), so 2-instance GPU contention (G2) is refuted. Remaining: (G1) first-use Metal pipeline/shader compile; (G3) texture upload burst; (G4) present/vsync wait; (G5) CPU-side DL processing growth in RT64.
Discriminator: ONE build with per-second aggregate timers inside RT64 send_dl (lib/rt64): pipeline/shader create, texture upload, draw submit, present wait, plus counts of pipelines created. Run single arm via scratch/agent/s4266_single.sh. G1 predicts time concentrated in pipeline create at t=17–26 with a pipeline-count burst; G3 upload; G4 present; G5 none of those but total dominated by DL parse. Positive control: healthy seconds t=9–14 must show nonzero in the phases that run each frame (submit/present).
After editing lib/: ./submodule-patches/export.sh and commit.
Also decide: if purely host-renderer, re-rank M5 de-stub steps (audio gap is not an M5 defect).
