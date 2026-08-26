# s2490 M5 descriptor comparison

The independent oracle positive control ran before the port capture and
reached its 10,000-callback threshold in 8 emulated seconds: 10,000 writes
from the whole-RDRAM watch. This validates the oracle watch instrument only.

The Debug build succeeded. Two short captures were non-results for the target
phase: one used three early Start presses and reached only 1024/title; the
other used the same input mistake with a 70-second window. The fixed run used
the established eleven-Start boot-relative schedule and reached 512 /
`0x6AB400` at 26.1 seconds. It produced 36 phase-10 and 28 phase-12
comparison rows, plus the existing descriptor and scheduler controls. The
capture ended by the probe watchdog with no crash marker.

Every selected field in every comparison row had:

```
MEM_W == TO_PTR != explicit memcpy(rdram + (task_ptr - 0x80000000))
```

For example, phase 10 field 0 was `memw=0x60A77444`,
`explicit=0x00000001`, `toptr=0x60A77444`; field 2 was
`memw=0x0CB0001D`, `explicit=0x800825D0`, `toptr=0x0CB0001D`.
The explicit bytes retain the coherent OSTask shape from s2489.

The source contract explains the equality: `MEM_W` and `TO_PTR` subtract the
sign-extended constant `0xFFFFFFFF80000000` from their guest address. The
callback currently accepts `task_ptr` as `uint32_t`, so the generated callback
argument is zero-extended before those macros are evaluated. Both macro and
struct-view reads therefore agree on invalid host memory. This is
source-contract evidence paired with the same-run measurement. No runtime
behavior was changed.
