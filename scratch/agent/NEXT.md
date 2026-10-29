# NEXT: split actual GPU shader inputs from blend/attachment output
HYPOTHESIS-ID: g1d-levelselect-texel

s6622 locates the tear BEFORE native conversion. Do not repeat GPU/native/RAM
localization or CPU plane scalars. Evidence scratch/agent/s6622_pipe/verdict.json;
owner sheet docs/owner_sheet_s6622_pipe.png. Single-source runtime result.

ONE work unit: actual GPU floor-fragment value table plus bound texture snapshot,
from the same captured draw/frame. Hypotheses:
- H-binding: GPU sampled texture/binding/format differs from the intended I4
  TMEM decode (RGB channels should be equal before shade). A non-grayscale
  texVal0 or a bound-texture mismatch selects this, name upload/binding writer.
- H-shader: sampled texture is correct but actual interpolated UV/shade or
  combiner/blender evaluation diverges from the logged mesh/CPU walk. Select
  the FIRST divergent GPU field, name its producer; do not guard the output.
- H-backend: actual shader pre-attachment result is sane but the final GPU
  target contains rainbow rows. Inspect dual-source blend factors, pipeline
  format/attachment state, shader specialization, and resolve/downsample
  operations for that draw. The s6622 GPU snapshot is AFTER resolveTarget,
  not a readback of the original multisampled attachment.
- H-witness: stage/draw/pixel keys fail to join, or known GPU pattern cannot
  be recovered. Repair the control in this iteration before using nulls.

Ground truth first: docs/F5-UCODE-REFERENCE.md and independent paraLLEl-RDP
reference linked in tools/g1d_floor_mesh.py. Inspect existing shader/descriptor
and debug-output facilities before adding any. The GPU target is RGBA16 UNORM,
scale 1; source height 339, VI crop 336. Integer FbWriteColorCS.Load sampling.

Complete table in ONE instrument/build, not one field per iteration: submission
frame + framebuffer address + pair + draw/triangle id + pixel x/y; actual UV,
vertexSmoothColor/selected shade, tile/gpuTile/texture ID and format, sampled
texVal0 RGBA, combinerColor, Blender::run resultColor/resultAlpha, and final
attachment RGB. Read back the ACTUAL bound texture with s6622 blit support.
Instrument only the two floor columns rows 180..250 and the known checker,
with per-phase budgets. Preserve primitive last-writer order: overlapping
fragment writes to one unordered record are NOT a valid last-writer witness.
Use per-primitive records or replay same-frame draws to scratch targets if
needed; do not infer GPU values from another CPU formula. No extra baseline
soak or repeated coverage sweep.

Anchors:
rg -n 'sampleTexture|shadeColor|combinerColor|resultColor|resultAlpha' lib/rt64/src/shaders/RasterPS.hlsl
rg -n 'padding|renderIndex|set.*Descriptor|shader' lib/rt64/src/render/rt64_framebuffer_renderer.cpp
rg -n 'floorSerial|floorGPU|captureFloorRAM' lib/rt64/src/render/rt64_native_target.cpp
rg -n 'textureCache|gpuTile' lib/rt64/src/render/rt64_framebuffer_renderer.cpp

Positive control: known GPU-uploaded checker must survive texture snapshot AND
actual shader sample/output witness; controls must exercise the new path,
not just a fabricated host array. Retain existing same-run tear and floor
controls. The existing ROGUESQ_FLOOR_PIPE_DIR checker changes x/y32..39 on
purpose; keep it off in ordinary play.

Exact baseline verification/run commands (adapt scorer only for new fields):
python3 tools/g1d_floor_mesh.py --selftest
cmake --build build --target RogueSquadron64Recomp -j 5 > scratch/agent/s6623_build.log 2>&1
python3 tools/g1d_floor_pipe.py
The runner currently roots at s6622; add an output-root parameter or change
it to s6623 BEFORE running to preserve s6622 evidence. It runs both width
arms sequentially, checks screen lock, uses phase input, and SIGKILLs.
python3 tools/g1d_floor_pipe.py --analyze
./submodule-patches/export.sh

A discriminating field must select H-binding/H-shader/H-backend. A table of
only pipeline IDs or CPU reconstructed values does not finish this unit.
Defaults remain retail; no mitigation without naming the writer.
