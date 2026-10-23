# NEXT: G1c - fold the three queued arms (s6018_g1c_pos/r2/lod2)
HYPOTHESIS-ID: g1c-draw-distance
Hypotheses: L-radius (0x8003A538 float scales terrain window), L-lod (0x8009ECB0 thresholds), L-budget (streamTerrainGridCellsByDistance 0x80042B50 caps), L-fade (haze).
Discriminator: in soak logs, split RDP tricount / RT64 drawn lines by the preceding `[g1c] state=retail|scaled` marker. pos arm (radius 0.25) MUST show fewer tris in scaled state (positive control) - if not, the lever does not reach terrain and the whole instrument is void (check [g1c] dump printed non-zero radius).
If r2 raises tris in scaled state: L-radius works; check pop-in/crash, then try 1.5/3x and build ROGUESQ_DRAW_DISTANCE wrapper. If r2 flat: read 0x80042B50 for its own radius/budget cap and add a lever. Then fb-dump pairs for distant-terrain pixel fraction.
