# NEXT work unit — trace the first divergent output/state producer

HYPOTHESIS-ID: m5-output-state-contract-boundary

The controlled title join selected a real divergence at the first joined row:
`s0` differs at all four target PCs in both port arms versus the independent
retail oracle. Determine whether it is already wrong at the producer or is
changed by the wrapper/ABI boundary.

Competing hypotheses and discriminating outcomes:

- `H-ProducerInput`: producer-side `s0` differs before the target call;
  selects the missing producer/input contract.
- `H-WrapperClobber`: producer-side `s0` matches but target-entry `s0` differs;
  selects wrapper register capture or ABI clobber.
- `H-ProducerJoinAbsent`: controls fire but producer rows cannot be joined by
  title phase, producer PC, target PC, and ordinal; result is unevaluable.
- `H-ControlFailure`: the producer table's positive control is absent; repair
  the control before interpreting any null.

Build one instrument containing producer PC, target PC, per-target ordinal,
`s0`, `s1`, source word, branch selector, branch state, and output/state fields;
retain the existing four-PC positive-control marker. Run the controlled title
route once, then join to `scratch/agent/s3450_oracle_fixed.log` using phase,
producer PC, target PC, and ordinal. Do not alter waits, slots, dispatch,
clear behavior, or PCM writeback.
