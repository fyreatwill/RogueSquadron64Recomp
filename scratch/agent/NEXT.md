# NEXT (s7542)
HYPOTHESIS-ID: class-gc-host-write-vs-signal

Fold first: SOAK-RESULTS lines for s7541_wbw_rwait (WBW under NODRAIN=3: any [wbw] live reader that is not RT64 self/updateScreen
hash = a real consumer of a late writeback -> item 18(c)) and s7540_rwait_cost (fps, tools/g1e_level_fps.py; needs AC).

Work unit: class GC idiom census (offline, one tool, the s7538 model). s7541 found that under NODRAIN RT64 writes guest RAM AFTER
the completion signal. Generalise: enumerate EVERY host-side write into guest RAM (grep rdram/RDRAM/MEM_W/memcpy-into-rdram sites in
src/, lib/N64ModernRuntime, lib/rt64 hle writebacks, audio/PI/SI/cont/eeprom paths, debug/probe/patch writers) and classify each:
- H-before: the write completes before the message/flag that tells the guest (PI DMA, SI, RT64 drained writeback).
- H-late-noreader: lands after the signal, and a measured census shows no guest reader (cite: s6938, s7391, s7541_wbw_rwait).
- H-late-reader (OPEN): lands after the signal and the guest reads it -> fix order.
- H-guest-thread: done on the guest thread itself (synchronous by construction).
- H-diag: only under a diagnostic env (list the env).
Tool: tools/s7542_gc_census.py with --controls (mutation: move one PI copy after its message post -> row FAIL-check; delete a
classified site -> unclassified>0), exits 0 only with 0 unclassified and 0 OPEN. Expected outcomes: all rows classify (close GC) or
a named H-late-reader row (next unit: measure + fix it, two-arm).
Battery note: timing arms need ALLOW_SLOW=1 and are comparable only in-run.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
