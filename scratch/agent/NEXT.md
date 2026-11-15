# NEXT (s7393)
HYPOTHESIS-ID: guest-mq-recreate-census

s7392 closed class BB (guest message-queue drops: 59 sites classed, 5 runtime drop families all benign, AI drops = port
timing with no added underrun). Its one residual opens class BC.

Work unit:
1. Fold s7392_mq_levels from SOAK-RESULTS (reports scratch/s7392q/report_l{5,10,15}.txt). Pass = alive, report rc 0 with
   --known (CONTROL PASS, no DROP row outside the 5 families). A new DROP row: read its census verdict
   (tools/s7392_mesg_reviewed.tsv) and name the writer before any change.
2. New idiom class BC, osCreateMesgQueue on a LIVE queue. s7392 found rs_malloc -> ensureHeapInitialized ->
   buildHeapFreeList re-creating the heap mutex 8010FEE0 while it is held; osCreateMesgQueue sets blocked_on_recv /
   blocked_on_send = NULL and validCount = 0, so any thread blocked on that queue at that instant is orphaned (never
   woken) and pending messages vanish. Hypotheses: H-none (every re-create happens with no waiter and no pending message),
   H-orphan (a re-create drops a blocked waiter or a pending message in play -> stall), H-port-timing (only because host
   cadence lets a waiter park there). Discriminator, ONE build: (a) static census of every osCreateMesgQueue call site
   in /tmp/s7392.dis (mips64-elf-objdump -d --no-show-raw-insn ../rogue_squadron64/build/roguesquadron.elf), reusing
   tools/s7392_mesg_census.py's resolver: queue address, caller, and whether the caller can run more than once (init-once vs
   re-init path); (b) runtime counter at osCreateMesgQueue (lib/N64ModernRuntime/ultramodern/src/mesgqueue.cpp, weak hook
   like rs64_s7392_ext, src/main implementation env-gated) keyed by (mq, host return address): create count, and per
   create the pre-state validCount, blocked_on_recv != 0, blocked_on_send != 0; positive control = a planted queue with
   validCount 1 and a fake non-null blocked_on_recv re-created once (must count 1 orphan + 1 lost message). Route
   tools/s7392_mq_run.zsh (owner + RETAIL=1 arms, same binary). Any lib/ edit: ./submodule-patches/export.sh + commit.
