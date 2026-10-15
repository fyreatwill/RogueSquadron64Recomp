# UNBLOCK s4949

Route taken: 1 (refute) + 3 (re-scope). Not escalated.

Block claimed every tier is closed and asked for a human choice among (a) conditional-move recompiler support,
(b) an oracle mission-entry recipe, (c) stop.
Evidence the dependency is unnecessary:
- (a): docs/M3-S4840-MOVZ-MOVN-REACHABILITY.md classifies 149 movz/movn sites: 2 reachable, 16 post-return, 131
  data-like. Both "reachable" ones (funcs_49.c 0x800A2B64 movn $k0; 0x801096F4 movz $zero) follow `.word` junk /
  `sll $zero` in data-as-code. movz $zero is a no-op. do_break (lib/N64ModernRuntime/librecomp/src/recomp.cpp:454)
  prints "Encountered break at original vram" and exits, so any live hit would be loud; none recorded. N64Recomp
  src/include contain no movz/movn lowering (grep), so the gap is real but dormant. Not worth gating the loop on.
- (b): not needed for a work unit; mission entry is reached by the port route (s4946, 96.8s).
Work not needing a human exists: SOAK-RESULTS has no completed verdict since s4794 (s4921 rc=137), so a fresh
mission-route soak is the highest-information unit. NEXT.md rewritten accordingly.
Refutation experiment for this conclusion: a soak run printing "Encountered break at original vram 0x800A2B64".
