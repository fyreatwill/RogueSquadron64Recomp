# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e lever (1) — real game frame rate per level at the owner recipe (s6989 closed the QoS bundle)
HYPOTHESIS-ID: g1e-game-fps
State: QoS work closed s6989 (ROGUESQ_QOS_ALL=1 opt-in, owner decides default). G1e asks for the real game frame rate
(distinct framebuffers per second) per level, with FPS60 on and off, at the owner recipe (16:9 dd4 VI_LOCK QOS_ALL).
Hypotheses:
- H-60: FPS60 already gives ~60 distinct game frames/s on every level -> G1e frame-rate goal met; report per level table.
- H-dense-drop: dense levels (lvl5 / lvl10 / cutscenes) fall to 30-45 distinct/s -> name the binding cost (guest CPU, send_dl, RT64).
- H-dup: presents are 60/s but some are repeats of the same game frame (VI vs game frame mismatch) -> pacing bug.
Unit: one build (none needed if the present ring already stamps the game-frame id; check ROGUESQ_PRESENT_RING fields first),
levels 1, 5, 10 x FPS60 on/off, 120 s each through tools/g1e_owner_quiet_arms.zsh with ROGUESQ_FORCE_SAVE_MISSION=<lvl>;
count distinct game frame ids per real second from ring_*.txt. Positive control: FPS60 off must read ~30/s.
