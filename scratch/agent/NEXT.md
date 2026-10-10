# Next work unit: hangar framebuffer pixel-diff, port vs oracle (RDRAM dump, not Rice pixels)

HYPOTHESIS-ID: hangar-artifact-triage

s4505 finding: port hangar frame 1 is a nearly-correct scene (scratch/agent/s4505_port_hangar/f_001*.png);
defects: rainbow rim band, blue holo spikes, right-edge column garbage; later frame black + right-edge garbage.
Hypotheses: H1 colour/texture-format on specific materials; H2 bad geometry data (weakened);
H3 LLE ucode divergence; H4 framebuffer width/stride mismatch (right-edge garbage).
Discriminator: dump the 16bpp RDRAM framebuffer at VI origin 0x006AB400 at the first VI-512 transition from
(a) oracle (mupen RDRAM read in rs64_oracle.c; Rice only needs to drive the game, the framebuffer is read from RDRAM
    but Rice may not write RDRAM fb -> check; if it does not, this arm is invalid and the comparison must use
    display-list/texture-source bytes instead), (b) port. Positive control: same procedure on title VI 1024 (0x790400).
Run scripts: scratch/agent/s4505_port_hangar.sh as the port driver. One game run at a time. SIGKILL.
