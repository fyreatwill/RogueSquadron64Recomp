# M5 Session 3485 — selector/load join

The independent Rice oracle passed its whole-RDRAM control (19,300 callbacks),
candidate-span controls (4,643/4,657), and reached 3,566 VI. The preceding
block executed 154,327 times overall. Retail's selected source at
`0x800916F0` remained within the two normal values established by s3483:
`0x80171CE0` and `0x80173B20`.

The port received a regeneration-safe probe at `0x800916D8–0x80091714`.
The task-writer and writer-entry controls fired, and 4,096 bounded title rows
were emitted. At `0x800916F0`, the port selected `0x80171CE0` 264 times and
`0x80173B20` 265 times, but also selected `0x8018FB70` twice and
`0x8018DD30` once. At `0x80091710`, the port's `a2` values included sizes 1,
2, and 3. These extra selections match the extra writer/enqueue operands from
s3483.

This selects `H-SelectorDivergence`: the first measured divergence is in the
port's pre-writer selected operand, not an intervening mutation after
`0x8009177C/0x80091784`. The upstream table read or writer remains unresolved.
The capture is diagnostic-only; no task fields or audio behavior changed.

Evidence: `scratch/agent/s3485_m5_selector_oracle.log` and
`scratch/agent/s3485_m5_selector_port.log`.

ORIGIN: this iteration observes selector registers and task-writer values; it
does not rewrite, skip, or validate the differing operands.
