# NEXT: compare emitted-mesh interpolation with the RDP coefficient walk
HYPOTHESIS-ID: g1d-levelselect-texel

s6620 completed the fill/alpha experiment. Both widths have one constant
fill word FFFCFFFC and alpha equation (0-0)*0+0. dA=0.08538 versus 0:
strict agreement fails, so verdict is unresolved. Do not silently relabel
it H-pipe. Shader source confirms shade alpha is unused by that equation;
this is single-source. The CPU coefficient walk is not necessarily what
RT64's emitted mesh interpolates at the actual framebuffer pixels.

ONE whole discriminator, not another scalar per iteration. Before building,
read decodeTriangles vertex construction and shader interpolation, then
consult an independent RDP triangle specification/reference (existing local
reference first). State which interpolation model is required by that
reference. Do not treat our shader as the independent witness.

Hypotheses:
- H-mesh: triangulation/perspective reconstruction differs from the original
  RDP edge coefficients at 1024 only. Actual emitted vertex interpolation
  introduces the row step before the pixel pipe.
- H-pipe: the emitted mesh and original coefficients agree, but observed
  framebuffer steps do not. Raster/texture/blend backend remains the target.
- H-witness: sample-to-command/frame association or coefficient interpretation
  was wrong; the supposed agreement across widths was an instrument artifact.

Log the WHOLE necessary table in one build: width, VI origin/frame boundary,
RDP command ordinal and coefficients, all emitted vertex xy/w/uv/RGBA for
that primitive, triangle topology, viewport/scissor, effective sampler,
combiner and blend/coverage flags. Include only the phase and sample-crossing
floor primitives, preserving command order. At x=16 and x=w-17, y=180..250,
reconstruct the last covering emitted triangle and its perspective-correct
UV and shade. Compare to the original coefficient walk and framebuffer
steps in the same phase. Include the exact vertex-position transform used
before rasterization; do not compare normalized coordinates to source pixels.

Positive controls: synthetic mesh with known interpolation; perturb one
vertex's W/UV so the scorer visibly detects a row step, and verify values
at vertices. Retain I4 and alpha/fill selftests, original sample totals,
lastF/touchR/over=1, touchU=0, and same-run visible tear at 1024 and smooth
796 pixels. Null backend verdict is invalid unless all controls pass.

Discriminator:
- A 1024-only >2x reconstructed row step absent in the coefficient walk
  selects H-mesh. Name the responsible vertex-construction expression.
- Mesh/coefficient agreement within 25% on both widths with the reproduced
  pixel tear leaves H-pipe, explicitly single-source until independent replay.
- Failure to match commands, coverage or phase selects H-witness; correct
  the association in this iteration rather than concluding from a null.

Baseline runner and exact build/run commands:
`python3 tools/g1d_floor_inputs.py --selftest`
`cmake --build build --target RogueSquadron64Recomp -j 5 > scratch/agent/s6621_build.log 2>&1`
Copy/adapt tools/g1d_floor_inputs.py's run_arm to a fresh s6621 output root;
run both widths in this iteration, sequentially (one game at a time),
phase-gated, SIGKILL after >=50 closed frames plus the width-matched dump.
Check CGSSessionScreenIsLocked before each arm. Export any lib/ edit using
`./submodule-patches/export.sh`. Do not patch rendering or change defaults
until the writer and value legitimacy are established. Do not retune HUD.
