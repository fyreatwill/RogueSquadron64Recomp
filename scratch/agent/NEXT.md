# NEXT: G3c(c) residual - does VI pacing jitter (sd ~2 ms, all arms) reach the screen?
HYPOTHESIS-ID: g3c-shake
s6455: camera yaw jerk is identical across retail/FPS60/ASPECT/both (VI-index alt 0.19-0.21). Left: H-vi-timer (our VI loop, events.cpp ~1473-1493, jitters; port defect for any setting) vs H-retail (30 Hz judder only; nothing to fix) vs H-logger-artifact ([g3c] stamp not the present time).
Work: read the VI timer loop (sleep_until(next) accumulating vs rebased after oversleep). Add a stamp at the RT64 present/swap call, queue one retail soak, compare present-dt sd/alternation with the VI-event dt. Present dt sd >1 ms and bimodal -> fix the timer (absolute deadlines, spin the last ~1 ms); present dt flat -> close G3c(c) as retail, tell owner, move to G1c phase 2.
