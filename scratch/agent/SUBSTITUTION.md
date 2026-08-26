# s2474 SUBSTITUTION

## 1. What stopped the planned work unit

There was no planned s2474 work unit. The previous session (s2473) completed
its experiment and committed its ledger entry, but did not rewrite NEXT.md for
the next iteration. NEXT.md was labeled "(s2473)" and described s2473's work.
The exit-contract check flagged "NEXT.md predates this iteration."

## 2. Evidence (this iteration) that it was actually stopped

NEXT.md header on entry: "# NEXT work unit (s2473)". The PORTING-STATE.md
grep at session start showed `## Session 2473 (2026-08-26)` as the last entry,
matching the committed work. There was no s2474 entry and no s2474 work unit
to run.

## 3. Single experiment to refute

There is no blocking condition to refute — the work unit was simply absent
from NEXT.md, not blocked by environment. The session used the time to trace
the root cause statically and write the s2475 discriminating work unit.
