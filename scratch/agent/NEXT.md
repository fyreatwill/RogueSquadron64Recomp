Single next work unit (s5592): fold s5590_plume_attach_e and _f (queued; loop runs them; do NOT run the game yourself).
Commands: grep -n s5590 scratch/agent/SOAK-RESULTS.md ; cat scratch/agent/soak_results/s5590_attach_e/summary (and f)
Control: summary must say control=PASS, else tooling null.
Outcomes:
  - STOP/BREADCRUMB lines -> read run$r.lldb bt, name writer of si_addr=0x58 deref, fix root cause.
  - titles~10/10 clean, no stops (x2) -> ~20 clean attached boots; pivot to M6 mission-hold soaks (>=10 min, >=3 runs).
  - control=FAIL -> attach is also blocked; BLOCKED.md asking for human to run lldb interactively.
HYPOTHESIS-ID: plume-title-extended-hold
