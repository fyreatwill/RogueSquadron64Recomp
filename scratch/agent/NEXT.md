# NEXT (s7229): why FPS60 flight runs rigid 30/s stretches of 21-62 s in the coverage harness
HYPOTHESIS-ID: fps60-flat30-stretches
Context (s7228): LEVEL=4 owner recipe via scratch/agent/g1_level_coverage_common.zsh: every arm shows a 21-s flat-30 run at t=76 and
others up to 62 s (game swap cadence rigid 33.3 ms, present path free, VI timer 60 Hz). s7204 measured fl_shown ~60 at the owner
recipe on a quiet host. The harness logs ~1M stderr lines per run ([s3290-stall]/[s3294-stall]/[s3295-disp]/[s5901] dominate).
Hypotheses: H-log (diag logging on the game thread pushes frames past 16.7 ms), H-cost (scene cost at that route time: RSP/guest >16.7),
H-host (host load / E-core placement; check load avg and thread QoS), H-mode (FPS60 latches a 2-VI cadence after one late frame and
needs a trigger to return).
Run (one build, current binary; arms sequential, same route, windowed display 0, no virtual display): copy scratch/s7228/arm.zsh minus
the virtual display; arm A = as s7228; arm B = same + minimal logging (find the env that silences s3290/s3294/s3295/s5901, e.g. the
s7204 recipe's quiet env; grep PORTING-STATE s7204). Score with tools/s7228_present_rate_score.py style flat-run census on Q rows
plus per-second swap cadence; add per-frame guest/RSP ms if a cheap existing counter exists (G1B instrument, grep CURRENT-TRUTH).
Outcomes: B has no long flat runs -> H-log (harness artefact; owner unaffected, document); both flat at t=76 -> H-cost/H-mode, then
compare frame cost in that window (H-cost: cost >16.7 throughout; H-mode: cost <16.7 but cadence stays 2 VIs -> fix the latch).
