# Next work unit: M5 - classify the early 0x8000834c crash (spTaskSchedulerThread+9632)

HYPOTHESIS-ID: m5-audio-destub-sequence

s4228: crash at last-guest-pc 0x8000834c (SEGV in spTaskSchedulerThread+9632, 1-3 s after launch, phase 320) hit a stale-save run; 0x8000b650 SIGABRT hit a fresh run. Both save states crash -> not volume. In stale2 x19=0xffffffff8011a89c (sign-extended guest ptr used as host ptr?).
Hypotheses: (a) a sign-extended/unmasked guest address reaches host deref in the scheduler thread (recomp idiom, class audit); (b) race with audio thread start (timing); (c) bad DMA descriptor.
Discriminator: disassemble spTaskSchedulerThread+9632 (lldb/objdump on the binary or the generated .c), find the load that faults, name the register source; then count crash frequency over 10 stale-save runs of 10 s each (cheap) with a log of that register.
