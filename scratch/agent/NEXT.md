# NEXT (s7768)
HYPOTHESIS-ID: owner-report-triage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner answer to docs/OWNER-REVIEW-QUEUE.md
rows, then new SOAK-RESULTS lines after the s7750 fold. Any of those outranks everything (arm table, discriminator, root fix;
an owner "close" -> close that row in the queue + CURRENT-TRUTH).
Do NOT add coverage units, crash-hunt soaks (G4 parked), repeat holds, or more latency arms: s7767 closed the latency thread
(queue->photon 23 ms in every window mode; game side 1 frame).
If nothing arrived: take the next open ladder rung that is agent-measurable and not waiting on the owner's look (see CURRENT-TRUTH
Next steps; G5/G6 rows that wait on the owner don't count). Write its 2-4 hypotheses + discriminator here before building.
Note for g1e_owner_quiet_arms.zsh users: `mkdir -p $R` first (the tool does not create it).
