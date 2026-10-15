# M5 s4932 — retail mission-entry qualification

The bounded retail oracle capture passed its controls: the whole-RDRAM watch
reached its 10,000-hit positive threshold, VI polling recorded 10,716 lines,
and the qualified `0x006AB400` 512-wide hangar bucket produced 630 type-2
audio-task rows. The selected mission origins were then observed independently:
`0x00690400` first appeared at about 97.4 seconds and `0x00620400` at about
180.1 seconds.

The same-build port baseline reached `0x00690400` after the first Start/A pair,
advanced `update_screen` from 6656 to 13888 over 120 seconds, and had zero
crash/abort markers. Its existing origin-specific audio counters were zero in
this baseline; that is not a retail parity measurement.

This selects **H-retail-mission-qualified** over route absence and invalid
instrumentation. The next experiment may join retail and port publications at
the two selected origins. No guard, skip, or other behavior change is
authorized by this result.

ORIGIN: no mitigation or game-behavior change; this iteration only qualified
the independent retail route and retained the existing port baseline.
