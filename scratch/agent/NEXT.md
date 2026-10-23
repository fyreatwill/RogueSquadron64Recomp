# NEXT: fold s6013_g1b_lvl1 / lvl10 soaks (G1b frame-pacing)
HYPOTHESIS-ID: g1b-frame-pacing
Hypotheses: H-host (gfx thread cpu<<wall, qos low, load1 high), H-rsp (sd_cpu ~ sd_wall and rises with scene), H-shader (sd_wall spikes with low cpu, on new materials), H-log (logB bursts coincide with vi<30/s).
Fold: `grep '\[g1b\]' scratch/agent/soak_results/s6013_g1b_lvl*.log`. Find seconds with vi well below the normal rate; see which column co-varies. Positive control: vi/sec must be nonzero and sd_wall>0 in every line. If no slow seconds appear, queue a busy-host arm (run a CPU burner alongside) and a log-quiet arm.
