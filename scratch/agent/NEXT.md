# Next work unit

HYPOTHESIS-ID: m5-task-family-retail-compare

s4872 result: synth 0x8009123C is the VI-retrace callback (retail single caller 0x80019B74). Port: retrace walk ~117/s ~ 2x VI updates (update_screen #5888 vs ~5800 AI-done msgs), AI-done 1x per VI update, strict 1,0 alternation. Retail: 1.91 AI-done per retrace, VI-per-retrace unmeasured.
Hypotheses: (H-R2) port posts two retrace messages per VI update (host VI callback + a second source/timer); (H-A1) port AI-done paced to 1 per VI (host audio DMA length/cadence) while retail does ~2 per VI; (H-VI) retail VI is not 1:1 with retrace.
Discriminator (one build, both sides): port - count posts to the retrace queue by poster per VI update, and AI_LEN per AI-done message; retail - oracle VI-poll rows joined with 0x80019B74 exec counts and AI_LEN writes per VI. Two posters -> H-R2; AI_LEN differs -> H-A1.
Reuse: tools/apply_s4873_msgrate.py + apply_s4874_caller.py (live tree already patched), scratch/agent/run_s4873_msgrate.sh, s4873_oracle_msgrate.sh.
