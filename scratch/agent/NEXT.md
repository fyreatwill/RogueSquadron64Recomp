# NEXT: score pose-matched early-flight frames for G3c(a) edge arms
HYPOTHESIS-ID: g3c-edge-arm-route-gate

s6400: ROGUESQ_POSE_LOCK=1 gives matched pose in the first ~600 polls of flight in all arms (retail, dd2, aspect16:9, combined), dirs scratch/agent/m6/g1_lvl1s6400_*/fbd, log lines [poselock] n=.. pos=...
Work unit: map FB dump files to poselock n (dump order/VI vs wall time in run.log; or pick the first K dumps after the first [poselock] line), view contact sheet of the first ~10 post-spawn frames per arm (sips -> PNG in scratch/agent/view/s6400/), score with tools/g3c_horizon_score.py on those only.
Outcomes: dd2 tracks combined, aspect tracks retail -> grid footprint; dd2 tracks retail, combined tracks aspect -> aspect side edge. If early frames still show no edge in any arm, lengthen the matched window by lowering sim drift (e.g. hold throttle/brakes) before concluding. Do not change runtime defaults.
