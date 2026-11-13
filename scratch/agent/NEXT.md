# NEXT (s7284): offline classification of load-edge gaps, then the next non-owner-gated rung
HYPOTHESIS-ID: g5c-load-edge-gaps
State: s7283 closed GPU contention (commit count not the lever). Every Next-steps item 2-16 is owner-gated.
Bounded offline unit (no game run): across every s7277-s7283 toggle run (scratch/s7277/*.toggle + present rings
scratch/s7277/ring_*.txt + scratch/s7272/<TAG>/sheet.txt), list every gen gap >=250 ms with its distance to the nearest
toggle edge (on->off / off->on) and the load type (cpu/gpu, GPU_ITER).
Hypotheses:
  - H-edge-drain: every off-window gap >=250 ms lies within ~1 s after an on->off edge of a GPU arm (in-flight foreign buffers
    drain after SIGKILL) -> harmless; note in OWNER-OPT-INS ("a short hitch when a GPU-heavy app stops").
  - H-quiet-freeze: some lie >2 s from any edge -> a real quiet-host freeze; take its frames (KEEP sheets) and name the stall.
  - H-cpu-edge: CPU arms show edge gaps too -> scheduler re-ramp, not GPU drain.
Positive control: the SIGSTOP control gaps (179/280/381 s) must appear in the list with distance labels.
Then: write a tool (tools/s7284_edge_gaps.py), fold, and take the next ladder rung (ITERATION 3c); do not change defaults.
