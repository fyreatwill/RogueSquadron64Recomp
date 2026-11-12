# NEXT: host completion-delivery audit (lost-completion livelock class)
HYPOTHESIS-ID: host-completion-delivery-class
Context: s7196 closed the guest busy-poll class (docs/COOP-SCHED-POLL-CENSUS.md). It also showed that a host path
returning without posting its completion freezes the game: the PI unknown-region path did this, forced arm 3/3 FROZEN,
now fixed. Siblings of that path were not audited.
Unit (offline first, class-audit model):
 1. Enumerate every host function that owes the guest a completion message. Each one ends in
    enqueue_external_message* or do_send to a guest mq:
    - lib/N64ModernRuntime/ultramodern/src/events.cpp: SP task done, DP full sync, VI retrace, AI, SI
    - timer.cpp
    - librecomp pi.cpp (the remaining paths) and the flash / eeprom / controller-pak code in librecomp
    - src/rsp/dpc_bridge.cpp and our src/main overrides (osSpTaskStartGo, osViSwapBuffer, etc.)
 2. For each one, list every early return, error branch, env-gated skip, drop or guard that exits WITHOUT posting.
    Classify each: DEAD (cannot happen), SAFE (hardware also posts nothing), or HAZARD (hardware completes but we do not).
 3. For each HAZARD: a forced arm like ROGUESQ_PI_UNK_TEST, old path vs fix, plus a same-run control, in the
    boot_freeze_hunt owner env.
Hypotheses:
- H-none: all paths always post. Close the class, then take the next ladder rung (item 3c).
- H-lost: a gated/early-return path exists. It is a boot-freeze candidate if [stall-wait] would show the waiter IN recv
  on that mq.
Discriminator: the table.
