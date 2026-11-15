# NEXT (s7395)
HYPOTHESIS-ID: mesg-event-rebind

s7394 closed class BD (heap-mutex re-seed window: 0 intrusions in 40 windows; retail re-seed-while-held fixed by
ROGUESQ_S7394_HOLDFIX default on, =0 retail).

Work unit:
1. Fold s7394_holdfix_levels from SOAK-RESULTS (scratch/s7394q/report_l{4,7,12}.txt). Pass = alive, report --fix rc 0
   (FIX-ARM CONTROL PASS, no RACE row), holdfix_skips > 0 per level. A RACE row or a hang after a skip: read the
   [s7394-win] row (owner, ctid, ckey) and name the thread before any change; HOLDFIX=0 reproduces retail for an A/B.
2. Class BE (message-queue lifecycle sweep, next idiom): osSetEventMesg / osViSetEvent / osSpSetEvent-style event
   re-registration. Grep-enumerate every guest call site in /tmp/s7392.dis (regenerate with
   mips64-elf-objdump -d --no-show-raw-insn ../rogue_squadron64/build/roguesquadron.elf if missing), class each: event,
   queue, message, one-shot vs re-bound per scene. Hypotheses: H-none (every re-bind targets the same queue or a queue
   with no pending event messages), H-strand (a re-bind moves an event to a new queue while the old queue still has a
   waiter that only that event wakes -> stall candidate), H-port (ultramodern's event table keeps a stale binding).
   Discriminator, ONE build: hook osSetEventMesg_recomp / osViSetEvent_recomp (lib/N64ModernRuntime/librecomp/src/
   ultra_translation.cpp, export.sh + commit) -> per (event, caller) count re-binds, old queue, old queue's blocked_on_recv
   waiter and whether any later post reaches that old queue; planted control: re-bind a fake event away from a queue with
   a linked fake waiter (must count 1 stranded). Route tools/s7392_mq_run.zsh, owner + RETAIL=1 arms.
