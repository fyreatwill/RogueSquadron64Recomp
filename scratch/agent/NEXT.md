# Next work unit: one generated-symbol renaming candidate
HYPOTHESIS-ID: generated-symbol-renaming-sweep

Bound the sweep to one candidate outside the already-audited
`func_800E9AE0`. First enumerate nearby placeholders and companion-map names:

`rg -n 'func_0x|func_[0-9A-Fa-f]{8}' RecompiledFuncs docs tools | head -200`

Then inspect the candidate's generated function span and its companion m2c/map
entry with bounded `rg`/`sed` windows. Write `docs/RENAME-S5396.md` containing
the address, span, callers, companion evidence, and decision. Rename only when
the generated tree and companion map agree; otherwise leave the symbol intact.

Competing hypotheses:

* H1: one placeholder has a matching companion semantic name and exact span;
  a regeneration-safe mapping edit and regenerated host name are justified.
* H2: candidates have names but no exact generated-span agreement; no rename
  is safe and the audit records the missing discriminator.
* H3: the selected region is already synchronized or contains only data and
  wrappers; this lead is closed and the next ranked region must be selected.

Discriminator: exact address/span agreement between the companion map and the
generated function, plus a non-placeholder semantic name. Do not infer a name
from callers alone.
