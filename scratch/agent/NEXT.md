# NEXT work unit (M3 FULL_SYNC parser/control-flow audit)

HYPOTHESIS-ID: m3-full-sync-parser-control-flow

Session 783 compared the stock Mupen64Plus CLI with the oracle. The stock CLI
fresh config lacked `Input-SDL-Control1` and fell back to `InputAutoCfg.ini`,
but a fresh 130-second oracle run using the attached SDL input path and the
verified eleven Start schedule still stayed 320-only: 21,618,871 whole-RDRAM
writes, 7,793 VI, all presses verified. The oracle runtime/configuration
thread is closed for this concrete difference.

## Discriminating measurement

Enumerate the authoritative post-sec2 FULL_SYNC/E9 dispatch path and its
control-flow gates in one phase-gated port run, reusing the existing positive
task/E9 alignment and `State::fullSync` counters. The discriminating outcome
is: if aligned E9s advance the authoritative parser but do not reach
`GBI_RDP::fullSync`, the map/handler path is implicated; if they reach
`GBI_RDP::fullSync` but `State::fullSync` does not advance, the state/pacing
path is implicated; if aligned E9s do not advance the authoritative parser,
the parser's command-boundary/control-flow walk remains the active fault.
Require a same-run positive control that marks every instrumentation arm and
phase-gate the counters to the post-sec2 VI transition.

## Controls

- Read `docs/F5-UCODE-REFERENCE.md` before interpreting command boundaries.
- Write the competing hypotheses and this discriminating measurement into this
  file before building; do not run a counter-only null.
- Use one build/run for all parser, aligned-E9, authoritative-dispatch, and
  State::fullSync counters; scope budgets to the post-sec2 phase.
- Do not productize a mitigation without naming the writer and legitimacy.
