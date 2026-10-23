# NEXT: fold s6015_g1b_sample (G1b) - read scratch/agent/g1b_samples/s6015/s*.txt
HYPOTHESIS-ID: g1b-frame-pacing
s6014: quiet arm not quiet (151 vs 171 KB/s; dominant logs are ungated [m4-y8000]/[s3290-stall]/[s3294-stall]/[s3295-disp]); slow-second fraction loud 17.6% vs quiet 23.2%, so the five toggled knobs are not the cause. cpu~wall in slow seconds => not blocking/shader.
Fold: for each s*.txt, read the heaviest stacks of the Gfx/RSP thread (RT64 vs F5 LLE interpreter vs our hooks vs fprintf). Positive control: s*.line must show sd_wall>100 and the sample must contain the gfx thread.
If a logging/hook function dominates: gate it (env) and add a truly-quiet arm (stderr to a file the script does not grep needs run.log - gate the 4 prints above instead). If RT64/interpreter dominates: look at per-scene cost (triangle/vertex count co-variance) next.
