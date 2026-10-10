# NEXT: renderer-side check of hangar white pillar stubs / right-edge strip

HYPOTHESIS-ID: hangar-artifact-triage

s4520: aligned port frame 910 == retail frame 0 for 1246/1249 tris (all words), so stubs and right-edge strip are NOT RSP/stream defects. Hypotheses: (A) genuine retail look; (B) RT64 combiner/texture-format/blend handling of those tris; (C) RT64 output scaler cropping at the right edge.
Work unit: find the stub tris (screen x~85-155,y~585-650 of 1280x1024 window => N64 x~35-60, y~..) in port_rdp.bin frame 910, extract their combiner (setcombine) + texture tile state, and render with RT64 combiner override toggled/ compare against a hand-evaluated combine; for the strip, check RT64 VI crop/scale code path vs VI width 512.
Discriminator: if hand-evaluated combine yields white too => A (stop, hangar considered fixed); if not => B, name the RT64 handler.
If no discriminator emerges in one iteration, mark hangar triage closed and pivot to M5/M3 audits per ITERATION.md priority.
