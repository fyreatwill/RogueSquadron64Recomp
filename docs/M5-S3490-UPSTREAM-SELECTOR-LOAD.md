# M5 Session 3490 — upstream selector-load witness

Ground truth was obtained before changing the port. The independent Rice
oracle passed the whole-RDRAM positive control, reached both title origins
`0x00790400` and `0x00790800`, and produced 2,555 executions at each of
`0x80091060` and `0x80091074`. At the load site, retail returned selector
indices `0` and `4`; the following writer published `0x80171CE0` and
`0x80173B20`.

The port received a regeneration-safe witness immediately after the indexed
load at `0x80091060`. The build succeeded and the fixup script reported the
probe already present after applying it. The prescribed silent LLE/spin-yield
retry reached the 640 route but did not reach either title origin during its
30-second watchdog. Consequently the load and writer controls both remained
zero, and no port-vs-retail selector join is valid in this session.

This is a qualified port-route failure, not evidence for any selector
hypothesis. The next run must re-qualify the Session 3488 silent route before
interpreting the new witness.

ORIGIN: the witness observes selector index, table address, loaded value, and
register context; it does not rewrite, skip, or validate any selector value.
