# NEXT (s7912)
HYPOTHESIS-ID: g3-m6-island-b-state
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED' | head`, docs/OWNER-REVIEW-QUEUE.md answers,
new SOAK-RESULTS lines. A crash or owner report outranks this.
State (s7911): pre-flight census H-mixed. m6 island B (port 6071:6283 on scratch/s7896/m6q, text-screen tail, PRIM FFFFFFFF tris,
6 -> ~80 differing tris) re-locks at the SAME lag (532) after the island (tools/s7911_island_relock.py), is not a half-frame
phase (tools/s7911_island_phase.py, control PASS) and survives full rand-value replay (s7896). So it is game state.
Hypotheses:
- H-callcount: advanceNpcOnCurvedPath (0x8006C0FC) steps a different number of times pre-tick (s7896: run lengths 81 vs 80,
  71 vs 69), so a curved-path NPC/element sits elsewhere when the text screen draws it.
- H-init: the element's state is initialised from something that differs (camera/pose word, scene timer) before the screen.
- H-order: same calls and values, different interleaving between update sites (s7896 saw interleaving diffs in m11).
Discriminator (one oracle run + one port run, or offline first if possible): identify the element (which display list / object
emits the PRIM FFFFFFFF tris: grep RDP bins' setPrim context, then the guest object via ROGUESQ_G3C_CAMLOG/RAMDUMP), then a write
watch on its position/path-parameter word on both sides (retail oracle --watch-write PHYS, port XTRACE_MEM at 0x8006C0FC) across the
text screen. H-callcount: same per-call values, different call totals; H-init: values differ from the first call; H-order: totals
equal, sequence differs. Offline prerequisite: find what the xtrace 2nd field is (not VI: retail rand rows 422..18299) so the two
sides' rand rows can be aligned on a shared clock; tools/s7896_rand_replay.py uses [vi] t= lines instead.
Bins (cite exact paths so the prune keeps them): scratch/s7896/m6q/r1/retail.bin.zst, scratch/s7896/m6q/p1.bin,
scratch/s7896/m6q/p1_rand.txt, scratch/s7896/m6q/r1/oracle.log.zst.
Budget: if 2 iterations give no discriminating result, record the table and take the next ladder rung (owner queue / G1e).
