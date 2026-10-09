# Next work unit (s4336): compare the retail C904 and port C88C field tables

HYPOTHESIS-ID: m5-step9-retail-port-field-join

The s4335 retail field dump passed all controls. C904 executed 3,107 times and
produced 461 phase-gated rows at `0x006AB400` and 836 at `0x006AB800`, with
caller `0x8009C0E4`, object `0x80153420`, and nonzero source/branch fields.

Competing hypotheses:

- H-port-retail-parity: port C88C and retail C904 expose the same descriptor
  object-relative source and branch fields after phase normalization.
- H-pre-route-divergence: the mapped boundaries are equivalent, but their
  source/branch sequences differ before filtering, preserving the audio-route
  divergence.
- H-port-instrument-invalid: the port field witness cannot be joined or its
  route controls fail, so the comparison is unevaluable.

Discriminator: run one same-build port matrix with the existing C88C field
witness, phase-gated to VI origin `0x006AB400`/`0x006AB800` width 512, and
normalize the first bounded rows by object-relative offsets. Matching ordered
fields select H-port-retail-parity; valid controls with a stable mismatch
select H-pre-route-divergence; missing port controls or no joinable rows select
H-port-instrument-invalid. Do not change decoder, RSP, AI, or game-path code.

Suggested command shape:

`env ROGUESQ_LOG_VI_CALLERS=1 ROGUESQ_LOG_M4=1 zsh tools/run-field-join.sh ...`

The script must retain the independent oracle result at
`scratch/agent/oracle_s4335_c904_field.log` as the retail arm and capture the
port arm in a new non-dot path. Positive controls are port VI 512, the existing
field-call witness, and the oracle whole-RDRAM/title/hangar controls.
