# M5 s4931 — retail parity join remained unresolved

The bounded same-iteration oracle/port capture tested the selected Factor5
route reprepare without changing runtime behavior.

The retail oracle positive controls passed: the whole-RDRAM watch recorded
11,629 writes and the run reached 3,570 VI. Its qualified 512-wide hangar
bucket at origin `0x006AB400` recorded 359 type-2 audio tasks (463 phase task
hits, 104 non-type-2 rows, no invalid pointers). It never reached the selected
mission origins `0x00690400` or `0x00620400`, so it cannot answer the
post-handoff parity question.

The port arm reached `0x00690400`, advanced `update_screen` from 6,720 to
13,824 over 120 seconds, and had zero crash/abort markers. It recorded 885
mission-origin rows, 862 transition controls, and 4,663 transition events;
the origin-specific route/task/PCM counters were zero in this capture while
global route and PCM controls remained positive. This is consistent with the
already-known port attribution boundary but does not establish retail parity.

Conclusion: H-unresolved. The oracle route is qualified for hangar but not the
mission handoff; the null mission comparison is not evidence of absent retail
publication. No guard, skip, or audio behavior change is authorized.
