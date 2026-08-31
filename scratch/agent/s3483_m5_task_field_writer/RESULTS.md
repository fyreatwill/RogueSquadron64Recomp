# Session 3483 — M5 task-field writer values

The independent Rice oracle ran the retail ROM for 45 seconds with a whole-RDRAM
positive control and a physical watch on `0x1494A0:0x1494A8`. The control fired
15,248 callbacks, the task-field watch fired 5,248 writes, and the title phase
reached 633 width-1024 VI frames. The post-store-PC detail captured 629 rows at
each target PC in the title phase. At `0x8009177C`, retail stored only
`0x80171CE0` or `0x80173B20`; at `0x80091784`, it stored only sizes 1 or 2.

The validated port arm reached title origin `0x00790400`, fired the task-writer
control, downstream-store positive control, and host-task boundary, and emitted
480 host rows plus 2,048 writer rows before the watchdog's later 512 phase.
Title writer values were `0x80171CE0` (102 rows) and `0x80173B20` (100), but
also `0x8018DD30`/size 1 and `0x8018FB70`/size 3. The first host rows exposed
those same extra payloads. Both arms therefore have live controls and the first
divergence is present at the writer operands, selecting `H-WriterOperand` and
refuting `H-TaskPayloadMutation` at this boundary. The remaining question is
which upstream producer supplies the two extra port operands.

The initial oracle attempt was killed before shutdown, so it is retained only
as a control/reachability artifact; the natural 45-second capture is the
qualified result. No code or runtime behavior was changed.
