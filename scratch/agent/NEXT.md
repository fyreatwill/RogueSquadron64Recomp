# NEXT (s7458)
HYPOTHESIS-ID: soak-stall-measure-coverage

Class DN (offline + fake-ring controls). s7457 made every live soak launcher print a per-arm `tag=` line; the g1e owner-recipe
harness (tools/g1e_owner_quiet_arms.zsh, 64 recipes, the harness of every G1c/G5e qualification hold) prints `vi_stalls30s=na`
because it runs with no game logging (s6932), so its arms read `stall_na=1` and a frozen-image hold is invisible to the verdict.
It already arms ROGUESQ_PRESENT_RING=$R/ring_$arm.txt (lib/rt64 plume_metal.cpp ~2075: one row per present, CoreAnimation
presentedTime, mach clock, flushed every 64 rows).
Step 1: read the ring row format; write tools/agent/ring_stalls.py <ring> [gap_s=30] -> "vi_stalls30s=<n> max_gap_ms=<m> rows=<r>"
  (n = present gaps >= gap_s while the game was alive; 0 rows -> na). Hypotheses: H-ring (ring is a valid stall witness: a SIGSTOP
  plant shows up as one gap), H-blind (ring rows keep coming while the image is frozen, e.g. same drawable re-presented -> needs fb
  hash), H-absent (ring not written in the harness's build/env).
Step 2: fake ring controls (planted 31 s gap -> 1, steady -> 0, empty -> na) + mutation control; wire it into tagline so g1e arms
  carry a real vi_stalls30s (stall_na drops to 0). Extend tools/s7453_harness_death_test.zsh.
Discriminator: one real check is only possible with a game run; if H-blind cannot be ruled out offline, queue one short g1e soak with
  a SIGSTOP 35 s plant (tools/s7272 shows the SIGSTOP pattern) as the positive control.
