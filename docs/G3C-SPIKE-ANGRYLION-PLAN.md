# G3c(b) H-retail: angrylion replay plan (s6453)

Why: docs/G3C-SPIKE-REFERENCE.md said no LLE reference exists. That inventory missed
/Users/williambuckley/Documents/Tools/g3_angrylion (angrylion-plus mupen64plus plugin,
built clean s5963, used for the retail hangar/lvl1 pixel oracles). It is an accurate RDP,
so it can answer "does the hardware RDP draw a wedge with these coordinates?" - the only
part of H-retail the RSP replays (s6385/s6388) and the scissor model (s6441) cannot.

Hypotheses
- H-hw-draws: angrylion rasterises the logged wedge polygon -> visible lines on hardware too (retail-faithful; ask owner about CULL_SPIKE default).
- H-hw-clips: angrylion draws nothing/less than the s6441 model predicts -> hardware discards it (RDP edge-walker coordinate limits), RT64 differs -> fix RT64/host-side cull.

Discriminator: take one logged [spike] polygon (5 edge vertices, tools/g3c_spike_rdp_model.py
parser), encode as an RDP fill/shade triangle command pair (edge coeffs, s15.16 X, s11.2 Y)
inside a scissored 320x240 frame, run through angrylion's rdp core, count lit pixels.
Positive control: a sane in-screen triangle in the same harness must light pixels;
the s6441 model's prediction for the same polygon is the comparison value.

Not done in s6453 (planning only).
