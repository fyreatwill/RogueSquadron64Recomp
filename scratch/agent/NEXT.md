# NEXT work unit (s1078)

HYPOTHESIS-ID: oracle-512-consumer-observation

Add or expose exactly one independent retail-oracle observation on the
controller consumer/alias path, then use it in the same eleven-Start schedule.
Prefer a physical read watch on the consumer's controller-state range; if the
consumer address cannot be established, implement a guest execution-breakpoint
trace at the relevant menu/controller dispatch entry. Do not arm a freelist
watch and do not change the input schedule.

Competing hypotheses and discriminator:

* `H-consumer-read`: the retail game reads the injected controller state, but
  the expected `0x13A960..0x13A970` writer is not the active alias; a read/PC
  hit identifies the real consumer path.
* `H-consumer-not-reached`: PIF delivery is positive but the state/controller
  consumer is never executed before the width-320 attract loop; no read or
  execution hit selects a state/dispatch gate.
* `H-observation-insufficient`: the oracle cannot expose either read or guest
  execution evidence; the missing capability, not a game conclusion, is the
  result.

Discriminating measurement: in one run require the whole-RDRAM positive
control, PIF Start reads, and VI callback/poll agreement, then classify a
consumer read/PC hit before or after the first VI observation. A hit with no
expected writer selects `H-consumer-read`; positive controls with no consumer
hit select `H-consumer-not-reached`; inability to arm or attribute the
observation selects `H-observation-insufficient`.

Before any build, run:

```sh
rg -n -S 'watch-read|watch-rw|DebugBreakpoint|execution|breakpoint|read' \
  tools/oracle src /Users/williambuckley/Documents/Tools/rs64-oracle/src/mupen64plus-core \
  --glob '*.{c,cc,cpp,h,hpp,md,sh}'
sed -n '1,240p' tools/oracle/README.md
```

If the observation already exists, run the resulting one-arm command for 120
seconds from the repo root, capture to `scratch/agent/oracle_s1078.log`, and
use SIGKILL only if a watchdog is required.
