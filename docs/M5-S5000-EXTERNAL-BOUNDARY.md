# s5000 — external retail boundary retry

The independent retail oracle watched whole RDRAM, the render range
`0x8008FFAC..0x80090640`, `0x800901C0`, exact consumer `0x800903F0`, and the
two named writer PCs. The port arm used the keyed route with phase and caller
diagnostics enabled.

Retail controls passed: whole-RDRAM reached 10,000 callbacks; title
`0x00790400` and hangar `0x006AB400` were reached; the render range recorded
24,195,957 executions, `0x800901C0` recorded 244,691, and exact
`0x800903F0` recorded 0. Writers `0x80090C80` and `0x800921E8` recorded 593
and 1,280 executions.

The port reached title and `0x00620400`, but not qualified hangar
`0x006AB400`; its phase join was therefore unevaluable. This selects
`H-route-mismatch` for the retry, not a retail design-dead conclusion. No
guest value was rewritten, filtered, or guarded.

Evidence: `scratch/agent/s5000_external_boundary/oracle.log` and
`scratch/agent/s5000_external_boundary/port.log`.

ORIGIN: diagnostic-only independent retail/port boundary capture; no value
change or mitigation was introduced.
