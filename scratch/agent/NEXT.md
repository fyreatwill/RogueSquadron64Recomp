# Next: does mission flight code react to the (now located) stick input?
HYPOTHESIS-ID: m6-mission-input
H1: ship state words (position/velocity floats) change in response to stick y=127 at 0x80130B8B. H2: input reaches the struct but flight code is gated off (byte 0x80130B56 != 0 disables readControllerInputs, or the mission is a non-interactive demo).
Discriminator (ONE run): per VI log rdram[0x130B56], [0x130B88..0x130B8D] and the candidate flight float cluster (s5074 candidates 0x9DEAC, 0x10C0F0..0x10C340), phase-gated at origin 0x620400, windows no-key / W hold / no-key in the same run. Positive control: 0x130B8B must read 0x7f during the hold. H2 is indicated by 0x130B56 != 0 or floats unchanged while 0x130B8B=0x7f.
Reuse the scratch/agent/s5069_mission_snap.sh route (file-injected pad override keys). Do NOT repeat whole-RDRAM diffing. Mission onset ~170-260 s; 600 s cap.
