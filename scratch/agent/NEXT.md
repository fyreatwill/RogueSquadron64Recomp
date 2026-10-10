# NEXT: explain port-vs-retail hangar RDP stream difference (195 texrects vs 0; ~1125 vs 1244 tris)

HYPOTHESIS-ID: hangar-artifact-triage

s4515 result: port hangar sync = tris~1125, texrect 195; retail = tris 1244 (0x0D x275, 0x0F x969), texrect 0. Title control matched (161 texrects).
H1a: scene-state difference (our route's Starts bring up a UI overlay retail lacks at VI-512 entry) vs H1b: ucode/DL path divergence.
Discriminator: dump the port's first sync after VI 512 with a per-opcode histogram split by type (0x0D vs 0x0F, texrect), and run retail (oracle) with the same Start key schedule so scene state matches; diff the RDP bytes offline against rs64-oracle/s4514_rdp_hangar512.bin.
