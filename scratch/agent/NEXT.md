# Next work unit (s4411): compare retail pre-filter selector/decode payloads

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4410's fixed phase latch selected a title-phase `0x80091CB8` call
consumed at the first hangar VI transition, followed by live hangar
boundary/input/source/store/task witnesses. The remaining open boundary is
before the selector call: retail and port need a phase-keyed comparison of
selector input, call arguments, and published task payload identity.

Competing hypotheses:

- H-retail-selector-multiplex: retail call arguments/input and task payload
  identity are phase-specific in the same qualified route.
- H-retail-shared-selector: retail call arguments/input and task payload
  identity recur across title and hangar despite different VI phases.
- H-retail-watch-boundary: controls and phase transitions are live, but one of
  the call/task watches is absent or unjoinable, so no payload conclusion is
  valid.

Discriminating measurement: one retail-oracle run with whole-RDRAM and VI
positive controls, phase-gated `--watch-pc` arms for `0x80091BAC`,
`0x80091CB8`, the selector input/decode boundary, and `0x80033FCC` task
publication; retain the task dump and compare `(input, call args, data_ptr,
first payload words)` by title/hangar bucket. H-retail-selector-multiplex is
selected by live phase-specific rows in both call and task arms;
H-retail-shared-selector by recurring values/payload family;
H-retail-watch-boundary by a missing arm with controls live.

Exact commands:

1. Build the oracle if needed and run one capture following `tools/oracle/README.md`
   with `--watch-write 0x0:0x800000`, VI trace, phase logs for
   `0x00790400,0x006AB400`, the two direct edges, selector boundary, and
   `--pc-task-dump 0x80033FCC`.
2. Inspect bounded evidence with `grep -n` and compare phase buckets; do not
   interpret a null unless whole-RDRAM, VI, and both route arms fired.

Do not repeat caller enumeration or the completed port phase-latch run.
