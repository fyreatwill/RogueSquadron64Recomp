# NEXT: s5877 soak was a null (fuse never armed, no [bit1], y flat -6.5, no input). Re-run same fusewatch build WITH keyed descend input so [bit1] fires (control), then read writers per below.
# NEXT: G1 - s5877 read [fzw] from soak s5877_fusewatch (queued; log scratch/agent/m6/s5877_fusewatch/run.log + soak_results)
grep -a '\[fzw\]\|\[bit1\]\|\[plpos\]' run.log: find the first non-decrement (pc != 0x800B1080/10D8) writer of a=80137F40 (timer) / 80137F3C (flags) before each [bit1]; read its ra/fn and y vs plpos.
Hypotheses: (a) legit ground impact (y descends smoothly) (c) wrong terrain/y. Control: dec writer lines present (dec= counter) in the same run. Then disassemble the writer's fn and name the condition.
HYPOTHESIS-ID: g1-mission-progression
