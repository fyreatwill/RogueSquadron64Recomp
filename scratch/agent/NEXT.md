# NEXT: G1d step 38 - find the real flight-HUD x writer
HYPOTHESIS-ID: g1d-widescreen
s6145: ROGUESQ_HUD_DX only moves subtitles (linkHudNodeAndComputeScreenPos). Flight HUD = mesh nodes/matrices from initHudStruct (0x800C0084, funcs_33.c:6314), HUD structs D_8010CA30[2] (0xF80 B each).
Hypotheses: H-node (per-element node x at struct offsets +0x18/+0x1C etc. written in initHudStruct; shift there per anchor), H-matrix (single HUD ortho/projection matrix built once per HUD pass; one translate shifts all, but then right-anchored vs left needs scale: x' = x*k about centre instead), H-mesh-verts.
Discriminator, one build: log (once per VI) every store into D_8010CA30..+0x1F00 with pc, plus a "mark everything" control that adds +160 to the float at every logged store target; HUD must visibly move in the fb dump (positive control) before any conclusion. Then pick H-node vs H-matrix by whether all HUD elements move together.
Recipe: scratch/agent/s6144_run.sh pattern (21:9, OSMEM 12, ROGUESQ_FB_DUMP_VI=1); runs take ~100 s hold but harness wall time ~5 min each; run in background, one game at a time.
