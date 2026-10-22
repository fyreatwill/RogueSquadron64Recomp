# NEXT: G1 - s5872: what kills the autopilot ship (3x requestMissionTransitionMode a0=1 = death path, s5871)?
Hypotheses: (a) enemy fire/collision with terrain, (b) autopilot flies into scenery/ground, (c) fall-out/out-of-bounds kill. Discriminator: at each a0=1 call log lives byte 0x80130B10+[0x8010C9E8], player hp, position (PLPOS) and the last damage source; arm B: player god mode (poke hp each frame) - if mission survives past VI 15987 the cause is damage, else a different end path.
Extend tools/apply_s5847_mask_log.py [m47] with lives+hp, regen order make_elf->N64Recomp->fixup->cmake, queue as soak.
HYPOTHESIS-ID: g1-mission-progression
