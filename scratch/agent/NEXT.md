# Next work unit: requalify the M5 source-construction predecessor pair

HYPOTHESIS-ID: m5-source-construction-predecessor

Retry the s4139 caller/entry discriminator only with a retail capture that
reaches title 1024 and hangar 512. Keep the existing port source-context hook;
do not change image, wait, cap, predicate, slot state, guest behavior, or host
writeback.

Competing hypotheses and discriminator:

- H-retail-port-caller-match: a qualified paired run shows matching retail and
  port caller/argument setup before `0x800078EC`.
- H-retail-port-caller-split: a qualified paired run repeats a divergent
  caller, source pointer, or length before the zero-valued store.
- H-route-invalid: either arm lacks whole-RDRAM control or one of the two
  target phase gates.

The s4140 port arm is phase-qualified and emitted 256 sampled rows per phase:
title `a0=0x80178C80`, `a2=0x298`; hangar `a0=0x801797B0`, `a2=0x298`; `ra=0`
is still an instrument limitation. Both s4140 retail retries remained at VI
640, so they cannot update the caller split.

Before the next build, run the retail oracle with the existing accepted
schedule and require the whole-RDRAM control plus title/hangar gates. If it is
qualified, build once and run the port with:

```sh
python3 tools/apply_s4140_m5_source_context.py
cmake --build build --config Debug --target RogueSquadron64Recomp
```

Use the s4140 real-audio/LLE/solo/spin-yield environment and phase settings
from the prior iteration. A missing gate selects H-route-invalid and must not
be used to infer a source or caller fact.
