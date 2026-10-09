# Next work unit (s4473): M5-AUDIO-PLAN next step after closing the status-03 lead

HYPOTHESIS-ID: m5-status03-service-reaping

State (s4472): port status 03 / request-byte 4 chain is IDENTICAL to retail (C21C=2, C2B0=3, C268=4, B7CC at hangar+~10s). The "retail B7CC x0" premise was wrong. Lead has no retail-divergence basis; close it.
Residual question: does the port reach C268/B7CC at a comparable time after hangar entry (retail: VI512 at 38.4s, first 2/3 at 43.3s, 4 at 48.7s), and what does the port do right AFTER B7EC (retail: status continues; port: crash family?). Compare the post-status-03 sequence (B7EC and following status writes 0x8009B7xx) retail vs port using s4472_run.sh logs (ROGUESQ_LOG_S4472 control already fires).
Pick: read docs/M5-AUDIO-PLAN.md, take the next un-run de-stub step rather than another status-03 table. Expected: a step with a validation soak.
