# NEXT: pose-locked capture for G3c(a) edge arms
HYPOTHESIS-ID: g3c-edge-arm-route-gate

s6398: width filter (s6397) and VI-offset phase gating (s6398) both fail: autopilot attitude diverges per arm, so scene content differs. Metrics on unequal scenes are noise.
Work unit: add an env (e.g. ROGUESQ_POSE_LOCK=1) that, after the phase-5 witness + N VIs, pins the camera/craft attitude (hover, no autopilot input, or freeze camera matrix in guest RAM) so all four arms (retail, dd2, aspect, combined) render the same pose; dump one frame per arm; score with tools/g3c_horizon_score.py and eyeball a contact sheet (sips -> PNG in scratch/agent/view/).
Alternative cheaper: log camera yaw/pitch/roll per dump VI and pick pose-matched frame pairs offline.
Outcomes: dd2 tracks combined, aspect tracks retail -> grid; dd2 tracks retail, combined tracks aspect -> aspect side edge. Do not change runtime defaults.
