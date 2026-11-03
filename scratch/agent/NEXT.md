# NEXT: name the residual 3-5 VI port AI feed gaps on the title screen
HYPOTHESIS-ID: g3-title-ai-gap

State (s6807): the 19-VI transition gaps are fixed (set_frequency same-rate no-op). Port fix arm still shows gaps of
5 VI @VI737 (the 640->1024 title switch, a burst of ~30 osViSetMode calls #85-#113, one per VI), 4 @974, 3 @1958,
3 @2508 (scratch/s6807/fix.rand.txt). Retail from boot (scratch/s6807/retail/oracle.log): max 2 VI everywhere.
~60-80 ms each: small, but possibly audible as a click on the title.
Hypotheses: H-vimode (per-VI osViSetMode in the port does host work - RT64 mode/present reconfig - that delays the
guest audio thread); H-sched (the game thread holds the guest run token through a long non-yielding section - title
asset decompress - which retail preempts with the higher-priority audio thread on the VI interrupt); H-host (host
jitter: page faults / shader compile on the first title frame).
Discriminator, ONE build: per-gap wall-clock stamps (cheap ring buffer, dumped at exit) of: last osAiSetNextBuffer
before the gap, every osViSetMode in it with host ms spent inside, RT64 pipeline creations, and which guest thread
held the run token (ultramodern current thread id) at each VI in the gap. Run tools/g3_ai_gap_pair.sh-style port arm
twice (same build) to check the gaps recur at the same VIs (if not, H-host). If osViSetMode host ms sums to the gap ->
H-vimode; if the game thread holds the token -> H-sched.
Command: env SAVE_FROM=scratch/s6807/lvl3.eep SECS=40 CAP0=9999 AP=6:start,11:start,16:start,21:start XE="ROGUESQ_DEBUG_WRITE=80003470:1:320:0 ROGUESQ_RAND_TRACE=$PWD/scratch/s6808/a.rand.txt" zsh tools/g3_port_capture.sh scratch/s6808/a
If this is not cheap to instrument within one iteration, take the next ladder rung (G3 in-flight frame diffs).
