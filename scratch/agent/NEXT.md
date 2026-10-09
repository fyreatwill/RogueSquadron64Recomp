# Next work unit (s4403): qualify the title AI-boundary callsite

HYPOTHESIS-ID: m5-selector-decode-boundary

The qualified port route is `0x00790400 -> 0x006AB400`; the absent
`0x00790800` bucket is not part of this unit. Session 4402 showed title
selector setup/source/mixer/input/store-entry/tick activity, while the
AI-boundary/callsite witness was filtered to hangar by host code.

Competing hypotheses:

- H-title-callsite-present: the existing AI-boundary/callsite hook executes in
  title but its width/origin filter hid it; widening that filter yields title
  callsite rows with the same phase/task controls.
- H-title-callsite-absent: title setup activity does not reach the hooked AI
  callsite; widening the filter yields no title callsite rows despite controls.
- H-title-callsite-route-mismatch: the title phase label is not paired with the
  selector callsite's task/image route; title callsite rows, if any, lack the
  qualified phase/task join.

Discriminating measurement: change only the existing host filter in
`rs64_m5_selector_ai_boundary`/`rs64_m5_selector_ai_callsite` to admit title
`width=1024, origin=0x00790400` while retaining the hangar arm. Build once,
then run `run_s4402_m5_title_selector_witness.sh` with its positive input
control and all selector gates. Title callsite rows paired with live title
task/image joins select H-title-callsite-present; zero title callsite rows
select H-title-callsite-absent; rows without paired title controls select
H-title-callsite-route-mismatch. The hangar arm is a same-run positive
control for the widened diagnostic.

Exact commands:

1. Edit the two host filters in `src/main/upstream_compat.cpp` with
   `apply_patch`; preserve the original hangar condition and add the title
   condition.
2. `cmake --build build --config Debug --target RogueSquadron64Recomp`
3. `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh`

Capture to `scratch/agent/s4402_m5_title_selector_witness/`; SIGKILL the game
and report positive control, title/hangar phase counts, task/image joins, and
title/hangar AI-callsite rows.
