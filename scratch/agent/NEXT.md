# NEXT: FPS60 near-wall flicker: fold the s7099 repeats, pool the per-tick episode rate, read the eye trace at every episode
HYPOTHESIS-ID: fps60-wall-camera
Context (s7099): one same-run split (L6 dd4 16:9, FPS60=0, ROGUESQ_G1E_LIMIT=1 ROGUESQ_G1E_WIN=600, ROGUESQ_G3C_LOG=1) gave 2 episodes in
60 fps windows, 0 at 30 (P=0.47, not discriminating). In flight the eye reversal rate is equal (H-osc as a general spring refuted).
Locally the eye shows a push-out-like jitter/stop at the episode ticks (n=2, single-source).
Hypotheses left:
 H-ret   equal episodes per sim tick at both rates (the 60 fps mode only doubles the chances): report to the owner as retail behaviour
 H-push  a terrain push-out/clamp on the eye that converges in fewer steps at dt 1/30, so at 1/60 the eye sits inside the wall for a tick
         more often (per-tick rate at lim=1 > lim=2)
Unit:
 1. Read SOAK-RESULTS for s7099_wallsplit_r1..r3; logs in scratch/agent/soak_results/, game logs scratch/agent/m6/g1_lvl6s7099w6rN/run.log.
    If any did not run (queue not yet drained), run one repeat directly: `zsh scratch/agent/soak_queue/s7099_wallsplit_r1.sh`.
 2. Pool: episodes and ticks per lim over w6 + r1..r3 (w6 csv = scratch/s7099/w6.csv; raw is deleted by the soaks, so rerun
    tools/s7099_wall_split.py only where the raw exists, otherwise take the printed lines). Poisson test of per-tick rate.
 3. For every episode, dump the eye trace (-0.3..+0.1 s, the snippet in the s7099 entry: mach column of the drops csv vs g3c m=)
    and classify: jitter / dead-stop / smooth. A pattern only in lim=1 episodes = H-push; then find the writer of 0x80130C10 (eye)
    with a write watch at the episode tick and read the clamp code.
Outcomes: per-tick rates equal within noise with >=8 episodes = H-ret (owner note, close); lim=1 per-tick rate >=2x with p<0.05 = H-push.
