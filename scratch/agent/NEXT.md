# NEXT (s7792; s7791 closed the vendored-dead-block-prune campaign)
HYPOTHESIS-ID: ct-maintenance-s7792
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, owner answers in docs/OWNER-REVIEW-QUEUE.md,
new SOAK-RESULTS lines (any of these outranks the rest).

Unit: CURRENT-TRUTH is 60,328 B (> 60,000), so Step 0 makes this a MAINTENANCE iteration. Compact it toward ~35 KB:
- Migrate the long CLOSED census items (backlog 18, 29-36: s7575 UB gates, s7766-s7790 audits) and the s7702-s7767 headline
  paragraphs verbatim into PROJECT-OVERVIEW under "(s7792 maintenance)". Leave a one-line pointer plus each item's gate
  command, because the gates stay in the sweep.
- Renumber Next steps into ONE monotonic sequence again (it is now 1-5, 18, 20, 23, 28-36 out of order).
- Refresh the Headline: every ladder rung is closed or waiting on the owner's look; list the owner items.
Proof: `wc -c` net shrink >= 15000 B; `python3 tools/s7762_owner_doc_check.py --controls` rc 0 (owner-doc paths still resolve).
No experiments this iteration.

After maintenance (s7793+): every rung is closed or waiting on the owner. Take ITERATION 3b secondary (title-boot plume SIGSEGV
si_addr=0x58: check whether the s7725 plume fix stopped it. Loop title boots under lldb, about 20 boots, and record the
recurrence count), then G3 render-fidelity frame diffs against the angrylion oracle on a level not yet sheeted.
Hypotheses (plume): H-fixed (0/20 recurs: the s7725 fix covers it), H-other (a recurrence: the lldb backtrace names the writer).
