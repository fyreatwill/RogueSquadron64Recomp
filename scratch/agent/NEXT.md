# Resume next work unit

HYPOTHESIS-ID: m5-a10-replay-validation

Single bounded work unit: validate the regeneration-safe A9/A10 fixup replay on
a pristine generated-function copy. Run the existing scratch regeneration
recipe and compare its replay failure count, A9/A10 patch reports, and selected
generated files against the live tree.

Competing hypotheses:

* H-replay-valid: the pristine copy replays with `failures=0`, A9/A10 reports
  are present, and the selected generated functions match the live tree.
* H-replay-drift: replay completes but one or more A9/A10 reports or generated
  function comparisons differ, showing regeneration drift.
* H-replay-blocked: the pristine-copy prerequisite or replay command fails
  before producing a meaningful comparison.

Discriminating measurement: the single replay summary line
`[s4648-replay] failures=...`, the A9/A10 replay lines, and the four selected
`cmp` results from `scratch/agent/s4814_regen.sh`. `failures=0` plus matching
reports/files selects H-replay-valid; any mismatch selects H-replay-drift;
missing pristine input or no replay summary selects H-replay-blocked.

Exact command:

```sh
zsh scratch/agent/s4814_regen.sh
```

Do not rerun the s4828 startup capture or the route-invalid Step 11 A/B.
