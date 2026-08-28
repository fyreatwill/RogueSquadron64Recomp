# s2877 M5 route-state consumer discriminator

The retail-first run used Rice, the whole-RDRAM positive control, and a bounded
execution range. The control reached 10,000 callbacks; retail reached title
(`0x00790400:1024`) and hangar (`0x006AB400:512`). The range census selected
`playObjectiveVoiceLine2` (`0x800C7D1C`), reached from `0x800C5D40`, as a
phase-live audio consumer candidate.

The same-build image/silent port arms used the qualified LLE-only route, the
same phase-relative Start schedule, and the new consumer probe. Both reached
only 640 (`0x0066A500`) and stopped at the 180-second phase-gate timeout. Both
had no crash or abort marker and no target-phase consumer rows.

| arm | positive control | title/hangar | consumer rows | result |
|---|---:|---|---:|---|
| retail oracle | 10,000 | title + hangar | retail range hit | candidate selected |
| port silent | n/a | no; 640 only | 0 | H-route-invalid |
| port image | n/a | no; 640 only | 0 | H-route-invalid |

This is route-failure evidence for this run, not evidence that the consumer is
missing or equivalent in the port. No behavior change was made.
