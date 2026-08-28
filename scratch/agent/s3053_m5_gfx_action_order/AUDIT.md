# Session 3053 M5 gfx action-order audit

The retail preflight used Rice, the eleven-Start schedule, VI tracing,
watches for `osSpTaskStartGo` (`0x80033FCC`) and the DP consumer body
(`0x8001C38C`/`0x8001C3D4`), and a whole-RDRAM positive control. The control
reached its cap, retail reached title `1024 @ 0x00790400` and hangar
`512 @ 0x006AB400`, and the watched PCs reported 5,341, 1,852, and 1,852
executions respectively.

The port build added one phase-keyed host table at action dequeue, SP
completion entry/return, `send_dl` entry/return, DP completion,
DP external enqueue/delivery, and display-list submitted/parsed/completed
callbacks. The build succeeded after adding the forward declaration required
by the new action hook. The LLE-only AUTOPILOT capture was run from `build/`
with phase logging and route controls.

Port counts: action dequeue 559; SP completion entry/return 559 each;
`send-enter` 5,203; `send-return` 559; DP completion/enqueue 559 each;
external delivery 455; display-list submitted/parsed/completed entry/return
559 each. Phase-4 rows consistently order action dequeue, SP completion,
display-list submission, `send_dl` return, DP completion, enqueue, parse, and
completion callbacks. The phase control fired, but the port again stopped at
VI 640 / `0x0066A500`; target phases never armed and route preparation stayed
`accepted=0`.

This is a positive instrument result but an insufficient target-phase
discriminator. It supports that the observed pre-target gfx action path is
internally ordered and that DP delivery is asynchronous after enqueue; it
does not establish that this order causes the VI-640 boundary, nor compare
host callbacks against retail. No behavior change was made.

Evidence: `oracle.log`, `run.log` in this directory.
