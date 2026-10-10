# Next work unit: hangar geometry/colour artifacts (from CURRENT-TRUTH "Current state")

HYPOTHESIS-ID: hangar-artifact-triage

Goal: localize the first divergence between the port and the oracle in the hangar
scene (VI 0x006AB400, VI 512). Competing hypotheses: (H1) RT64/RDP state or
texture-format handling (colour), (H2) wrong/missing geometry data from a
recomp'd loader or stubbed DMA/audio side effect, (H3) RSP gfx ucode path
(LLE) divergence. Discriminator: one capture, analysed offline. Dump the hangar
frame's display-list / RDP command stream (or framebuffer) from the port at the
first hangar VI transition, and the same from the oracle (use its --video plugin,
see its --help), phase-gated on the VI transition — no cross-run A/B on
animating frames. Positive control: title VI 1024 frame must match between the
two in the same tooling. One game run at a time; SIGKILL to stop it.
Check prior notes first (grep -i hangar docs/CURRENT-TRUTH.md PORTING-STATE.md).
