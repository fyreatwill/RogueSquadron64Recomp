# NEXT: L4 21:9 mid-mission cutscene lower-right hole: name the writer (CURRENT-TRUTH item 35)
HYPOTHESIS-ID: g3-219-cutscene-hole
State (s7165): event-triggered letterboxed cutscene on L4 (X-wing over water, ~190-300 s into a forced-level run, 4/5 runs). At 21:9 (dd1 and dd4)
for ~0.5 s the water right of the screen centre is neither cleared nor drawn (replay unpainted up to 27136 px). Not seen at 4:3 by eye. XFIX tog did not move the edge.
Hypotheses: H-clear (horizon clear rects at camera+0x7C..0x8B, writer 0x8005B51C, leave the lower-right uncovered in this camera under ASPECT; SKYFILL not reaching it),
H-cam (cutscene camera viewport/aspect widened differently from flight, s6104), H-terrain (water cells right of centre culled by the wide frustum / CULL_XFIX s7134).
Discriminator, ONE run with the RDP stream inside the cutscene: in the hole swaps, (a) the FILLRECT/clear rects the game emits vs the hole bbox, and
(b) whether water tris exist right of centre. Clear rect covering only x<centre and no tris -> H-clear; tris emitted but culled by our x-cull -> H-terrain (CULL_XFIX=0 arm);
camera+0x10 width / perspective aspect differing from flight -> H-cam.
Step 1 (engineering): the stream recorder can't hit an event-timed scene with a 12 s window. Add a ring trigger in src/rsp/dpc_bridge.cpp next to
ROGUESQ_G5B_FRAME_TRIG: ROGUESQ_G5B_FRAME_TRIG_WORD=<physaddr>[:<value>] fires when that RDRAM word changes (or equals value). Find the cinematic flag first
(updateCinematicCameraStateMachine / cutscenePopulateSlotsFromLevelLists writes; ROGUESQ_STORE_WATCH on candidate state words), or trigger on a
letterbox signature in the RDP ranges (full-width black FILLRECT at the top rows). Positive control: trigger fires at the cutscene start in a run where
tools/s7165_rawlb.py also finds it.
Step 2: tools/s7141_arm.zsh 4 <name> "ROGUESQ_ASPECT=21:9 ROGUESQ_DRAW_DISTANCE=1 ROGUESQ_G5B_FRAME_TRIG=4,400 <trigger>" 100 320, replay, s7165_letterbox.py, then inspect the clear rects
(tools/s7138_streamseq / s7133_rects.py on the hole swap). KEEP the .cap until the hole swaps are explained.
Owner save rule: NO_SAVE_WRITE stays, no SAVE_FROM. CURRENT-TRUTH ~59.7 KB (<60000): keep edits net-neutral.
Deferred: 21:9 flight sweep of the other 15 levels (item 34), same recipe as s7165 L1.
