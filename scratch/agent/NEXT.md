# M5: A9 qualified at mission; A10 emitted 0 rows at mission — find why

HYPOTHESIS-ID: m5-audio-destub-mission-route

s4807: A9 inert at mission (0 bad / 143 rows, forced control fires 152/152). A10 (ROGUESQ_LOG_M5_A10, tools/apply_s4681_m5_a10.py) printed 0 rows in the mission run (grep '^\[m5-a10').
Work unit: read apply_s4681_m5_a10.py for its trigger and log tag. Hypotheses: H-A10-tag-mismatch (my grep tag wrong; boring check first: grep -a -i a10 scratch/agent/s4807/normal.log), H-A10-not-reached (site never hit at mission), H-A10-build-absent (patch not in the current build). Discriminator: a forced/positive arm for A10 in the same run.
