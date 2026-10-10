# NEXT: with the skip on, find why hangar is never reached (arm A alive at phase 9, hangar=0 after 400 s)
HYPOTHESIS-ID: m5-audio-destub
Established (s4564): skip-on survives 400 s with 0 crashes; skip-off crashes 36x (first: zcfree <- inflate_trees_free).
Hypotheses: H-stall-audio (a wait on audio slot/status never completes with synth skipping), H-route (autopilot recipe never reaches hangar, unrelated to audio), H-gpu-path (hangar gating in graphics).
Discriminating step: re-run arm A only at 400 s and track VI count and phase over time (does VI advance or stall?); grep arm A for waitForAnyAudioSlot-style loops. Make the skip default-on only with an ORIGIN line.
