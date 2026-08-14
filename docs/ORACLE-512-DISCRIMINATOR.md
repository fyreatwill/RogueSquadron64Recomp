# Retail oracle VI-512 discriminator

Design result for s1076. This is a source/config audit; no build, oracle run,
or freelist watch was used.

## Controls already established

- The whole-RDRAM write watch is the positive callback control; it should
  produce substantial traffic in the same run. A zero result without it is
  invalid.
- `--vi-trace` and `--vi-poll` are independent VI controls. Nonzero width
  transitions prove that the retail core is advancing; polling is not a
  substitute for the debugger callback.
- `--pif-trace` proves that the game reads the injected pad word. Named
  `start` is scancode 40 and produces the N64 Start bit; the documented
  eleven-event schedule is not an unverified key-code experiment.
- The tested Start-only, Start+Z, hold-duration, cadence, first-input, and
  120-second variations remain closed as explanations for width-320 attract.

## One new discriminator

Run the documented eleven-Start schedule once with these additional watches:

```sh
--watch-write 0x0:0x800000 --hit-cap 10000 \
--watch-write 0x13A960:0x13A970 \
--watch-write 0x130B40:0x130B58 \
--press 6:start,11:start,16:start,21:start,26:start,31:start,36:start,41:start,46:start,51:start,56:start \
--vi-trace --vi-poll --pif-trace
```

The first extra range is the generated controller current/new-edge storage;
the second covers the selector/state family around `0x80130B40`, including
`demoId` at `+0x14`. Addresses are physical for the oracle and are written
without a KSEG prefix.

Phase-gate interpretation on the first VI width/origin transition, not wall
clock. Record watch-hit PCs and whether each hit is before or after the first
512-origin observation:

| Controller-edge writes | Selector/state writes | VI result | Interpretation |
|---|---|---|---|
| absent, PIF reads present | absent | remains 320 | input delivery/consumption remains open |
| present | absent | remains 320 | a state/config gate is selected |
| present | present | remains 320 | a downstream state/asset predicate is selected |
| present | present | reaches 512 at `0x6abxxx` | hangar route is solved |

The first row is valid only if the PIF trace and whole-RDRAM controls pass. If
the controller range is silent despite those controls, the missing observation
is an execution/alias path rather than another schedule experiment:
`H-oracle-route-open` requires a guest execution breakpoint or equivalent read
watch on the consumer.

This uses one input arm and one state observation in the same run, avoiding
cross-run comparison of an animated scene.
