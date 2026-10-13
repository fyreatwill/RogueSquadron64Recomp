# Map musyxSynthFrame_s4562_impl+5808 to a guest instruction

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4776: crash again at +5808 (si_addr 0x38000950e; x9=0x8000950e unmasked guest KSEG0 addr, x8=0x300000000), VI 640 0x696100, load ~9. Same si_addr in 5 sessions -> phase-gated, not load.
Hypotheses: (A) guest register legitimately holds 0x8000950e and one macro path (not rebased) is used, i.e. codegen/fixup bug in that load; (B) a stale/corrupt pointer written to a voice/slot struct; (C) pointer is valid but the access was meant to be through a different base.
Discriminator: produce the generated C for the faulting instruction (compile the TU with -S or find the line via the crash handler's guest-pc dump) and read which register/op uses 0x8000950e; then check whether 0x8000950e is a legit RDRAM address (it is: 0x0000950e physical) -> if so (A) and the macro lacks the mask.
Write ORIGIN: in the session entry if a guard is added.
