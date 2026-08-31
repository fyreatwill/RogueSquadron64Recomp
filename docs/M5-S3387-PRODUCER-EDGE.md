# M5 Session 3387 — upstream producer edge

The independent retail oracle and the port were run with phase controls and
positive controls in the same iteration.

Retail oracle (`oracle_s3387_fixed.log`): the whole-RDRAM watch crossed the
10,000-callback positive-control threshold; title 1024 and hangar 512 phases
were observed. In hangar origin `0x006AB400`, each PCM target span had 449
writes. The phase writer histograms attributed 256 writes per span to
`0x800078EC`, 116 to `0x80007670`, and seven each to the remaining small
initialization PCs. The oracle exited cleanly after 2,850 VI.

Port (`port_s3387/run.log`): the phase and audio/task/PCM controls fired and
the route reached title 1024 and hangar 512. Its only target-overlap static
row was `0x8008F2CC -> rs_memset`, filling `0x801797B0` for `0x298` bytes
with zero. There was no port row for `0x8002BEEC`, `0x800078EC`, or the
retail `0x80007670` target-writing edge. Port PCM boundary samples remained
nonzero in title and zero in hangar, consistent with the established source
boundary.

This selects `H-RetailDrivenProducer`: the retail target bytes are produced
by the `0x800078EC`/`0x80007670` writer family, while the driven port route
only performs the zero-fill at `0x8008F2CC`. It refutes a matching port
producer edge at this observed target boundary. This does not establish that
the port's zero fill is illegitimate, nor identify the missing producer's
input or dispatch contract.
