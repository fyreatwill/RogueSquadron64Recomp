# NEXT work unit — identify the M5 image-to-output boundary

HYPOTHESIS-ID: m5-step1-image-silent-qualification

Run one ground-truth-first discriminator for the missing image-to-output
writer/consumer boundary exposed by Session 3325. Before building an
instrument, use the retail oracle to arm a positive control and watch the
candidate physical output/slot words plus their PCs during the title and
hangar phases. Then build one port probe covering the same boundary and rerun
the supervised pair only if the oracle control is live.

## Competing hypotheses

- `H-RetailWritesOutput`: retail writes the candidate output/slot field in the
  target phase; a missing port write is the contract gap.
- `H-RetailDoesNotWriteOutput`: retail does not write that field; the missing
  port edge is elsewhere in the image/task consumer chain.
- `H-PortMatchesRetail`: both sides show the same writer/order, so the current
  discriminator is measuring a downstream symptom.

## Discriminator

The oracle watch must pass the whole-RDRAM positive control and emit a
target-phase candidate write with a PC attribution. In the same qualified
port capture, compare writer PC/order and value transitions at the candidate
field. Retail-only writes select `H-RetailWritesOutput`; matching writes
select `H-PortMatchesRetail`; a positive control with no candidate retail
write selects `H-RetailDoesNotWriteOutput` and moves the watch upstream.
No null without the positive control is interpretable.

## Exact starting checks

```sh
sed -n '1,220p' tools/oracle/README.md
rg -n 'slot|output|PCM|B40|route|candidate' docs/M5-AUDIO-PLAN.md docs/CURRENT-TRUTH.md
```

Do not build or change behavior until the candidate physical address and
retail watch PC are named from those sources. Keep the existing M5 Step 1
pair recipe available for validation:

```sh
cmake --build build --config Debug --target RogueSquadron64Recomp
zsh scratch/agent/run_s2286_m5_step1_trace_light_pair.sh s3325_m5_step1_repeat
```
