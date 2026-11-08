# OWNER OVERRIDE 2026-11-04: do ITERATION.md G5 in order. G5a-G5h all fixed or done, owner confirmation pending.

# NEXT: G1e — what makes the residual late frames slow once ROGUESQ_WL_QOS=1 is on (s6987).
HYPOTHESIS-ID: g1e-wl-residual
State (s6987): lates = RT64 workload thread threadRenderFrame long (8 vs 3 ms) + wake 1.5 ms at QoS 21; WL_QOS=1 cuts lates
58/53 -> 24/14 ABBA and removes the wake. Residual lates (W1/W1b, 38 total): render 5-6 ms vs 3, send_dl (ksd) 13-16 ms vs 9.5.
Hypotheses:
- H-preempt: workload / Gfx thread runnable but not running (burst still steals P-cores even at QoS 33).
- H-work: thread running the whole time -> real extra work (dense frame, pipeline creation, big upload).
- H-shared: both threads slow in the same frames -> they contend with each other or with the burst for one cluster.
Measure OFFLINE first, no build: scratch/s6987q/thr_W1*.bin (ROGUESQ_G1E_THREADS sampler, 1 ms) with tools/g1e_thread_census.py
(feed it windows from tools/g1e_late_leg.py --windows style, or add a --windows option to tools/g1e_vi_phase.py writing the
corrected-chain R->W and kick->R windows). Per late: run vs runnable ms of the workload and Gfx threads, CPU id cluster.
Positive control: on W0/W0b lates (QoS 21) the workload thread must show runnable-not-running time (the wake gap WL_QOS removed).
If H-work: correlate rend with tri count / pipeline creation in the same frames. Owner decides WL_QOS default (OWNER-OPT-INS row).
