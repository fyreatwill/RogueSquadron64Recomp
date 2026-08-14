# NEXT work unit (s1136)

HYPOTHESIS-ID: m4-ground-truth-accumulator-origin

Run the retail oracle arm with whole-RDRAM positive control and a targeted
physical watch over `0x688:0x710`, derived from the port capture's
`r9=0x670..0x6C0` and output record `r9+0x18..0x4F`. Include `--vi-trace` and
the documented Start schedule; do not interpret a targeted null unless the
matching shaded phase is reached. Do not change the port probe.

Competing hypotheses and discriminating outcomes:

- H-retail-writer: retail PC-attributed writes hit the candidate range in the
  reached phase, so the game owns this record edge.
- H-retail-null: whole-RDRAM control and matching phase pass, but the target
  range stays quiet; the candidate port-side source is rejected.
- H-phase-unreached: whole-RDRAM control passes but the matching shaded phase
  is not reached; the targeted null is unevaluable.

Discriminator: whole-RDRAM hit count, targeted PC-attributed hits, and VI phase
reachability from the same oracle invocation.

Expected command shape (resolve the configured oracle core/ROM paths from
`tools/oracle/README.md`):

```sh
tools/oracle/build/rs64_oracle --core <debugger-core> --rom <retail-rom> \
  --secs 180 --watch-write 0x0:0x800000 --watch-write 0x688:0x710 \
  --vi-trace --press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start
```
