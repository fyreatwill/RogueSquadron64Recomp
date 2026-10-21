# M6 s5759 — the bit1 "spawn" event is the post-death respawn request (static read + s5757 log)

Source: /private/tmp/s5547/ctl/funcs_30.c, funcs_42.c (recompiled comments); scratch/agent/m6/s5757_bit1ctx/run.log.

## Chain (each link read from code)
1. updatePlayerCraftPhysics dispatches on a per-slot state halfword (`lhu -0xD0(slot*0x2A0+0x8013 8004...)`, slot = craft+0xB8):
   bit 0x8 -> 0x800B0A88 (+ exit); bit 0x10 -> 0x800B1024 (call site 0x800B1EAC); bit 0x20 tested next. (bits 0x8/0x10 look like exploding / settling states.)
2. 0x800B1024 (placeholder name computeOrientedTransformFromQuat; really a death-settle tick): craft+0x184 (float) -= dt;
   while >0 it runs the 0x800B1144 tail; at <=0 it sets craft+0x180 |= 0x100, clamps y onto terrain (0x80067D90), and — if the phase word
   0x8010CA20 == 0 — ORs **bit1** into the event mask 0x8010C9E0 (pc 0x800B1140, delay slot of `j 0x800B13C4`) and records slot byte in 0x8010C9E8.
3. runInMissionFrame event table 0x8010B350: id1/id2/id3 -> requestMissionTransitionMode (0x800FB190). Bit1 -> mtm(a0=1) = the DEATH path:
   `lives[0x80130B10+slot]--`; nonzero -> cue 0x37, phase 1 (respawn timer); zero -> mode byte 0x80130B14 = 3 (game over) and mask |= bit0 (pc 0x800FB2B0, val=3).
4. s5757 run.log: 3 bit1 events per mission cycle (717109, 721284, 725939), the third followed at 725967 by `[mtmst] 0x800FB2B0 val=3` = lives 3->0 game over. Matches
   the s5738 finding (lives start 3, one per death).

## Verdicts
- s5758 "bit1 = benign player spawn event; terrain sane" is WRONG in its label: terrain sanity is just the settle clamp; bit1 is the death-settle completion -> life lost. (Superseded.)
- 0x800FB2B0 val=3 = lives hit 0 (game over), NOT mode-3 results/success. H1 (real mission-end by success) refuted for this run; fail is the game's own game-over after 3 deaths.
- 0x800EE85C val=0x100 (tickSongFadeTimer) is followed immediately by the normal FA844 clear; unrelated to death, no gate seen (single-source).
- The open question is unchanged from s5738 but now narrowed: WHO sets state bit 0x8/0x10 in the slot table (the kill source), ~7.5 s after each respawn, while the plain route (s5742) has no deaths.
