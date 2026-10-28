# NEXT: land a dd>1 span-reject bypass inside ROGUESQ_DRAW_DISTANCE and qualify it
HYPOTHESIS-ID: g1c-span-reject-predicate

s6528 confirmed: at dd4 the span compares at 0x80042D8C/0x80042DA4 reject cells that hold visible terrain (tight fraction 0.047 -> 0.209 when forced, 3 recurring steps).
Hypotheses: H-bypass-safe (accepting all in-window cells at dd>1 is fine: no spikes, frame time ok), H-bypass-costly (extra cells blow the tri/time budget or the ucode cap), H-saturation-writer (the clean fix is upstream: the span grid's -128 clamp floor at the writer in streamTerrainGridCellsByDistance/scanConvertTriangleToSpanTable; bypass is only a workaround, needs ORIGIN naming).
Discriminator: build default-on bypass when DRAW_DISTANCE>1 (env opt-out), run pinned lvl1+lvl5+lvl10 dd4 with G1B frame-time instrument vs dd1 retail control (same recipe, 240 s); score terrain fraction, VI/s, crashes. Also trace why grid holds -128 (pre-clamp inputs unlogged) to name the writer.
