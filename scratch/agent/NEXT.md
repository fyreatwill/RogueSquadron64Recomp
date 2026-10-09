# Next work unit (s4338): qualified C904/C88C field join

HYPOTHESIS-ID: m5-step9-retail-port-field-join

The s4337 fixed A/B qualified the known in-process autopilot route: it reached
VI 512 with 253 C88C rows and 256 direct rows. The external field-key arm was
route-invalid despite the corrected from-boot schedule, so it is parked.
Compare the retained retail C904 table against the qualified port C88C table.
Use one run, phase-gated to origin `0x006AB400`/`0x006AB800`, and require the
positive control plus VI 1024/512 and nonzero C88C/direct counts.

Competing hypotheses:

- H-payload-parity: C904 and C88C fields correspond after the known address
  mapping, so the earlier descriptor divergence was an instrumentation or arm
  artifact.
- H-descriptor-mapping: the retail C904 fields correspond to a different port
  descriptor field/argument than C88C's retained tuple.
- H-pre-filter-stream: the qualified port route reaches the helper, but its
  source/branch sequence diverges from retail before or at descriptor choice.

Discriminator: a keyed same-phase table of retail C904 rows and qualified port
C88C rows, including caller/object/source/branch fields and descriptor words.
Matching field distributions select H-payload-parity; a stable retail-to-port
field offset with different descriptor arguments selects H-descriptor-mapping;
different source/branch sequence before descriptor choice selects
H-pre-filter-stream. Keep decoder, RSP, AI, and game-path behavior unchanged.

The retail C904 field table remains at
`scratch/agent/oracle_s4335_c904_field.log`; defer comparison until the route
control passes.
