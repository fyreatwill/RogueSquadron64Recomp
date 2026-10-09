# Next work unit (s4415): corroborate the title-side selector entry on the port

HYPOTHESIS-ID: m5-selector-decode-boundary

Session 4414's qualified retail range run passed the whole-RDRAM and VI
controls and retained 629/628/538 type-2 task rows in the two title buckets
and hangar. The selector family executed in all three phases. Title entered at
`0x80029E80` from `0x8008EE84`; exact `0x80029E78` and its `0x80091CB8`
predecessor remained hangar-only. This is single-source evidence for a
title-side alternate entry.

Competing hypotheses:

- H-port-matches-retail-alternate: the port title selector path reaches
  `0x80029E80` or the same caller family, corroborating the retail alternate.
- H-port-retains-exact-entry: the port reaches exact `0x80029E78` in title,
  showing a port/retail selector-path divergence.
- H-port-route-boundary: phase, selector, or task controls fail, so the
  cross-source comparison is unevaluable.

Discriminating measurement: one existing qualified port run with phase-gated
selector route/caller/precall logs, title and hangar VI markers, task/image
joins, and the input positive control. Title `0x80029E80`-family activity
with live controls selects corroboration; title exact `0x80029E78` activity
selects divergence; missing phase/task/input controls selects the boundary arm.

Exact commands:

1. Run `zsh scratch/agent/run_s4402_m5_title_selector_witness.sh` after
   confirming the existing build and qualified route; retain its all-selector
   logs under a new `s4415` directory, not the old result.
2. Count phase-keyed selector/caller rows and verify the input, task, title,
   and hangar controls before interpreting a null.

Do not repeat the retail range capture or caller enumeration.
