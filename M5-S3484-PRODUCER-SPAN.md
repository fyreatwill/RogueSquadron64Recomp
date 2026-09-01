# Session 3484 — M5 producer-span capture

The retail Rice oracle ran for 45 seconds with a whole-RDRAM positive control,
physical watches on `0x18DD20:0x18DD50`, `0x18FB60:0x18FB90`, and the task-field
span `0x1494A0:0x1494A8`. The whole-RDRAM control fired 24,592 times, the two
candidate spans fired 4,681 and 4,673 times, and the task-field watch fired
5,238 times. Retail reached 632 title-origin VIs. Candidate-span writer PCs
included initialization at `0x80018F5C/0x80018F60` and active title writers
`0x80091078`, `0x8009114C`, `0x80091168`, `0x80091170`, `0x80090CA4`,
`0x80090CB0`, `0x80090CBC`, `0x80090CC8`, and `0x80090DE4`.

The rebuilt port reached title origin `0x00790400` and fired both the existing
task-writer control and the new source-span control. Its nine bounded source
rows were initialization of the two candidate records at `0x80091078`, then
nearby-field stores from `0x8009114C`, `0x80091168`, and `0x80091170`; none
stored either extra operand value. The task writer emitted 205 rows for each
normal operand (`0x80171CE0` and `0x80173B20`) but only one row each for
`0x8018DD30` and `0x8018FB70`.

The independent retail writer census and the port source/task census both had
positive controls and title rows. Together they reject the measured hypothesis
that the extra port operands are produced by writes into these two candidate
source spans. They do not identify the actual upstream read or table-selection
source; that remains the next boundary.

No game behavior was changed. The added hook is phase-gated and observational.
