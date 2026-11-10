# NEXT: owner reports first; otherwise RT64 vs angrylion on the exact forwarded RDP stream (layer below the bridge)
HYPOTHESIS-ID: rt64-vs-angrylion-stream
Context: the bridge is closed end to end (s7095 DPC registers, s7096 forwarding = hardware byte stream, s7097 every edit is a
documented walker edit, 0 unattributed). So any G5b terrain drop the owner still sees at dd2/dd4 is either already in the RDP
stream the ucode emits (game/ucode side) or in RT64's rendering of a correct stream. Nothing has compared RT64 output with a
reference RDP on the SAME dd4 stream (s6744/s6748 angrylion matches were retail-ROM frames at dd1).
Hypotheses: H-stream (frames with missing terrain already lack the terrain triangles in the forwarded stream; angrylion
replay of the stream shows the same hole) vs H-rt64 (stream carries the triangles, angrylion draws them, RT64's presented frame
lacks them: RT64 framebuffer/depth/tile-cache or present-selection defect) vs H-none (no frame in the capture differs beyond
the A/A floor: the owner's drops are not reproduced by this recipe; report and ask for a screen recording timestamp).
Unit (ONE capture, offline analysis):
1. Capture: L6 (and L4) dd4 16:9 owner recipe with ROGUESQ_G5B_FRAME=<file> (dpc_bridge.cpp rs64_g5b_frame: per swap marker,
   RAM every ROGUESQ_G5B_FRAME_EVERY swaps, every forwarded range) plus the presented-frame capture (scratch/s6894/g5b_capture)
   in the same run.
2. Replay each RAM+range frame through tools/angrylion_replay/replay.c; score terrain pixel fraction per frame for angrylion vs
   RT64 presented (same VI swap number); flag frames where RT64 < angrylion by more than the A/A floor (replay a frame twice = 0).
3. Positive control: drop one terrain triangle range from a replayed frame; the scorer must flag it.
Outcomes: flagged frames = H-rt64 (bisect RT64 state for that frame); holes in both = H-stream (go upstream into the ucode/game
terrain submit); no flags with a passing control = H-none.
