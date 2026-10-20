# NEXT (s5682): per-VI dump of ship object 8034f680 +0x4C..0x54 and record 0x137DB8 +0xD0..D8
s5681 selected 8034f680 (+0x4C/50/54) as position candidate; 1 Hz sampling too coarse (c<=0.28). Add ROGUESQ_PLAYER_DUMP=2: every poll (not 1 Hz) for 150 polls print pos vec3 + vel vec3 + stick. Discriminator: |corr(delta pos, vel)|>0.9 -> integrator confirmed, altitude=+0x50; <0.3 at frame rate -> vel is not world velocity, try +0xDC/E0-driven or oracle watch.
HYPOTHESIS-ID: g1-mission-progression
