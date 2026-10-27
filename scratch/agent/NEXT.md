# NEXT: why does streamTerrainGridCellsByDistance (0x80042B50) return an empty / tiny list on 15% / 24% of dd4 calls
HYPOTHESIS-ID: g1c-dd8-limit
s6492: ForFace never skips cells; the loss is upstream: empty list 220/1416 dd4 calls (7/2337 dd1) + tiny lists with no cell < DEB4. s6491 listnz was a stale-r16 artifact.
Hypotheses: H-radius (stream's window/radius test uses a bound not scaled by dd), H-pool (cell/link pool alloc failure returns 0 under dd4), H-gate (an early-exit on camera-moved / grid-cache-valid flag).
Do: map the stream function's exits (delegate a scouting agent like s6492: control flow, early returns, what v0 is), add cumulative per-exit counters [streamcum] (positive control: dd1 exit mix), run scratch/agent/s6492_forface.sh arms (dd1/dd4, 150 s, concurrent). Also fix the deb4 readback in [ffempty] (read via MEM_W(-0x214C, 0x800A0000)) if still wanted.
Outcome: dominant exit on empty-list calls names the gate; read its operand.
