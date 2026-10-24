# NEXT: G1c - pixel proof of the draw gain, then dd15/dd3
HYPOTHESIS-ID: g1c-draw-distance
s6056 proved dd2 submits 2.4x kept cells (gridlog fixed). Open: H-pixels (extra cells reach the framebuffer) vs H-hidden (downstream L-lod/L-budget drops them).
Discriminator: VI-phase-gated fb capture at the same phase in dd1 and dd2 on lvl1 (PROBE_PHASE_WIDTH / PROBE_KEYS_FROM_PHASE=1, not an fbd index); compare distant-terrain pixel fraction. Positive control: dd0.5 visibly shrinks.
Then dd15/dd3 on lvl1 (pool cap 2048 binds at 2x: consider raising u16 0x80130C4C for dd>2), then ask owner to judge the look. Default stays retail. No macOS `timeout`.
