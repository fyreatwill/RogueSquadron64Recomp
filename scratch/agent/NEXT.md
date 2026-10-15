# Next work unit: choose a new M3 idiom-class audit (all prior M5/s4540 threads closed by s5012)

HYPOTHESIS-ID: m3-new-idiom-class-audit

s5012 closed the mission-sample thread (32/32 current-base, 0 stale, crash=0; plus s4993). Nothing else is queued.
Step 1: `grep -n 'Parked and closed' -A15 docs/CURRENT-TRUTH.md` to list already-audited classes; grep-enumerate generated code for one NOT listed (e.g. a stack/array-index idiom family akin to -0x25A4), classify every site, guard or prove dead.
If no unaudited class can be named after ~15 min of grep, go BLOCKED with that specific question (not a repeat of the owner-decision block refuted in s5010).
