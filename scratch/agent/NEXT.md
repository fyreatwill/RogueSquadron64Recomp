# Next: fold s6311 edgefade soak, then implement ROGUESQ_EDGE_FADE distance fade
HYPOTHESIS-ID: g3c-owner-visual
Read scratch/agent/SOAK-RESULTS.md tail for s6311_pos / s6311_test02 (logs in scratch/agent/m6/s6311_g3c, FB dumps from the runner).
1. Positive control: test02 (RGB x0.2) FB dump must show visibly darker terrain vs pos arm. If YES -> 0x8004B644 colour reaches the Vtx; go to 2. If NO -> find the copy from the 0x80137A50 array into Vtx (grep consumers of the 0x10-stride array, likely in the 0x8004C... builder) and hook there.
2. From [edgepos] lines: are pos x/y/z camera-relative? (look for min distance ~0 and monotone far extent). If not, find the camera global from the footprint code at 0x80043868 (0x2C($s1)-0x1C($a1)).
3. Implement ROGUESQ_EDGE_FADE=<cells> in tools/apply_s6311_edgefade.py: scale RGB toward fog colour by distance ring; 3-arm dd3 soak (none/fade4/fade8) scored with tools/g3c_edge_score.py.
Also ask owner re ROGUESQ_CULL_SPIKE default (G3c b).
