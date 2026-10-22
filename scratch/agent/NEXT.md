# NEXT: consume the repaired G1 level-10 coverage pair

HYPOTHESIS-ID: g1-mission-coverage

Work unit: let the queue run `g1_lvl10a.sh` and `g1_lvl10b.sh`, then classify
both only if they reach flight. The previous attempt produced
`g1_level_coverage_common rc=1, 0s` and `g1_lvl10a rc=127, 0s`; inspection
showed the common `.sh` runner was consumed by the queue glob. It is now
`scratch/agent/g1_level_coverage_common.zsh`; all active wrappers pass syntax
checks and level 10 `a/b` are restored.

Competing hypotheses for the next pair:

- H1: level 10 reaches flight and holds 300 seconds in both arms; this is
  valid level-10 route+hold coverage.
- H2: either arm launches but misses `[lvsel]` or flight; the forced-level
  harness is still invalid and must not count as coverage.
- H3: either arm crashes, hangs, or stalls VI for 30 seconds after flight; the
  log is a new G1 root-cause datum.
- H4: either arm still fails at 0 seconds; the path repair is incomplete and
  its stderr identifies the remaining launch contract defect.

Discriminator: per run, require `[lvsel] a1 == 1<<10`, flight handoff, HOLD
completion, zero `CRASH`/abort lines, and no unchanged VI origin for 30 seconds.
The positive control is the `[lvsel]` line itself; missing controls make the
run unevaluable rather than a pass.

Suggested checks after the queue verdicts arrive:

```sh
tail -5 scratch/agent/SOAK-RESULTS.md
rg -n '\[lvsel\]|flight|CRASH|VI|stall' scratch/agent/soak_results/g1_lvl10[ab]_*.log
```

The following unit is level 11 `a/b` after level 10 is valid.
