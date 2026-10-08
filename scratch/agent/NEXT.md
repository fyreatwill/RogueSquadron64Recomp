# Next work unit: why is RT64 send_dl slow (0.2–0.9 s/task) in t≈17–31 s (s4266)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4265: gap seconds = send_dl on Gfx thread slow (both arms), audio SP tasks 0.2 ms. See PORTING-STATE s4265.
Hypotheses: (G1) first-use Metal pipeline/shader compilation in a new scene; (G2) two concurrent game instances contend for the GPU (the gate runs 2 arms); (G3) texture/upload burst; (G4) present/vsync wait.
Discriminator: run ONE arm alone (copy s4265_gate.sh with a single arm) — G2 predicts the stall vanishes/shrinks; if it persists, time send_dl phases inside RT64 (pipeline creation vs upload vs present) in one build; G1 predicts slowness decays after first appearance of each scene and shows in pipeline-create timing.
Also decide: if the stall is purely host-renderer, the "audio gap" is not an M5 defect — re-rank M5 de-stub steps accordingly.
