# NEXT: G3d turning-shake timing follow-up (ITERATION item 3c)
HYPOTHESIS-ID: g3d-turning-shake-timing

G1d level select is closed (s6694 scissor wrap, s6695 spike-cull bound + radar-shift gate). Spec: ITERATION.md G3d.
Evidence that reopens G3c(c): s6458 VI stamps arrive in bursts (3-4 VIs within 0.1 ms, then ~66 ms gaps) and lvl1
ran ~18 gfx tasks/s vs ~30/s retail (s6452, 0x8011A890).

Hypotheses:
- H-log: the soak's G1B/G3C logging slows the game thread and bunches VI delivery; normal play is fine.
- H-thread: VI events go to a game thread busy for ~66 ms, i.e. real ~15-18 fps in normal play too.
- H-present: game frames are even but RT64 presents bunch.
Discriminator (ONE build): cheap ring buffer (no per-frame stderr) stamping wall time of (a) VI event delivery,
(b) game gfx-task submit (osSpTaskStart of the gfx task), (c) RT64 present; dumped at exit. Arms, same build,
sequential runs: lvl1 forced route steady turn (autopilot yaw hold), minimal logging vs usual soak logging, retail
and FPS60. Report per arm: game fps, submit-interval and present-interval distribution (p50/p95, burst count).
Outcomes: minimal-logging arm even ~30 fps -> H-log (fix: cheaper logging); both ~18 fps bursty -> H-thread
(find what blocks the game thread: QoS/priority, VI delivery path); submits even but presents bunched -> H-present.
Owner judges feel after any fix.
Side item (small, optional): grey radar wedge stays at x~690 top in 21:9 flight (screenshots/s6695_21x9_flight_radar_gate_check.png);
the s6159 shift leaves it behind. Owner: send screenshots/s6694_* and s6695_21x9_levelselect_before_after.png.
