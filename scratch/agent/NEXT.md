# NEXT: do hangar draws on colour target 0x656000 (512 wide) ever cover x=511?
HYPOTHESIS-ID: hangar-renderer-artifacts

s4640: col 511 is writeback-stable at 0x656000 (changed 0 rows after first call) while col 510 converges; other targets do change col 511 (control). Selects H-native-unrendered.
Hypotheses: H-scissor (SETSCISSOR xl <= 511*4 excludes x=511), H-viewport (viewport/ucode projection ends at 510), H-seed (native col 511 only seeded by copyRAMToNative; draws do cover it but are fully transparent/alpha-killed there).
Discriminator (one build, one run): at the 512 writeback site also log the max drawColorRect right edge (fbPair.drawColorRect) and the scissor rect of draws into 0x656000; positive control: the same log for 0x7AB000 must show right edge >= 512. Outcome: right edge <=511 => H-scissor/viewport (then read SETSCISSOR source in the hangar DL); right edge >=512 => H-seed (inspect shader/alpha at col 511).
Tools: scratch/agent/s4640_wbcol.sh (copy, add env), lib edits need submodule-patches/export.sh + commit.
