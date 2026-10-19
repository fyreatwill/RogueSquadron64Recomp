Single next work unit (s5590): fold s5589_plume_lldb_a and _b (3 title boots each under lldb, 15 s hold). Loop runs them; do NOT run the game yourself.
Commands:
  grep -n s5589 scratch/agent/SOAK-RESULTS.md
  cat scratch/agent/soak_results/s5589_plume_lldb_*/summary
Control: each boot needs a TITLE line; otherwise null (lldb launch failure shows as no TITLE).
Outcomes:
  - 'stop reason' / CRASHMARK in a run*.game -> read the lldb bt, name the writer of the si_addr=0x58 deref, fix root cause.
  - All 6 TITLE, no crash (10/10 total clean) -> queue more batches via tools/agent/gen_plume_lldb_soak.py (c d e ...); after ~20 clean boots pivot to M6 mission-hold soaks.
  - No TITLE (lldb broke boot) -> check run1.game head, drop `-o "register read"`/adjust.
HYPOTHESIS-ID: plume-title-extended-hold
