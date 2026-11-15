# NEXT (s7397)
HYPOTHESIS-ID: timer-lifecycle

s7396 closed class BF (thread lifecycle): H-none on route, upstream thread_queue_remove walk fixed (ROGUESQ_S7396_TQFIX default on).
Fold soak s7396_tq_levels (SOAK-RESULTS) first: pass = alive + 0 crash + tools/s7396_tq_report.py rc 0 on L4/L7/L12.

Work unit, class BG (timer lifecycle, next in the message-queue lifecycle family):
1. Static: census the 3 guest osSetTimer/osStopTimer jal sites in /tmp/s7392.dis (template tools/s7396_thread_census.py):
   caller, OSTimer struct (a0), countdown/interval, mq, msg, in-loop, callers. Read ultramodern timer.cpp (osSetTimer/osStopTimer,
   the host timer thread) for the same kind of latent defect s7396 found in threadqueue.cpp: re-arm of an already-active OSTimer
   struct, stop of a timer whose message is already queued/in flight, interval timers, and host-side lifetime of the struct.
2. Hypotheses: H-none (each timer struct armed once at a time, stops only hit armed timers), H-rearm (osSetTimer on a live struct
   leaves two host entries -> double messages or a send into a re-created queue), H-stop-late (osStopTimer races the host timer
   thread: message sent after stop returns).
   Discriminator, ONE build if the code read does not settle it: hook osSetTimer_recomp/osStopTimer_recomp -> log struct, live
   flag (host table), mq, msg; count sends after stop. Planted control: arm one fake timer twice + stop it with a message pending
   (must report 1 rearm + 1 late). Route tools/s7392_mq_run.zsh owner + RETAIL=1 arms (one at a time).
   Any lib/ edit: ./submodule-patches/export.sh + commit.
