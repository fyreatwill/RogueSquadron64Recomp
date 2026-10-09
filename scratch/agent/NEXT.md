# Next work unit (s4343): ground-truth the retail branch candidate boundary

HYPOTHESIS-ID: m5-step9-retail-branch-boundary

s4342 passed the qualified in-process-autopilot route, host control, title VI
1024, hangar VI 512, and existing filter controls. The active D740 witness
recorded 256 rows. Its object-backed table words varied with the cursor and
its decoded a0/a1 values were small index/selector values; neither matched
retail C904's retained `branch_state=0x0010/0x3108`. The direct C88C callsite
probe itself was not reached on this route.

Competing hypotheses:

- H-retail-table-producer: retail writes or reads the C904 object/table field
  carrying the `0x0010/0x3108` family.
- H-retail-selector-producer: retail carries that family through the decoded
  selector/stack path rather than the table word.
- H-port-boundary-remap: neither port candidate is the retail counterpart and
  the semantic mapping boundary is earlier than C904.

Discriminator: one independent retail oracle run with whole-RDRAM, title, and
hangar positive controls plus phase-gated read/write watches on the C904 object
and its table-relative candidate range. A retail writer/reader carrying the
`0x0010/0x3108` family selects table versus selector; a qualified C904 witness
with no such access rejects both direct port mappings and moves the boundary
earlier.

Run requirements:

1. Read `tools/oracle/README.md` before changing the watch instrument and arm
   its whole-RDRAM positive control first.
2. Build all retail candidate watches in one oracle instrument/run; no port
   A/B and no external field-key route.
3. Positive controls must visibly fire in the same run.
4. Do not add a guard or alter decoder/RSP/AI behavior.
