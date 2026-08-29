# NEXT work unit — close the next M3 NULL-plus-offset idiom class

HYPOTHESIS-ID: m3-next-null-offset-idiom

Session 3153 ran both Step 6 policy arms. Each reached VI 640 and emitted
eight shade-DMA controls, but neither emitted the drain-gate positive control.
Policy state and target-phase audio fields are unevaluable; no wait hatch is
authorized.

## Competing hypotheses and discriminator

- `H-M3-ValidProducer`: every site in the selected complete idiom has a
  reachable nonzero/in-range writer or a dominating validity test; no guard is
  justified.
- `H-M3-UnclassifiedProducer`: at least one reachable site lacks that proof;
  its writer or dispatch edge becomes the next investigation, with no
  mitigation added.
- `H-M3-DeadSite`: the apparent site is unreachable or a duplicate lowering
  artifact, so it is removed from the live class.

## Single work unit

Select the next complete NULL-plus-constant-offset class from the existing M3
inventory, enumerate every guest site and generated lowering, then classify
each site's writer, dominance, range, and reachability in one evidence file.
The complete table selects the hypothesis: all proven, one reachable site
unproved, or no live sites. Do not edit generated functions or add guards.

Exact starting commands:

```sh
rg -n 'MEM_[RWB].*\+0x|MEM_[RWB].*\+0X' RecompiledFuncs src
rg -n 'NULL-plus-offset|idiom' docs/CURRENT-TRUTH.md scratch/agent/*.md
```
