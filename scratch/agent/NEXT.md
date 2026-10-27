# NEXT: phase-gated fixed-camera capture for G3c(a) edge arms
HYPOTHESIS-ID: g3c-edge-arm-route-gate

s6397: width-filtered re-score was not comparable (terrain_med 0.44 retail vs 0.035 dd2). Width is not a phase gate.
Work unit: in a run recipe, dump framebuffers only at VI count = (phase-5 witness + fixed N, e.g. 600 VIs) per arm (same level 1, same autopilot), and score a horizon-row profile (terrain/sky transition x-extent per column) instead of colour fraction. Positive control: dd2 must show a different far-extent than retail (it does by tri x2.3).
Outcomes: dd2 tracks combined, aspect tracks retail -> grid; dd2 tracks retail, combined tracks aspect -> aspect; aspect+combined shift vs both -> aspect side edge. Do not change runtime defaults.
