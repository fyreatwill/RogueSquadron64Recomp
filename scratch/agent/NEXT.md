# NEXT: G3 AT THE MOVIES TRI excess on shots 48/64 (port emits ~30% more RDP tris than retail)
HYPOTHESIS-ID: g3-cinematic-sweep

State: s6792 paired all 81 shots; s6794 fixed the sky seam (ROGUESQ_EXACT_EDGES default on). Open flag from s6792 sweep:
shots 48 and 64 have retail tri median 914 / 772 vs port 1188 / 846 per frame (scratch/s6792/mov/retail.bin vs port.bin,
tools/g3_cine_sweep.py sweep_vi.txt). Note: RDP dumps are taken before RT64, so the s6794 fan does not change these counts.

Hypotheses:
- H-lod: port picks a higher model detail (LOD index 0x80137CE4 / selectMeshLodAndSubmitForRender) in those shots; extra tris
  are a different mesh of the same object (per-frame tri x/y bbox clusters match, densities differ).
- H-dup: port submits a gfx task/DL twice (or a chained sub-DL repeats) in some frames; extra tris are exact duplicates of
  edge words already in the same frame.
- H-clip: port's LLE clip path splits near-plane tris more (more small tris near screen edge / at w~0), retail fewer.
- H-timing: frame pairing mismatch (port 30 fps vs retail 11-21 there) makes medians compare different content; counts
  equal when aligned on the same camera.
Discriminator (OFFLINE, no build): for shots 48/64 take 20 aligned frame pairs (tools/g3_cine_sweep.py alignment), and per
pair compute (a) duplicate-edge-word count within the port frame, (b) tri bbox histogram by screen region and size,
(c) fraction of tris touching the screen/scissor edge. Dup>0 only in port -> H-dup; same regions but smaller/more tris ->
H-lod; excess concentrated on edges -> H-clip; excess vanishing under re-alignment -> H-timing. Positive control: a frame
duplicated artificially (concatenate a port frame with itself) must read dup = 100%.
