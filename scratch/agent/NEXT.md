# NEXT work unit (s1239, blocked)

HYPOTHESIS-ID: retail-external-entry-boundary-closed

The prior external/front-end census is complete. Do not build or run. The
workspace artifact check in s1238 found no genuinely new retail-entry artifact.
The next work unit is blocked until the human supplies one frontend/launcher
source or binary invocation, or another callable retail state source, that can
perform a state-changing handoff not represented by the audited oracle/core
contract.

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

Exact commands after the artifact is supplied:

```
find /path/to/new-artifact -maxdepth 3 -type f -print
rg -n -C 4 'ROM_OPEN|EXECUTE|STATE_LOAD|STATE_SAVE|RESET|CoreDoCommand|EEPROM|savestate|entry|load' /path/to/new-artifact
```
