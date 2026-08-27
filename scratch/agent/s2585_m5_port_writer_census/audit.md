# Session 2585 audit — port-side M5 writer census

The independent retail capture in s2583 identified `0x8008ED48` as a
nonzero retail writer for `0x800A0F50` and `0x80094648` as a writer into the
`0x80141AD8+index` channel-byte span. This run changed no behavior.

Static enumeration of the generated tree found seven fixed gate stores in
`RecompiledFuncs/funcs_23.c`: `0x8008E9F8`, `0x8008EA34`, `0x8008EB40`,
`0x8008EB7C`, `0x8008EC88`, `0x8008ECEC`, and `0x8008ED48`. It found fixed
channel stores at `0x8008EA44`, `0x8008EA54`, `0x8008EA74`, `0x8008EB8C`,
`0x8008EB9C`, and `0x8008EBBC`, plus the indexed store at `0x80094648`
(`0x1AD8 + s1`, covering the retail watch span). These are the complete
direct store sites in the current generated output; no patch-side store was
found.

The qualified image run reached title (`0x00790400 @ 1024`, phase 8) and
hangar (`0x006AB400 @ 512`, phase 10). Positive controls fired: the audio
dispatch counter reached at least 4608, and PCM source and consumer rows
were both present through row 1664. The complete phase-gated gate census
produced writer rows only for `0x8008EC88` (`reapplyDisplayMode`), once in
each target phase, with post-store gate `0`. There were no runtime rows for
retail-attributed `0x8008ED48` or `0x80094648`, and no PCM guest-writer rows;
PCM samples remained zero in the sampled source/consumer rows.

This selects `H-PortWriterUninstrumented`/missing at the current observable
boundary: the static class and controls are complete, but the retail-named
port callsites did not execute. It rejects `H-PortWriterReachable` in the
qualified title/hangar phases. `H-PortContractElsewhere` is not selected,
because the only observed gate writer is a different site and no PCM or
channel-span value row appeared. This remains a boundary result, not an
explanation of the missing writer or authorization to alter a store, task,
output pointer, or gate.

The first launch attempt was unevaluable because macOS has no `setsid`
command; it was rerun immediately with a direct PID launch. The fixed run
was SIGKILLed at the 110-second bound. Full log:
`scratch/agent/s2585_m5_port_writer_census.log`.
