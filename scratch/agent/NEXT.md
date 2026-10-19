# Next work unit
Post-mission menu/results overlay fidelity: run m6_keyed_hold_post.sh once, dump framebuffers (ROGUESQ_FB_DUMP_DIR) phase-gated on the
VI-origin transition to 0x720000/0x790000 after phase 6; fix dump stride per VI width (read from VI regs, not 320) offline; inspect
frames for garbling/missing text/wrong palette. Positive control: same run's in-mission frames dump correctly. Do NOT use autopilot 'r'.
Second-mission start is already covered (s5435/s5437); do not redo it.
HYPOTHESIS-ID: menu-overlay-fidelity
