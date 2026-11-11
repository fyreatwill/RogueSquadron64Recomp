# NEXT: name the writer of the flight camera's partial background-clear rects (21:9 side-band holes, CURRENT-TRUTH item 29)
HYPOTHESIS-ID: g3-owner-recipe-219
State (s7132): at 21:9 (L6 FPS60 dd4) one 1.1 s banked-wall burst (swaps 7524-7591) leaves pixels that neither the clear nor geometry
covers. The clear list is camera 0x80138D18: +0x74 count, +0x78 ptr -> 0x80138D94 u16 rects {x0,y0,x1,y1} in 1024-px screen space,
consumed by emitFrameRdpInitDl (0x80008D20, rect list at *(0x801142C4), null = full viewport). No direct store to 0x80138D94 exists.
Hypotheses: H-xscale (the writer projects the horizon or split with the 4:3 x-scale, so it is only wrong when rolled), H-clamp (it
clamps to a 640/4:3 width or to the unwidened viewport), H-retail (the same estimate also leaves holes at 4:3 in this pose; check the
rects vs the drawn coverage at 4:3 in the same burst).
Discriminator, ONE build: a store watch in the apply_s5798_recwatch.py pattern on [0x80138D90,0x80138DB0) -> pc, function, guest ra, plus
the camera roll and the written rects per swap. Positive control: the logged rects must equal that swap's FillRects in the stream
(tools/s7132_tricover.py / the /tmp-style rect census; s7132 saw {468,0,1023,447},{0,113,467,447} at swap 7800).
Then read that function. If it uses the 4:3 scale, scale it by ROGUESQ_ASPECT_SCALE behind a default-on knob (=0 restores retail), and
re-run tools/s7132_arm.zsh (21:9, same env as s7132). Pass = 0 swaps with >3000 unpainted px in the replay, frac>40 at the 16:9 floor.
Re-analysis data: scratch/s7132/L6w.cap (12.6 GB) + L6w.raw + L6wr/ replays; delete them once the fix is qualified.
Regen order applies to any patch (fixup scripts). Owner save rule applies. CURRENT-TRUTH ~59.6 KB: keep edits net-zero.
