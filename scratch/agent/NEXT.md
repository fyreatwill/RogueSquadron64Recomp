# NEXT: G3 hangar artifacts under wide aspect (s6601 item, parked single-source)
HYPOTHESIS-ID: g3-hangar-artifacts

Context: s6839 closed g3-retail-match-lvl3 (stale: the per-mission sweep 1-19 is complete, s6777) and fixed the oracle
cfg leak (every retail run now prints `[oracle] save dir:`; check it). Every retail arm must use --save-dir with a private
copy of the save (tools/g3_mission/run.sh style), never a copy over the user-wide .eep.
Unit (PROJECT-OVERVIEW s6601 item, grep "g3-hangar-artifacts"): one same-phase capture table at the hangar origin for
retail 4:3 (oracle angrylion, --save-dir), port 4:3, port ROGUESQ_ASPECT=16:9 and 21:9. Build all arms in one iteration;
run the port arms one at a time.
Hypotheses: H-viewport (wrong scissor/viewport exposes the rim band), H-stride (wide fb row/flip stride leaves stale
right-edge data), H-rdp (RT64/RDP edge treatment makes the holo spikes), H-game (retail 4:3 shows the same artifact).
Discriminator: the artifact's first/last changed pixel bounds per arm plus command-range attribution in the same phase:
width-proportional stale bands -> H-stride; fixed screen-space clipping -> H-viewport/H-rdp (split by the RDP stream,
tools/g3_rdp_frame_match.py); present in the retail control -> H-game. Owner-viewable contact sheet before any change;
defaults stay retail.
