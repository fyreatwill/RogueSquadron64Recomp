# NEXT (s7459)
HYPOTHESIS-ID: soak-stall-measure-coverage

s7458 (class DN) gave the g1e owner-recipe harness a real stall score from its present ring (tools/agent/ring_stalls.py, wired into
tagline in tools/g1e_owner_quiet_arms.zsh): present gap >= 30 s, OR presents flowing but VI origin unchanged >= 30 s (the s6993 L4 boot
freeze shape: 235 s hold, max present gap 77 ms), OR a silent tail before the SIGKILL of a live arm. Fake-ring controls + 2 mutation
controls in tools/s7453_harness_death_test.zsh. Real-game control is QUEUED: scratch/agent/soak_queue/s7458_ring_stall_ctl.sh.

Step 1: fold s7458_ring_stall_ctl from SOAK-RESULTS.md. Expected: ok arm vi_stalls30s=0, stp arm vi_stalls30s=1 max_gap_ms>=34000,
  verdict stall_arms=1 stall_na=0, "CONTROL PASS". If stp reads 0 -> the ring did not see a SIGSTOP (H-blind in a new form: present thread
  not stopped? impossible under SIGSTOP; check the ring row times around the plant); if ok reads 1 -> false positive, print the episode.
Step 2 (class DO, offline): census every recipe in scratch/agent/soak_queue/ (top level + hold/) and every live launcher for arms that
  would still print stall_na (no VI stream, no ring, no frozen=). For each: does it launch with ROGUESQ_PRESENT_RING or a [vi] log? Give
  each a measure (ring_stalls.py is reusable: any launcher can set ROGUESQ_PRESENT_RING) or prove it boot-only/one-shot. Hypotheses:
  H-none (only g1e had none, now fixed), H-few (some s72xx launchers / boot hunts still na). Test: extend s7453_harness_death_test.zsh.
