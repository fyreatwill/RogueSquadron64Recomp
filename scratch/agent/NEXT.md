# Next work unit (s4397): obtain the second evidence line for the selector/decode boundary

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4396 qualified the caller/decode range census but remains single-source
retail evidence. The next unit is one independent port evidence line for the
same boundary, testing whether the no-writer/value-divergence result reproduces.

Competing hypotheses:

- H-port-corrob: the port's phase/task/payload join independently reproduces
  the retail no-writer/value-divergence result.
- H-port-diverge: the port's task/payload fields diverge from the retail
  publication relationship.
- H-instrument-gap: the port arm cannot produce the required phase/task join;
  this is invalid, not evidence for either semantic arm.

Discriminating measurement: one same-run port capture joining candidate-range
callsite rows, task publication ordinals, exact task-data destinations, and
source/post payload values in all three phase buckets. Reproduction selects
H-port-corrob; a qualified different relationship selects H-port-diverge; a
missing control selects H-instrument-gap. Require task rows >=1,000, exact
payload joins, and zero join-table overflow.

Exact commands:

    bash tools/oracle/build.sh
    bash scratch/agent/run_s4397_m5_selector_boundary_port.sh

The script must run one bounded port capture from the repo root and write its
log below `scratch/agent/s4397_m5_selector_boundary_port/`.
