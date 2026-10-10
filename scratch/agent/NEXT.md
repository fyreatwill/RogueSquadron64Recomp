# Next work unit: exact F5 vertex byte range, then re-compare static blobs c08-c10

HYPOTHESIS-ID: hangar-artifact-triage

s4511: dumped 0x400 B at each child-DL op01/02/04/fd target (scratch/agent/s4511/). fd blob identical; the six within-side-static blobs (c08,c09,c10 x op04/op02) differ cross-side (174-298 B, first diff at offset 6-14), but the window includes display-list residue and the F5 Vtx/VertexColor layout and length are unknown.
Do: (1) find the F3DSWRS_Vtx / VertexColor handler (lib/rt64 GBI_F3DFACTOR5, or docs/F5-UCODE-REFERENCE.md source refs; GLideN64 F5Rogue.cpp is not on disk -- grep lib/ for F3DSWRS / FACTOR5) and derive record size and how op04 w0 (0x04000c1f) encodes count/offset. (2) Re-run scratch/agent/s4511_cmp4.py restricted to that byte range for c08-c10 (existing dumps; rerun hooks only if 0x400 B is too short).
Outcomes: exact range identical => H2' dead for static blobs, go to renderer/ucode (H1/H3); exact range differs => trace the writer of that range (oracle write watch at the physical address, positive control = whole-RDRAM watch).
Note: tasks 1/2 are timing-dependent; compare t0 only, and only blobs static within-side.
