# s2481 — runtime SP lifecycle at the image route

Date: 2026-08-26

The eleven-Start `tools/probe.sh` capture was phase-valid: VI width 512 with
hangar origin `0x006AB400` appeared at 26.1 seconds. The run later crashed in
`recomp::do_rom_read` after 13 frames, after the target lifecycle had fired.

- One `event-wiring register` row registered SP queue `0x8011A420` with
  message `0x80128C70`.
- There were 64 `event-wiring complete kind=SP` runtime publications.
- Target-route `audio-route` rows reached phase 12, width 512, origin
  `0x006AB400`, with `run-task-return`, `sp-complete-enter`, and
  `sp-complete-return` rows.
- Independent `audio-sp-route` rows showed external enqueue, external
  delivery, then `guest-receive` for the same queue/message. The phase-12 row
  at ordinal 1474 completed this sequence.

Verdict: H-SPConsumed selected. The SP message is registered, published by the
runtime, delivered to the game queue, and received by guest-side code on the
qualified image route. This rules out a registration gap and a
published-but-unconsumed SP message at this boundary. It does not identify the
post-receive consumer/output contract. The late `do_rom_read` crash is a
separate failure and is not used to interpret the completed lifecycle.

Evidence is two-source within one run: runtime event-wiring publication rows
and independent audio SP queue-path rows.
