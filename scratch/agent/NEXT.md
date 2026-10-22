# NEXT: G1 - s5836: player-bolt min segment distance to any NPC sphere is 8.8 u (r~0.26), 0 hits; N control 155 hits. Collision code fine; positioning is what remains.
Step: add an env-gated probe (in apply_s5835_sphere_probe.py) that, once per N frames while P bolts fire, writes the player position to just beside the nearest NPC shape centre (centre seen in the sphere probe), then check P segin>0 / msg-5 sends / objective counter. Control: N SEGIN rows. If P segin>0 but no msg-5 send -> defect is in the send/damage path (audioCueDispatcherNpcHandler 0x8005D1C8+).
Run: env ROGUESQ_LOG_HITS=1 zsh scratch/agent/g1_fire.sh s5837 320
HYPOTHESIS-ID: g1-mission-progression
