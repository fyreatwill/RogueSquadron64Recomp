# M5 Session 3502 — selector comparison blocked by real-audio route

The independent retail preflight used the Rice video plugin, title-driving
Start presses, a whole-RDRAM write control, a physical watch on
`0x00150000..0x00150008`, and an execution range covering
`0x8009131C..0x80091333`. The whole-RDRAM control fired and the oracle reached
title origin `0x00790400`; the target execution range was live, including
`0x80091320` with `a0=0x801772F0`. The run ended with a normal oracle summary
after 3,565 VI. No bounded physical table-write row appeared in the retained
capture; the positive control and target execution rows prove the watch setup
and title phase, but the target write histogram is not available because the
whole-RDRAM watch consumed the printed hit budget and the requested shutdown
detail did not print.

Two independent port retries used the prescribed real-image/LLE/spin-yield
route and the selector pre-call, caller, producer, and table-selection
witnesses. Both crashed before title at host `spTaskSchedulerThread+9556`,
guest PC `0x8000834C`, with no 1024 phase or selector control/row. The retries
therefore do not discriminate table-writer value, writer route, or index
selection. They do establish a reproducible qualification blocker for this
route, distinct from an absent selector witness after title.

The next selector comparison must first obtain a qualified real-audio title
run with the same positive controls. No selector or audio state was rewritten,
skipped, or validated.

ORIGIN: diagnostic-only retail and port route, phase, selector, and crash
observations; no audio state, selector value, task field, or output was
rewritten, skipped, or validated.
