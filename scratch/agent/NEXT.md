# NEXT (s5927): G3 render fidelity - first hangar artifact vs retail framebuffer

HYPOTHESIS-ID: g3-render-fidelity

G2 closed pending owner listen (s5926 regression held; G2-AUDIO-FIDELITY-CLOSURE.md). G1 bolt-damage thread closed s5925.
Take CURRENT-TRUTH "Native hangar artifacts parked" (rim band, holo spikes, stale right edge). Hypotheses per artifact: (A) bad RDP/RT64 state translation, (B) stale framebuffer region not cleared/copied, (C) bad geometry from ucode/DL. Discriminator: dump the port framebuffer (ROGUESQ_FB_DUMP_DIR) and the retail oracle framebuffer (tools/oracle) at the same hangar VI phase; diff offline. Pixel-diff localised to the artifact region with retail clean -> port-side; then toggle one setting within a single run. Positive control: oracle dump of a known-different frame must diff.
NOTE: no `timeout` binary on this host; m6_god_common.sh has its own watchdog.
