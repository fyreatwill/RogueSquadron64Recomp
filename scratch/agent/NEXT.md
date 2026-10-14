# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4871 result: messages (L_8008EE44) per synth entry (0x8009123C): retail 1.91 (1345/704), port 0.50 steady. Port synth fires ~2x per AI-done message; retail ~0.5x.
Hypotheses: (H-W2) two registrations/wake sources of the synth entry in the port (callback table 0x8011A8A4 holds 0x8009123C twice) both fire per message; (H-T) a timer/VI-driven extra wake in the port shim; (H-Q) port drops messages.
Discriminator (one build, both sides): log r31 (caller) per synth entry plus the message-count delta since the previous entry; retail twin: oracle --watch-pc 0x8009123C with exec-prev, and r31 peek. If port r31 alternates between two callers -> H-W2/H-T (find them); if single caller with 2 entries per message -> look at queue post path.
Reuse: tools/apply_s4873_msgrate.py, scratch/agent/run_s4873_msgrate.sh (logs land in scratch/agent/soak_results/s4873_bound), scratch/agent/s4873_oracle_msgrate.sh.
