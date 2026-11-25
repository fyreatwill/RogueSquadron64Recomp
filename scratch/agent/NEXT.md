# NEXT (s7947)
HYPOTHESIS-ID: owner-handoff-regression
s7946: F6 panel qualified at 4:3 / 16:9 fs / 21:9 windowed (tools/s7946_panel_witness_all.zsh). Pad thread done for the agent.
0. `python3 tools/crash_reports.py --since 2026-11-25`; fold new SOAK-RESULTS lines.
1. Unit: whole owner-handoff regression after the s7941-s7946 pad/panel additions (last full pass ~s7762-s7765):
     python3 tools/s7762_owner_doc_check.py --controls
     python3 tools/s7763_owner_cmd_check.py --control      (expect 11/11 MATCH)
     zsh tools/s7764_inflight_toggles.zsh                    (expect 7/7)
     python3 tools/s7765_controls_dump_check.py              (expect 12/12)
   Hypotheses: H-ok (all match), H-drift (a queue/opt-in command or controls dump changed with the pad work -> fix doc or code),
   H-gate-stale (a checker's expectation predates s7941 pad rows -> update checker with a planted control).
   Each FAIL: name which commit changed the behaviour, fix, re-run that gate.
   If all pass: take the next agent-testable CURRENT-TRUTH Next-steps item; everything else waits on the owner.
