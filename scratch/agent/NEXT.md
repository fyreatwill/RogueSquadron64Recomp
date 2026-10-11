# Locate the alternate retail name-record source
HYPOTHESIS-ID: m5-audio-destub

s4605 passed the whole-RDRAM positive control and the VI-512 phase gate. The
target span `0x1724C0..0x17250C` received 76 writes, all from guest PC
`0x80007670`; one immediate writer is selected. The source feeding that writer
is still unknown because the port candidate span is `0xFF` in retail.

Competing hypotheses:

- H-alt-source-table: retail `rs_strncpy` receives the five records from a
  different table or copied buffer.
- H-direct-callsite: retail call sites provide direct literals or derived
  pointers to the same writer.
- H-host-translation: the bytes reach the writer through a host-side path with
  no guest-readable source span.

Discriminating measurement: phase-gated retail watch/snapshot around the
writer's source operands or likely source regions, with the whole-RDRAM
positive control. A stable source range containing all five records selects
H-alt-source-table; distinct call-site operands with no shared table select
H-direct-callsite; target bytes with no guest-readable source or operand
activity selects H-host-translation.

Before building an instrument, inspect existing oracle watch options and the
retail `rs_strncpy` call-site/static map. No mitigation.

Artifact: `scratch/agent/s4605_retail_target_writer/retail.log`.
