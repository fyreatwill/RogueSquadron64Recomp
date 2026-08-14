# NEXT work unit (s1079)

HYPOTHESIS-ID: oracle-512-consumer-gate-audit

Run exactly one bounded static audit of the input-consumer boundary. Enumerate
all generated callers and raw dispatch references for
`getControllerNewButtonsPressed` (`0x80079F50`), then enumerate generated
callers/raw entries for the menu/controller handlers around `0x800B47D0` and
classify the first state/asset predicate that can prevent those reads before
the width-320 attract loop. Do not run a new oracle arm, change the input
schedule, or arm a freelist watch.

Competing hypotheses and discriminator:

* `H-gate-state`: a concrete generated caller predicate or state value gates
  the consumer before width 320; static references identify it.
* `H-raw-dispatch`: no generated caller reaches the consumer, but a raw-address
  dispatch path does; the dispatch site and target identify the boundary.
* `H-audit-open`: generated and raw enumeration cannot establish either a gate
  or dispatch owner; the remaining boundary needs a new independent observation.

Discriminating measurement: the audit must produce a complete address/caller
table for both symbol families. A concrete predicate on a generated caller
selects `H-gate-state`; a raw dispatch with no generated caller selects
`H-raw-dispatch`; an incomplete table selects `H-audit-open`. Before any build,
run:

```sh
rg -n -S '80079F50|getControllerNewButtonsPressed|800B47C4|800B47D0|menuControllerInput' \
  RecompiledFuncs patches src docs scratch tools --glob '*.{c,h,cpp,md,txt,sh}'
rg -n -S '80079F50|800B47D0|800B47C4' \
  /Users/williambuckley/Documents/Tools/rogue_squadron64 --glob '*.{c,h,txt,s}'
```
