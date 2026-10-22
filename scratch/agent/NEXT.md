# NEXT: G1 - s5838: confirm the 32 forced P sends actually have effect (victim hp / objective counter change), then find why real aim never gets within 8.8 u.
Step: with ROGUESQ_TELE_BOLT=1, log victim state (+hp or kill flag) before/after each P SEND (apply_s5833 stage 4) and the mission objective counter (see s5787/s5788 counters). Control: N sends. If effect present -> G1 is only a steering problem (stick yaw ignored by ship, s5821): investigate why stick does not turn the ship. If absent -> receiver (msg-5 handler) is defective for player-sourced hits.
Run: env ROGUESQ_LOG_HITS=1 ROGUESQ_TELE_BOLT=1 zsh scratch/agent/g1_fire.sh s5838 320
HYPOTHESIS-ID: g1-mission-progression
