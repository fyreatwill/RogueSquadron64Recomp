# NEXT: name the 21:9 level-select floor primitive
HYPOTHESIS-ID: g1d-levelselect-tear

s6611 closed the step-column test. Do not retune `ROGUESQ_HUD_ANCHOR` or
`ROGUESQ_SHIFT_REGION`, and do not add a cull or a default change.

The tear is horizontal slices of the hangar floor in the outer thirds of
the phase-4 1024×336 buffer (n=1400/1500/1600). Outer-third dy over the
worst 70 rows is 24.3 / 19.1 / 18.3, against 7.7 on the 16:9 level-select
(sides quiet, center ring hot) and 3.8–5.1 on the quiet rows of the same
21:9 frames. Shift 384 or 512 makes the SAD worse (~50–62 vs ~17–22).
The center ring stays solid. Evidence: `scratch/agent/s6611_tear/summary.json`,
`zoom_left.png`, `zoom_left_16.png`, `zoom_ring.png`.

ONE work unit: name the textured primitive that paints x < width/3,
y in 170..260, of that phase-4 frame.

Offline first. `ROGUESQ_ASPECT_SCALE` and `ROGUESQ_VPW_SCALE` are consumed
only as the projection aspect, the footprint x scale, and the viewport
width (`tools/apply_s6031_far.py`, `tools/apply_s6144_fpx.py`, the s6112
viewport patch). Read those consumers. If one of them also scales a floor
texture stride or S/T, that consumer is the suspect: say which instruction,
and stop.

If they only widen the projection, the discriminator is one instrumented
build and two arms (ASPECT 21:9 and 16:9, same route as s6610). During
phase 4 only, log each textured primitive whose screen box hits
x < width/3 and y in 170..260: guest PC, texture width/stride, and the
UV derivative if the ucode stream has it. The primitive whose stride or
derivative jumps between width 796 and 1024 is the writer. Negative
control: 16:9 side dy stays near 7.7. Positive control: 21:9 side dy
stays above 18 on a frame in that phase. If both arms log the same
primitive with the same derivative, the wider frustum itself is the
cause and the next unit says so — do not patch yet.
