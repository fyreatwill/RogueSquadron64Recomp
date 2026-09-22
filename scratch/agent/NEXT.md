# Next work unit: M5 family-value/setup provenance census

HYPOTHESIS-ID: m5-port-family-value-provenance

Run one batched, phase-gated capture that adds argument/value provenance at
each port entry and call edge for `0x80007670` and `0x8001E2C0`. Retain the
oracle whole-RDRAM control, both source watches, both VI snapshots, exact
source-span stores, and real/silent controls. Do not change port behavior or
suppress the legitimate `0x800078EC` zero fill. Use the existing
`scratch/agent/run_s3737_m5_retail_writer_join.sh` recipe and add the new
argument log in the same build/run.

Competing hypotheses:

- `H-FamilyValueSetupAbsent`: family entries receive zero/uninitialized source
  values before the qualified route, and no later setup edge populates them.
- `H-FamilyCallEdgeDropsValue`: a caller has a nonzero source/value, but the
  family call or argument mapping loses it before the target span is written.
- `H-FamilyValueClearedBeforeRoute`: a nonzero value reaches family setup, then
  a legitimate or invalid clear makes the qualified source payload zero.

Discriminator: compare caller argument/value rows with family-entry arguments
and target-span stores in title and hangar phases. Zero at both caller and
entry selects `H-FamilyValueSetupAbsent`; nonzero caller becoming zero at entry
selects `H-FamilyCallEdgeDropsValue`; nonzero target stores followed by the
legitimate clear selects `H-FamilyValueClearedBeforeRoute`. Missing oracle
control or either target phase is unevaluable.

Ground truth already passed this iteration: the oracle positive control and
both target phases fired, and independently showed the retail earlier-family
writer PCs. Before any new instrument build, verify those same oracle options
remain enabled. A positive-control miss, absent phase, or absent real-audio
source route makes the result unevaluable.
