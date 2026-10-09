# Next work unit (s4408): join the hangar direct AI edge to selector state

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4407 showed that hangar does execute the already-known direct edge
`0x80091CB8`; the earlier zero was a readout/filter interpretation error.

Competing hypotheses:

- H-same-input-different-return: the hangar direct edge consumes the same
  selector input as title but returns a phase-specific frequency/state value.
- H-adjacent-path: the direct edge is live, but the hangar selector source and
  task payload are produced by a separate path and only happen nearby.
- H-callsite-row-alias: the phase row is stale or mis-keyed rather than a live
  hangar call; the existing setup/boundary controls would then disagree with a
  fresh callsite/return/store join.

Discriminating measurement: in one phase-gated run retain the hangar and title
rows for `ai-call`/`ai-return`, source store `0x80091CC8`, selector input
`0x8009192C`, and the existing task/image join, keyed by phase ordinal. A
same-input, directly joined return/store row selects H-same-input-different-
return; live direct rows with no selector/task join selects H-adjacent-path;
missing or phase-miskeyed callsite rows with live boundary rows selects
H-callsite-row-alias.

Exact commands:

1. Add the single phase-keyed join witness through the regeneration-safe probe
   script, then build:
   `cmake --build build --config Debug --target RogueSquadron64Recomp`
2. Run:
   `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh`
3. Compare only bounded rows:
   `grep -a -E '\[m5-selector-(setup-contract|ai-callsite|ai-boundary|source|input)\]|\[audtask-join\]' scratch/agent/s4402_m5_title_selector_witness/port.log | head -160`

Do not enumerate callers again or add another payload census. If the 85-second
route is invalid, record the route failure rather than interpreting absence.
