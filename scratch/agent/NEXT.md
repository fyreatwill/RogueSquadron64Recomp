# NEXT (s7762)
HYPOTHESIS-ID: owner-report-triage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report, then new SOAK-RESULTS lines.
RDP-output coverage is COMPLETE (s7761: SELECT LEVEL + LEVEL DESCRIPTION H-state invisible; s7753 21/21, s7756 6/6). Do NOT add
more coverage units, crash-hunt soaks (G4 parked) or repeat holds.
Unit: if an owner report / new crash report / soak RED exists, take it (arm table, discriminator, root-cause fix). Otherwise take
the first ITERATION 3c rung that is not closed or awaiting the owner. Every ladder item is currently "owner look" (CURRENT-TRUTH
Next steps 2-9, 20), so the candidate engineering unit is a one-page owner review packet: docs/OWNER-REVIEW-QUEUE.md listing each
owner-judgement item with its one-line command (from docs/OWNER-OPT-INS.md) and its sheet path, verified to exist
(`ls` every path), so the owner can clear the queue in one sitting. Hypotheses for that unit: H-current (all paths/commands valid)
/ H-stale (some sheet paths or env names were renamed: fix the doc and say which). Discriminator: a script that checks every path
and every ROGUESQ_* name in it against `tools/s7734_compiled_reader_census.py` output (compiled readers).
Max 2 CPU-heavy jobs. Waiters: poll the pid, never `pgrep -f <name>` from a shell whose own command line contains <name>.
