# NEXT (s7497)
HYPOTHESIS-ID: m3-partition-over-live-block

Fold first: SOAK-RESULTS line for s7496_eu_levels (tools/s7496_eu_recipe.zsh; `s7496_eu_levels eu arm=` rows in its out.txt): live=0
outside Z=0 + ctl ok==n on L1/L7/L10/L12 -> EU closed 6 levels.

Work unit: class EV. s7496 found the game sets a depth image at address 0 once (~t 11.2 s, both L4 dd1 and L15 dd8); with the guessed
480-row extent it covers live heap blocks 0x0D03E0..0x0DA630 at width 1024. Question: does the RDP/RT64 ever WRITE depth while Z=0?
Hypotheses: H-ev-placeholder (Z=0 is set while no z-update draws run; 0 depth writes / 0 writebacks to [0, w*960)) / H-ev-write (draws
with Z_UPD run while Z=0: RT64 writes depth into low RAM -> name the scene, compare retail) / H-ev-retail (retail oracle sets SETZIMG 0
at the same scene: tools/s7494_es_oracle.zsh reports RDP command order).
Instrument, ONE build: in lib/rt64 rt64_rdp.cpp count draws with othermode Z_UPD while depthImage.address == 0, and in main.cpp
s7493_wb count depth writebacks with base 0 (`[s7497] z0 draws_zupd= wb_base0= sets=`). Positive control: ROGUESQ_S7497_CTL=1 counts the
same for the CURRENT non-zero depth image (must be > 0). lib/ edit -> ./submodule-patches/export.sh + commit.
Run: `env XC=ROGUESQ_S7497_Z0=1 zsh tools/s7496_eu_recipe.zsh` (L4 dd1, L15 dd8). Outcomes: 0 with control > 0 -> H-ev-placeholder,
close EU/EV; > 0 -> oracle the scene.
