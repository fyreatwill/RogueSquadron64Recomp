# Next: ONE further M3 idiom-class audit that commits a guard (or resume M5 per docs/M5-AUDIO-PLAN.md)
HYPOTHESIS-ID: m3-idiom-class-audit
Closed: s5233 swizzle, s5234 host-wrapper ptr args, s5235 PI/EEPROM lengths, s5236 rsp.cpp rdram index masks (signed/unsigned base class already closed s5094-s5100). Candidate: raw rdram[]/memcpy index audit in src/main (debug threads, g_recomp_rdram_for_wp_raw users) for unmasked guest-derived addresses; or queue a soak with ROGUESQ_LOG_S4213 on to exercise the s5236-edited probes. Write hypotheses first.
