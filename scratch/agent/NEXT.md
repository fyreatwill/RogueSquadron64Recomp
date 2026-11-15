# NEXT (s7392)
HYPOTHESIS-ID: guest-msgqueue-drop-census

s7391 closed fb-cpu-reader-census and class BA (guest thread stack headroom: H-fits, two lines agree; build_spwm).

Work unit:
1. Fold s7391_spwm_levels from SOAK-RESULTS (reports scratch/s7391q/report_l{4,7,12}.txt). Pass = alive, report rc 0,
   LINEB control=PASS. On rc 3: the THREAD/SCAN line names the thread and its deepest frame (file:line) -> read that call
   chain (H-overflow if headroom < 0 or lowdirty below spmin: name the writer before any change).
2. New idiom class BB, guest message-queue drops. Hypotheses: H-none (every OS_MESG_NOBLOCK send either checks the -1
   return or targets a queue that never fills), H-drop (a send whose -1 is ignored drops a message in play: a lost
   VI/RSP/DP/service event -> stall or skipped work), H-port-timing (queues fill only because host threads run at a
   different cadence than retail). Discriminator, ONE build: static census of every osSendMesg / osJamMesg call site in
   /tmp disasm of ../rogue_squadron64/build/roguesquadron.elf (flags arg a2 = 0 NOBLOCK; is v0 tested after the call?),
   plus a runtime counter in lib/N64ModernRuntime/ultramodern (mesgqueue send path) of full-queue returns keyed by queue
   address and caller ra, positive control = a planted full queue (env) that must count. Remember export.sh + commit for any
   lib/ edit. Route: tools/s7391_spwm_run.zsh-style keyed route (copy it, swap the build dir).
