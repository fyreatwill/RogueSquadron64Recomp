# NEXT (s7302): G5e - fog/haze on the extended draw-distance far band (owner request), dd2/dd4/dd8 16:9
HYPOTHESIS-ID: g5e-far-fog
State (s7301): beyond ~88 cells the dd8 ring is already inside the haze (invisible, R_TOG A/B with R40 control). s7300 saw the far
terrain at dd>1 as a dark grid-textured band reaching the horizon on L1 (sheet docs/owner_sheet_s7300_horizon_dd.jpg, l1d8 t=250/290).
Owner wants the extended terrain to melt into haze instead of popping.
Unit: first grep CURRENT-TRUTH/PROJECT-OVERVIEW for the existing fog levers (ROGUESQ_DD_MELT, ROGUESQ_FORCE_FOG, G3c(a)/G5e items,
tools/g5e_edge_score.py) to learn what DD_MELT already does and where the dark band comes from. Hypotheses:
  - H-fog-unscaled: the game's fog start/end are retail-distance; at dd>1 cells beyond fog end draw at full fog colour (flat) -> the dark
    band is fog-coloured far terrain under a dark fog/haze colour; fix = scale fog with dd (DD_MELT may already).
  - H-shade: the band is vertex-shaded dark (lighting/LOD shade at distance), not fog; fix = melt far ring toward the sky colour.
  - H-lod-tex: the grid texture is the far LOD tile texture tiled without fog; fix = fade outermost ring.
Discriminator: one same-run toggle of DD_MELT (=tog if supported) on L1 dd4 16:9, g5b capture + g5e_edge_score (hard80 per third) +
mean colour of the far band vs sky colour per phase. Then owner sheet dd1/dd2/dd4 on 3 levels.
SOAK_NEEDS_IDLE=180 header if queued (window/keys + capture).
