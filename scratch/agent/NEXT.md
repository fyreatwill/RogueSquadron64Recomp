# NEXT: G3c(c) read s6457 VI spin vs NOSPIN soaks
HYPOTHESIS-ID: g3c-shake
Soaks s6457_vi_spin / s6457_vi_nospin were queued (see SOAK-RESULTS.md tail). Logs in scratch/agent/soak_results/. Compute per-VI wall dt sd and sign-alternation about 16.67 ms for both (method of s6455). sd drops from ~2 ms to <0.5 ms with spin only -> timer oversleep was the cause, keep spin, tell owner. No change -> sd is upstream of the sleep (logger/scheduler); close G3c(c) as retail 30 Hz judder, move to G1c phase 2. If results are missing, wait (do offline work), do not re-queue.
