# Next work unit (s4308): independent retail read-PC/value join

HYPOTHESIS-ID: m5-audio-destub-sequence

State (s4307): the expanded port hook passed a phase-gated positive control and
captured 256 target reads plus the writer join without a crash. Port's first
read was 0x17D9E0=0x8017D9F8 before any selected writer, unlike retail's first
post-free sequence. This independently selects H-retail-layout-different at
the consumer boundary; the exact lifetime/consumer fault is still open.

Competing hypotheses:

- H-shared-read-layout: retail and port read the same logical node fields at
  the same guest PCs; the apparent difference is sampling order only.
- H-retail-read-layout-different: retail's physical read-PC/address/value
  sequence differs from the port sequence after the shared free/reuse path.
- H-port-only-consumer: the port reaches a read PC or value absent from the
  retail read watch, identifying the port-only traversal that reaches the bad
  DMA fields.

Discriminator: run the independent oracle with whole-RDRAM read control first,
physical target --watch-read 0x17D000:0x17E200, and the documented hangar
route; retain read PC/address/value rows around the first post-free sequence.
Compare that table to the already-captured controlled port rows. Matching
logical tuples select H-shared-read-layout; a different legitimate retail
sequence selects H-retail-read-layout-different; a port-only read PC/value
selects H-port-only-consumer. Missing whole-RDRAM control or VI 512 is invalid.

Exact command:

Before changing code, inspect the existing oracle read-watch and post-target
sequence options; run one oracle arm with --watch-read and the whole-RDRAM
positive control. Do not add a guard or skip.

Expected outcomes: matching read tuples select H-shared-read-layout; a
different legitimate retail read layout selects H-retail-read-layout-different;
a read PC/value absent from retail selects H-port-only-consumer. No control or
no VI-512 phase is invalid. Do not add a guard or skip from this probe.
