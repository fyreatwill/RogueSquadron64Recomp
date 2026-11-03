# NEXT: G3 NPC vehicle destruction explosions vs retail (lvl14 in-mission cutscene)
HYPOTHESIS-ID: g3-npc-explosion

State (s6811): the large destroyed-craft fireball (lvl9 player crash) is H-match vs retail angrylion in tick order
(tools/g3_mission/fireball_pair.sh, tools/g3_fireball_score.py; dense port capture = g3_port_capture.sh BURST=t0,t1 via
`winctl burst`, ~16 fps). NOT covered: an NPC vehicle destruction (explosionEffectNpcHandler / spawnNpcDestructionDebris
path may draw a different effect from the player-crash fireball).
Deterministic NPC explosions without aiming: s6767 lvl14 (lava planet, scratch/s6767/lvl14.eep, dt pinned) has an
in-mission cutscene t2628-2865 (HUD off, camera follows craft/explosions over the lava), sim identical to retail through
t2874. Ticks -> VI: t2620 retail VI 15379 / port 10196; t2860 retail 16153 / port 10676.
Hypotheses: H-match (same explosion sprites/sequence); H-blend (colour/alpha differs on the NPC explosion sprite);
H-anim (frame sequence/timing differs per tick).
Method: copy fireball_pair.sh with EEP=scratch/s6767/lvl14.eep (check scratch/s6767/port.sh + retail recipe for the
lvl14 PRESS/AP schedules), retail FARM so 192 dumps x 0.1 s cover VI 15379-16153 (oracle wall ~= VI/60, check the
vi-poll t= lines of an s6767 log), port BURST over port VI 10196-10676 (~170-178 s wall + boot offset; widen to 12 s).
Score: g3_fireball_score.py --scale 2 (4 vs 2 VI/tick) with --rvi on the cutscene window; also eyeball sheets.
Control: hot-pixel class must fire on retail explosion dumps; pair d vs median control; pre-explosion frames.
Aim/steer work is OUT OF SCOPE (ITERATION 3c G1).
