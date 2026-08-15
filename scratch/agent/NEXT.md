# NEXT work unit (s1238)

HYPOTHESIS-ID: retail-external-entry-boundary-closed

The prior external/front-end census is complete. Do not build or run. The next
work unit is to obtain and inspect one genuinely new retail-entry artifact: a
frontend/launcher source or binary invocation that can perform a state-changing
handoff not represented by the audited oracle/core contract. If no such artifact
is available, stop and ask the human for it rather than repeating source searches.

Competing hypotheses and discriminator:

- H1: the supplied artifact contains a state-changing handoff absent from the
  port; its command/data and timing identify the next probe.
- H2: the supplied artifact is equivalent to the audited contract and contains
  no such handoff; the retail transition remains externally unavailable.
- H3: no artifact can be supplied; the investigation is blocked on external
  ground truth, not on an untested in-tree path.

Discriminator: one artifact-backed event table listing source/invocation,
lifecycle point, state-changing side effect, and port equivalent. A concrete
unmatched handoff selects H1; a complete equivalent table selects H2; absent
artifact selects H3 and requires BLOCKED.md.

Exact commands:

```
find /path/to/new-artifact -maxdepth 3 -type f -print
rg -n -C 4 'ROM_OPEN|EXECUTE|STATE_LOAD|STATE_SAVE|RESET|CoreDoCommand|EEPROM|savestate|entry|load' /path/to/new-artifact
```
