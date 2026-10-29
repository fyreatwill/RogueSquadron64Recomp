# NEXT: split GPU raster output from native conversion/writeback
HYPOTHESIS-ID: g1d-levelselect-texel

s6621 selects H-pipe, single-source: complete emitted mesh versus coefficient
replay agrees within 25% in both sample conventions, yet framebuffer edge
steps are 6.75/5.68 at 796 versus 56.45/53.40 at 1024. Do NOT repeat a
coefficient/vertex scalar. Evidence: scratch/agent/s6621_mesh/verdict.json.

ONE work unit: phase/frame/address-joined pixels at three stages of the same
floor frame, before changing rendering. Hypotheses:
- H-raster: GPU color target already contains torn rows. Investigate shader,
  actual interpolants/texture state/raster backend, not CPU coefficients.
- H-convert: GPU target is smooth but the native converted readback is torn.
  Name the native-conversion shader/address/width expression.
- H-copy: native pixels are smooth; post-copy RDRAM is torn or later changes.
  Name copy stride or subsequent writer; retain the before/after write keys.
- H-witness: captures do not join on framebuffer/frame, or the GPU/native
  positive control fails. Repair association before drawing any null verdict.

Ground truth first: read docs/F5-UCODE-REFERENCE.md; retain the independent
paraLLEl-RDP edge/plane reference linked in tools/g1d_floor_mesh.py. Inspect
existing readback/target capture helpers BEFORE implementing a new one.
Existing source anchors:
`rg -n 'copyNativeToRAM|ROGUESQ_WBLOG' lib/rt64/src/hle/rt64_state.cpp`
`rg -n 'copyToRAM|readback|copyToNative' lib/rt64/src/render/rt64_native_target.cpp`
`rg -n 'copyNativeToRAM' lib/rt64/src/hle/rt64_framebuffer.cpp`
`rg -n 'halfPixelOffset|screenScale' lib/rt64/src/render/rt64_framebuffer_renderer.cpp`
The prior pixel dumps are RDRAM/VI sources, not pre-conversion GPU witnesses.
Do not assume those two are identical. Preserve actual render resolution and
sample-center transform; halfPixelOffset adds half a target pixel.

Build all stage captures in ONE binary and collect both 16:9/21:9 arms this
iteration, sequentially, using tools/g1d_floor_inputs.py run_arm output_root
parameter. The exact baseline recipe is there (12 MB; phase-driven start/z;
LOG_FLOOR=1; wide hangar, height 336; >=50 closed frames plus matching dump).
`python3 tools/g1d_floor_mesh.py --selftest`
`cmake --build build --target RogueSquadron64Recomp -j 5 > scratch/agent/s6622_build.log 2>&1`
Use a fresh s6622 capture root. Check screen lock before each arm; SIGKILL.
Export any lib/ edits: `./submodule-patches/export.sh`.

Measurement: x=16 and x=w-17, y=180..250, row-step luma at all three stages;
record fb address, target id, width/height/pitch, render-scale, task/frame and
conversion/copy serial. Positive control: known checker target must visibly
survive the GPU-readback and conversion path with known row/column bounds;
a fabricated host array alone does not test GPU readback. Retain same-run
tear reproduction and baseline controls. Match source pixel centers exactly.

Outcome: tear first present at GPU -> H-raster; first present in native
conversion -> H-convert; first present after RAM copy -> H-copy. Missing
stage/failed control -> H-witness, fix now. No guard/skip/default change
without naming the writer and establishing value legitimacy. Keep any
CPU reconstruction-based conclusion explicitly single-source until replayed.
