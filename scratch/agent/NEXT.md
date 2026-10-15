# Next work unit

HYPOTHESIS-ID: m5-aux-store-ab

s4946: solo vs duo image-arm VI pacing identical (mission entry #5738/#5744/#5735 at ~96.8s), so concurrency/CPU contention does not explain fewer image-arm origin flips in s4944. M5 plan steps 0-11 are all closed.
Next: count per-arm `[phase]` origin transitions (not `origin=` lines, which match ~370k lines) offline from scratch/agent/s4944_aux_ab/*.log to see whether the 49-vs-512 flip gap is real; if not resolvable, pick an M5 A-table row without a Qualified marker in docs/M5-AUDIO-PLAN.md, or follow the REVISIT rules.
