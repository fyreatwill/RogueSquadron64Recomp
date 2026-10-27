# Next: implement radius edge-fade in the 0x8004B910 hook and compare frames
HYPOTHESIS-ID: g3c-owner-visual
State (s6324): lit-vertex pos (x,z at 0x48/0x50($sp)) is in cam*0.5 grid frame (camera x,z floats at *(0x80138D1C)+0x4C/+0x54). Radius max dd1 19.5, dd3 26.1 (p99 17.7/25.2).
Hypotheses: H-fade-dark (scaling RGB toward black by radius ramp r0..r1 hides the jagged edge, matches fog being dark/haze) vs H-fade-fog (needs fog colour target, black visible as ring) vs H-edge-not-radial (edge is grid-aligned rectangle, circular fade leaves corners).
Work unit: add env ROGUESQ_EDGE_FADE_R0/R1 (cells) to the s6311 hook: scale = clamp((R1-r)/(R1-R0),0,1) using cam*0.5 centre; first measure full per-frame max radius (log max per build) in the same run as the fade arm. Arms in one script: dd3 no fade, dd3 R0=18 R1=26, dd3 R0=10 R1=26; fixed-camera ROGUESQ_FB_DUMP frames, compare far-edge rows. Positive control: ROGUESQ_EDGE_FADE_TEST=0.2 darkens whole terrain (already proven s6311).
