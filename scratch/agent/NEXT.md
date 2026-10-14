# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4878 result: DEDUP=1 gives 0.99 synth entries/message vs 1.97 (DEDUP=0). Unit: run DEDUP=1 three times to PHASE VI1024 (scratch/agent/run_s4878_dedup.sh 1, but use PROBE_PHASE_TIMEOUT run longer than the 100 s sleep; look for PHASE lines/crash), compare with the s4870 AI-ring delta per synth entry (apply_s4870_producer.py; retail +2 per chunk). If stable and AI delta moves toward retail, make dedup default-on (flip the getenv default in tools/apply_s4878_synth_dedup.py, rebuild). Do NOT flip gate-write force-zero stubs (hung boot 4x). Beware: launcher env edits must be verified by grepping the log for the s4700 control rows.
