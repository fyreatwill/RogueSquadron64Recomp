# NEXT: G3c(a) H-grid — outer-ring geometry
HYPOTHESIS-ID: g3c-owner-visual

s6360: colour (s6357) and alpha (s6359) fades both leave the stair-step (jump_med .317 vs .317/.333). Step is geometry of the cell footprint.
Work unit: find the terrain cell submit loop footprint (see s6311 apply10j / EDGE_DROP_D2 hooks in tools/apply_s6311_edgefade.py), add an opt-in arm that lerps outer-ring vertex y toward the horizon/sea height over r=26..34 (ROGUESQ_EDGE_FADE_R2_Y=1), soak nofade/y/yred(control: y raised by +50 so it is obvious) with the s6359 recipe, score with tools/g3c_horizon_score.py.
- y changes jump_med by >0.03 down -> adopt, bundle into DRAW_DISTANCE, ask owner.
- control visible but jump unchanged -> raise footprint radius past 34 instead.
- control invisible -> hook not on the drawn cells; fix before concluding.
