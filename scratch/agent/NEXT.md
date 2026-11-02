# NEXT: G3 post-death screen vs retail (lvl9)
HYPOTHESIS-ID: g3-death-screen

State: every front-end menu, pause, debrief and LEVEL DESCRIPTION (lvl1, 13-16) match retail (s6778-s6803).
Gap: the screens after the player's death were never compared. s6763: in the lvl9 pinned pair the retail player dies by
itself (HUD-off death camera t2050-2208, retail 16/16 dumps); port also hid the HUD there. What comes next (respawn /
lives-left / MISSION FAILED / retry menu) is unscored.
Hypotheses: H-match (same screen sequence, static rect sets equal); H-diff-flow (port goes to a different screen or
respawns differently after death); H-split (the sim already split before death, so death timing differs - then align on
the death camera start, not ticks).
Discriminator, ONE pair run: tools/g3_mission/run.sh recipe from s6762/s6763 for lvl9 (scratch/s6763/lvl9_port.sh,
lvl9.eep = scratch/s6761/lvl9.eep), extended so both arms run ~60 s past t2208, with VIDEO=rdplog on retail and
RS64_RDP_BIN_PORT on the port (plus a few angrylion dumps in a 2nd run for a pixel crop of any text screen).
Score with g3_rdp_segments.py (texrect-count segments after the death camera) + g3_rdp_segcmp.py; positive control =
the pre-death flight HUD segment, cross control = death screen vs pause menu. Check ROGUESQ_LIVES_CAP is OFF in the port
arm (it changes lives handling). Do NOT poke damage/wins (G1(d) parked); rely on retail's natural death.
