# NEXT (s7219): G5c RETINA=1 + ASPECT=auto replicate past 354 s, 600 s hold, on screen throughout
HYPOTHESIS-ID: g5c-retina-auto-endurance
Context: s7218 a1 (FULLSCREEN+auto+RETINA=1, LEVEL=4) was clean on screen 95-354 s (59.6/s, 0 gaps >250), a0 clean for 420 s; at 354 s
a Claude.app auto-update relaunch covered the fullscreen Space (P at=0 for the rest, one 1 s nextDrawable timeout). The 354-600 s
window at RETINA=1 has no on-screen datum.
Hypotheses: H-free (0 hidden rows, 0 gaps >250 ms outside loads, gpu p95 < 1 ms through 600 s); H-long (a stall class appears past
354 s at 8x internal: texture-cache/drawable growth); H-host-again (another front-app change; then the arms.log `front` row names it
and the run is void past it).
Run (quiet host, screen unlocked; check /usr/sbin/ioreg -n Root -d1 for CGSSessionScreenIsLocked first):
  env R=$PWD/scratch/s7219 HOLD=600 ARMS="4:a1:ROGUESQ_FORCE_SAVE_MISSION=4+ROGUESQ_ASPECT=auto+ROGUESQ_RETINA=1" zsh tools/g1e_owner_quiet_arms.zsh
  (mkdir scratch/s7219 first; HOLD 600 = ~11 min, run in background and wait with a python poll on quiet.done)
Score: python3 tools/s7204_ring_cost.py scratch/s7219 a1 --from 95 and --from 354 (hidden column must be 0);
  grep front scratch/s7219/arms.log (positive control: the first `front` row at t=2 must name the game or the prior app; it always fires);
  grep -a -c -E 'CRASH|SIGBUS|\[stall-dump\]' log_a1.txt.
Outcomes: H-free -> report RETINA endurance complete to the owner (default decision stays theirs); H-long -> name the stall from the
Q row fields (acq/gpu/wl) and the [stall-dump]; H-host-again -> score up to the front change only.
