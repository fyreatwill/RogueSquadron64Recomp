# NEXT (s7400)
HYPOTHESIS-ID: replaced-libultra-output-contract

s7399 closed class BI (event-message payloads, H-none on two lines) and with it the message-queue family BB-BI.

Work unit, class BJ (replaced-libultra output contract):
1. Static census tool tools/s7400_replaced_contract.py: enumerate every `<name>_recomp` in lib/N64ModernRuntime/librecomp/src
   and src/main (the replaced() helper in tools/s7397_timer_census.py), and for each: does it set ctx->r2 (return value),
   which guest pointers it writes (TO_PTR / MEM_W / memcpy targets), and the libultra contract for the same function
   (return codes: osContInit bitpattern + OSContStatus, osContStartQuery/GetQuery errno, osContGetReadData OSContPad errno
   and stick/button format, osEepromProbe/Read/Write, osPfs*, osAiGetLength/GetStatus/SetNextBuffer return, osGetCount/
   osGetTime monotonic + units, osViGetCurrentFramebuffer/NextFramebuffer, osSpTaskYielded, osDpGetStatus...).
2. Join with guest call sites (jal in /tmp/s7392.dis) and classify what the caller does with v0 / the struct (reuse the
   s7392 TESTED/USED/IGNORED classifier and the s7399 use_of slot follower).
3. Hypotheses: H-none (every consumed output matches libultra), H-ret (a replaced fn leaves r2 stale or returns a value
   libultra never returns, on a TESTED site), H-struct (an out-struct field the guest reads is left unwritten or in a
   different format). Discriminator if static does not settle: per-fn runtime hook of (r2, struct bytes) on route
   tools/s7392_mq_run.zsh owner + RETAIL=1 with a planted control; plant controls relative to ctx->r29 only (s7399 lesson).
Fix any H-ret/H-struct deviation behind a default-on env with =0 restoring the old path, two-arm qualified.
