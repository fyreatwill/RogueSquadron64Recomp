# M5 Session 3517 — selector producer context capture was route-blocked

The independent retail oracle ran first with a whole-RDRAM positive control,
the physical selector span, and the range `0x8009189C..0x80091B3C`. Controls
were live: 10,012 whole-RDRAM writes, 12 selector-span writes, and 123 range
execution hits. The hangar phase armed at width 512, origin `0x006AB400`.
The selector writer histogram remained `0x8008F228` and `0x8008F264`, six
hits each. Retail range rows showed the first entry context as
`s1=a0=0x80165ED0`, `a1=0x12`; later rows retained `s1=0x80165ED0`.

Added `rs64_m5_selector_producer_context` through
`tools/apply_s3517_m5_selector_producer_context.py` at the port's
`initN64RspMixer` entry (`0x8009189C`), recording the matching register set.
The Debug build passed after correcting the generated call's block closure.

Two port attempts were then made with the new witness. The first used a
six-event autopilot schedule and remained at VI 640 through the 120-second
phase wait. The fixed run used the previously qualified `ROGUESQ_AUTOPILOT=1`
route and remained at VI 640 through the 180-second wait. Neither reached the
512 hangar phase, so the new port witness and selector-store witness had no
target-phase rows. The producer/context hypotheses remain unevaluable on the
port side; this does not contradict the qualified retail range result.

The immediate blocker is therefore the pre-title route, not a selector-context
conclusion. No audio, selector, task, or output state was rewritten.

ORIGIN: diagnostic-only oracle watches and port entry witness; all stores and
audio state remained untouched.

Evidence: `scratch/agent/oracle_s3517_selector_producer.log`,
`scratch/agent/s3517_selector_producer_port/run.log`, and
`scratch/agent/s3517_selector_producer_port_fixed/run.log`.
