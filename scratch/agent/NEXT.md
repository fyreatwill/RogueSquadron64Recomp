# NEXT (s7218): G5c endurance datum at the owner's ultrawide combo: FULLSCREEN + ASPECT=auto + RETINA=1, long hold
HYPOTHESIS-ID: g5c-retina-auto-endurance
Context: G3 fidelity matrix CLOSED s7217 (LDESC 21:9/16:9 H-match; crawl/pause/fail at 21:9 were s7146/s7150/s7153). RETINA=1 cost was
measured only at FULLSCREEN 16:9 with HOLD 240 (s7204: 0 gaps >250 ms, fl_shown ~60). The owner's ultrawide path is FULLSCREEN + auto
(fb 712 on the built-in panel, s7188) and the owner's RETINA default decision (s7205) has no long-hold datum there.
Hypotheses: H-free (60 fps in flight, 0 gaps >250 ms outside loads, 0 crashes, GPU p95 < 2 ms, same as R0); H-long (a gap/stall class
appears only past 240 s: drawable or texture-cache growth at 8x internal, log/stderr burst); H-auto (auto + Retina interacts: resize loop,
[retina] swap chain recreated more than once, viewport not full).
Discriminator, one game at a time, quiet host (screen unlocked, idle > 60 s):
  env R=$PWD/scratch/s7218 HOLD=420 ARMS="4:a1:ROGUESQ_ASPECT=auto+ROGUESQ_RETINA=1 4:a0:ROGUESQ_ASPECT=auto" zsh tools/g1e_owner_quiet_arms.zsh
  (check the spec syntax at the top of the script first; LEVEL=4 owner route; FULLSCREEN is in the harness recipe).
  Score: python3 tools/s7204_ring_cost.py <ring> per arm (presents/s, gpu p50/p95/max, gaps >50/>250 split before/after t=240),
  grep -c '\[retina\] swapchain create' and [g1f-win] resize rows, CRASH/SIGBUS in run.log.
Outcomes: equal arms with 0 >250 ms gaps -> H-free, report to owner as RETINA default evidence; gaps only in a1 past 240 s -> H-long,
name the stall with the [stall-dump]/host sample; extra swap chain creates or a non-full viewport in a1 -> H-auto, fix in plume/RT64.
