# NEXT work unit (s1046)

HYPOTHESIS-ID: retail-hangar-recipe-contract

Perform one bounded source/config audit of the oracle's documented hangar
recipe. Do not run the game or arm a freelist watch. Compare the exact
`--press` schedule, button-name-to-scancode table, input-plugin mapping, and
director timing against the README's claimed 512 transition. The purpose is
to determine whether the documented recipe is actually reproducible by this
binary/config, not to add another arbitrary button arm.

## Competing hypotheses and discriminator

* `H-recipe-contract`: the README schedule names buttons or timing semantics
  that do not match the current oracle binary/config, so the prior nulls are
  an input-recipe mismatch.
* `H-retail-state`: the schedule and mapping are equivalent, so the width-320
  result is a real retail state-path discrepancy.
* `H-observation-contract`: the recipe is equivalent but the claimed 512
  phase is identified by an origin/VI condition not represented by the
  current trace interpretation.

Discriminating measurement: produce a line-by-line equivalence table from
`tools/oracle/README.md`, `tools/oracle/rs64_oracle.c`, the generated config
from s1045, and the binary `--help`. If every scheduled event maps to the
same physical N64 button word and the timing loop is equivalent, select
`H-retail-state`; any mismatch selects `H-recipe-contract`; an origin/VI
definition mismatch selects `H-observation-contract`.

## Exact commands

```sh
sed -n '60,120p' tools/oracle/README.md
sed -n '300,380p' tools/oracle/rs64_oracle.c
sed -n '450,545p' tools/oracle/rs64_oracle.c
tools/oracle/build/rs64_oracle --help
sed -n '1,220p' scratch/agent/soak_results/s1045_retail_phase_discriminator/start_z-config/mupen64plus.cfg
rg -n "Start|A Button|Z Trigger|Input-SDL-Control1|g_keynames|g_hold_ms|g_press|director|0x6ab|512" \
  tools/oracle/README.md tools/oracle/rs64_oracle.c \
  scratch/agent/soak_results/s1045_retail_phase_discriminator/start_z-config
```
