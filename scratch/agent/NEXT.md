# NEXT: name the writer of the striped depth the 21:9 floor loses to
HYPOTHESIS-ID: g1d-levelselect-texel

s6624 selects H-late-test, SINGLE-SOURCE. The floor shader color is sane on
both widths. 16:9 enters x=16 and x=w-17, y=180..250 at depth exactly 1.0, so
LESS (shader z 0.99524..0.99667) replaces the color and the step falls to
~5. 21:9 serial 1 (frame 1351, addr 0x961000) already has the stripe at
sample 0, before any op in that submission: 25 samples at depth 0 on rows
0..12 (y 180..192), then 1.0 interleaved with ~0.961/0.967/0.984, and the
two columns are largely out of phase. Op 14 passes only on the 1.0 rows
(36/92) and that partial replace creates the tear (step 19.3/18.8 ->
42.2/45.6). Later scenes keep losing LESS (serial 7: 10 pass / 112 fail,
rejected_frac 0.873, later_frac 0). Floor blend is off, ONE/ZERO, and matches
Metal. The 9 wide16 blend mismatches are ops 1-9, not the floor. Do not
repeat the in-submission witness, the s6623 shader census, or a CPU replay.
Do not change a default or add a cull/skip/restore.

Depth create and clearDepth default to 1.0. A missing clear can leave 1.0.
It cannot by itself explain 0.0 or the ~0.96 cluster. Those values predate
this submission's draw loop. The color-clear branch in the framebuffer
renderer calls clearColor only when a color target is bound, and clearDepth
only in the else. That split is a lead, not a verdict.

ONE work unit, one binary, both widths. Log, per depth texture that the
phase>=4 floor submission uses, every event from setupDepth through sample 0
of the first captured floor submission:
- setup width, height, format, create-clear value, texture identity
- every clearDepth: value, rect or whole-target, scissor, color fb address
- every draw that writes those two columns: submission frame/pair, op kind,
  zCmp, depth compare, depth write, interpolated z, pre/post depth, pre/post
  color

Hypotheses and discriminating outcomes:
- H-prior-stripe: both widths show a clear or create of 1.0, then 21:9-only
  draws store 0.0 and the ~0.961/0.967/0.984 interleave. Name the first draw
  (kind, zCmp, compare, z range) whose post depth matches s6624 serial 1.
  16:9 must show no intervening store, because its sample 0 is still 1.0.
- H-depth-pitch: that draw's interpolated z is smooth across y and its
  scissor covers the band, but stored depth alternates by row and the two
  columns are out of phase. Depth texture width or row pitch disagrees with
  the color target. Name the pitch and the producing call.
- H-depth-readback: nothing stores 0.0, the create clear is 1.0, and a
  same-run known store read back correctly (the 16:9 floor write of z~0.996
  must appear). Then 0.0 is an unwritten tile, not a writer. The ~0.96 values
  still need their own store; do not use this label for them. Do not "fix"
  readback in this unit.
- H-witness: the 16:9 floor depth write does not appear, or 21:9 sample 0
  does not reproduce the 25 zeros plus the 1.0/~0.96 interleave. Repair the
  log in this same iteration before interpreting a null.

Positive controls, required: s6624 magenta pixel still changes (16,180);
16:9 sample-0 depth stays 1.0 and the floor store of ~0.996 is in the new
log; 21:9 log ends at the serial-1 pattern above. A silent log is not a
result. Phase-gate the route. No cross-run animation compare. Screen must be
unlocked (the runner asserts CGSSessionScreenIsLocked). SIGKILL. One game
run at a time. Do not overwrite scratch/agent/s6624_attachment.

Anchors:
rg -n 'clearColor\(|clearDepth\(|floorCapture|commitOp' lib/rt64/src/render/rt64_framebuffer_renderer.cpp
rg -n 'setupDepth|clearDepthTarget' lib/rt64/src/render/rt64_render_target.cpp
rg -n 'clearDepthStencil' lib/rt64/src/contrib/plume/plume_metal.cpp

Build and run:
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer cmake --build build --target RogueSquadron64Recomp -j 5 > scratch/agent/s6625_build.log 2>&1
PYTHONPATH=tools python3 tools/g1d_floor_attachment.py --selftest
PYTHONPATH=tools python3 tools/g1d_floor_depth.py --output-root scratch/agent/s6625_depth
./submodule-patches/export.sh

Adapt tools/g1d_floor_attachment.py into that depth runner. Keep the existing
attachment selftest green. If lib/ changes, the export is part of the commit.
