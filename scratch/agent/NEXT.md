# NEXT (s7285): decompose the scene-change (fb-relocation) stalls, offline first
HYPOTHESIS-ID: g5c-fbswitch-transition-stall
State: s7284 closed G5c load-edge gaps (0 lit quiet freezes in 17 toggle runs; every off-window gap >=250 ms is an fb-relocation
scene change). CURRENT-TRUTH item 16 closed transition stalls at the retail ~139 ms MusyX 3072-sample wait (s7065) with a reopen
criterion of a > ~350 ms hitch. s7284's FBSWITCH gaps reach 316-466 ms off-load (L4 restart sequence: 333/337/350/351/414 ms) -> reopen,
bounded and offline.
Unit (no game run first): from scratch/s7277/ring_*.txt (Q rows carry wl, wl_ms, tp_ms, acq_ms, gpu_ms, vi, fb, gen) list every
FBSWITCH gap (python3 tools/s7284_edge_gaps.py | grep FBSWITCH gives times) and, for the rows bracketing each gap, split the gap into:
present-side (tp_ms/acq_ms/gpu_ms of the first post-gap Q row) vs guest-side (no Q row at all = no VI present request; wl skipped).
Hypotheses:
  - H-musyx: guest-side, a fixed ~139 ms MusyX wait plus the game's own load work (dur scales with level/asset load) -> retail; note in
    OWNER-OPT-INS, close.
  - H-host-alloc: present-side: RT64 creates new fb/render targets for the relocated pair (first post-gap Q row tp_ms/acq_ms ~ gap) ->
    ours; fix candidate = pre-create targets / avoid blocking present on resource creation.
  - H-shader: post-gap rows show pipeline creation (check RT64 log for shader/pipeline counts at those times, if logged).
Positive control: the SIGSTOP control gaps must classify guest-side (process stopped: no Q rows) with ~1 s gap.
Second line before any conclusion: angrylion/retail oracle timing of the same L4 restart (or the s7065 MusyX attribution log).
