# NEXT: score pose-matched early-flight frames for G3c(a) edge arms
HYPOTHESIS-ID: g3c-edge-arm-route-gate

s6400: ROGUESQ_POSE_LOCK=1 gives matched pose in the first ~600 polls of flight in all arms (retail, dd2, aspect16:9, combined), dirs scratch/agent/m6/g1_lvl1s6400_*/fbd, log lines [poselock] n=.. pos=...
Work unit: matched-window scores exist (PORTING-STATE s6399): contact-sheet the windows (retail dump n 1569-1659, dd2 1650-1740, aspect 1443-1533, combined 1542-1632) and score outer-15%-width columns only, aspect vs retail.
Outcomes: dd2 tracks combined, aspect tracks retail -> grid footprint; dd2 tracks retail, combined tracks aspect -> aspect side edge. If early frames still show no edge in any arm, lengthen the matched window by lowering sim drift (e.g. hold throttle/brakes) before concluding. Do not change runtime defaults.
