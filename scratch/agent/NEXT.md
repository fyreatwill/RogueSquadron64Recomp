# NEXT (s7659)
HYPOTHESIS-ID: gate-sweep-standing

G6a/G6b/G6c and the G5 looks wait only on the owner (docs/OWNER-OPT-INS.md). If the owner reports, take that first.

s7658: sweep 135 = 130 GREEN, 5 REPORT, 0 NEEDS-INPUT, 0 RED. The gate-sweep thread is finished as a standing check.
Work unit: pivot off gate tooling to the next owner-facing ladder item that is not waiting on the owner. Read the CURRENT-TRUTH
Next-steps list for an item with an engineering step left (not an owner look); if none, take the s7631 cold-AST timing when
an rt64 edit happens anyway, else the G5 renaming sweep (item 4) with the revisit rule.
Hypotheses for the s7631 timing: H-fits (regen ~165 s < 300 s cap with 6 jobs) vs H-over (raise its cap or run it serially).
Rules: never touch build/saves; one game at a time; SIGKILL only.
