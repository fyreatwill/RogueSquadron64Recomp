# Who calls shutdownMusyXEngine (0x8008ECA4) in the port on the VI-640 phase-3 route?

HYPOTHESIS-ID: factor5-overlay-0x2c-splice

s4781: retail never runs shutdownAudioEngine/shutdownMusyXEngine in 85 s driven (5 transitions; shutdownMusyXVoices does, from 0x800678EC). The port runs shutdownAudioEngine on phase 3 (s4780). Hypotheses: A) a port stub/trap/gate routes a wrong branch into shutdownMusyXEngine (mis-resolved jump table or overlay call); B) a game path legitimately calls it from a state the port reaches early (init-failure/retry path caused by an audio stub returning a failure value); C) arrival by recompiler fallthrough from an adjacent function.
Discriminator: in the port, log ra/caller, a0 and the value at 0x800A0F50 on entry to shutdownMusyXEngine (via a fixup script, not generated code), plus the guest ra chain; run to VI 640 phase 3 (quiet machine). Control: the same log style on shutdownMusyXVoices (retail caller 0x800678EC) must fire on title route. Retail has 0 hits at 0x8008ECA4, so any port caller is divergent. A => caller PC is not a retail callsite; B => legitimate caller whose condition differs from retail; C => ra lands in an adjacent function.
Do NOT add a guard until the caller and divergent condition are named (ORIGIN rule).
