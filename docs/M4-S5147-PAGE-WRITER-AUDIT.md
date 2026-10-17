# Session 5147 M4 recycled-page writer audit

The required rename-sweep REVISIT used the independent retail oracle to watch
physical RDRAM `0x1F0000:0x1F1000`, the page that the port previously observed
being rewritten around `0x1F0D74`. Both runs used a whole-RDRAM write watch as
the positive control, Rice video, and continued Start presses through the
mission route.

The first run reached hangar (`0x006AB400`, width 512) and mission
(`0x00690400`, width 512), passed the whole-RDRAM control at 10,000 callbacks,
and reported 1,028,045 writes to the target page. Its phase table headers were
present but contained no writer rows. The fixed rerun added
`--phase-origin-watch 1`; it again reached hangar and mission, passed the
control, and reported 1,026,749 target-page writes, but the phase tables still
contained no writer rows.

Lifetime attribution is positive and entirely guest-PC-shaped: the dominant
writer is `0x800078EC` (926,416 writes), with additional writers including
`0x800C7F08` and the sequential `0x800C7F34`…`0x800C801C` family. This proves
that retail writes the page through game-code PCs somewhere in the run, but
does not prove those writes occur in hangar or mission because the phase
histogram did not retain rows.

Discriminator outcome: `H-unqualified` for the phase-specific M4 question.
The positive control and VI controls passed, so this is not a null caused by a
dead route; the missing phase rows are an instrumentation-boundary failure.
No runtime mitigation or explanation is authorized. This is single-source
oracle evidence and should not close the page-reuse boundary.
