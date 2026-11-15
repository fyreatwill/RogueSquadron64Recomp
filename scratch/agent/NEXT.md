# NEXT (s7396)
HYPOTHESIS-ID: thread-lifecycle-waiter

s7395 closed class BE (event re-binding: 6 live sites bind once each, owner + retail, H-none).

Work unit, class BF (thread lifecycle, next message-queue lifecycle idiom):
1. Static: extend the census pattern (tools/s7395_event_census.py as template) to osStopThread (3), osDestroyThread (2),
   osCreateThread (12) and osSetThreadPri (6) sites in /tmp/s7392.dis (regenerate with mips64-elf-objdump -d
   --no-show-raw-insn ../rogue_squadron64/build/roguesquadron.elf if missing). Per site: target thread (a0; 0 = self),
   entry fn, callers, in-loop. First check whether librecomp replaces each call (grep *_recomp in lib/N64ModernRuntime/librecomp/src).
2. Hypotheses: H-none (every stop/destroy targets self or a thread not blocked on any queue), H-dangle (a stopped or
   destroyed thread stays linked in a queue's blocked_on_recv/send list, so a later post wakes a dead thread or the
   message is lost), H-recreate (osCreateThread re-uses an OSThread struct that is still linked or running).
   Discriminator, ONE build if the logs do not already show it: hook osStopThread_recomp / osDestroyThread_recomp /
   osCreateThread_recomp -> log target tid, its state, and whether it is linked on any queue waiter list; planted control:
   stop a fake thread linked on a fake queue (must report 1 dangle). Route tools/s7392_mq_run.zsh, owner + RETAIL=1 arms.
   Any lib/ edit: ./submodule-patches/export.sh + commit.
