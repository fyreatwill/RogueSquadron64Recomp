# NEXT (s7765)
HYPOTHESIS-ID: owner-report-triage
First: `python3 tools/crash_reports.py --since 2026-11-13 | grep -v '^FOLDED'`, then any owner answer to docs/OWNER-REVIEW-QUEUE.md
rows, then new SOAK-RESULTS lines after the s7750 fold. Any of those outranks the unit below (arm table, discriminator, root fix;
an owner "close" -> close that row in the queue + CURRENT-TRUTH).
s7763 (startup commands 11/11) + s7764 (in-flight toggles 7/7, tools/s7764_inflight_toggles.zsh) verified every queue switch except
row 2 (F6 panel / ROGUESQ_CONTROLS_DUMP=1). Do NOT add coverage units, crash-hunt soaks (G4 parked) or repeat holds.
Unit if nothing arrived: row 2 CONTROLS_DUMP=1 — H-works (prints the live map, and with a temp controls.json in a COPY of the data
folder the dump shows the override) vs H-broken (dump absent or ignores the file). Positive control: default dump equals the
built-in table (s7620 table-vs-old comparison tool if it exists; grep tools/ for s762*). Never touch build/saves or the owner's
controls.json. One launch per arm, 12 s, SIGKILL.
