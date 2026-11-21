# NEXT (s7763)
HYPOTHESIS-ID: owner-report-triage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner report (answers to rows of
docs/OWNER-REVIEW-QUEUE.md), then new SOAK-RESULTS lines after the s7750 fold.
s7762 landed the owner review queue + tools/s7762_owner_doc_check.py (gate; GREEN). RDP-output coverage complete (s7761). Do NOT
add coverage units, crash-hunt soaks (G4 parked) or repeat holds.
Unit: if an owner answer / crash report / soak RED exists, take it (arm table, discriminator, root-cause fix; an owner "close"
answer -> close that row in the queue + CURRENT-TRUTH). Otherwise: verify every COMMAND in OWNER-REVIEW-QUEUE actually does what
the row says on a launch (H-works vs H-broken: e.g. `env ROGUESQ_DRAW_DISTANCE=2 ... --preset tv` really yields dd2 since env
beats preset; `--preset ultrawide` yields 21:9): one short boot per distinct command (max 2 at once, kill SIGKILL), grep the
startup echo lines for the effective settings; discriminator = echoed dd/aspect/fps60/standins per row vs the row's claim.
Positive control: a row with a deliberately wrong env (e.g. DRAW_DISTANCE=3) must echo 3. Fix any row that lies.
Max 2 CPU-heavy jobs. Waiters: poll the pid, never `pgrep -f <name>` from a shell whose own command line contains <name>.
