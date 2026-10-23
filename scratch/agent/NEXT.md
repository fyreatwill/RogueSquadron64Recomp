# NEXT: G1c - fold gated knob arms s6042_dd15s/dd2s/dd3s
HYPOTHESIS-ID: g1c-draw-distance
H1: dd2 crash was pre-terrain use of the knob/clamp (gate fixes it: dd2s reaches mission, keys.log `mission t=`). H2: gate insufficient, still nomission => stream fn itself runs pre-terrain with scale-independent garbage; look at what dd1 does differently (knob 1.0 skips clamp only). H3: in-mission deaths (dd2r died_in_verify, dd3 +9960 wild ptr) are a separate real window-overrun; take lldb backtrace.
Discriminator: SOAK-RESULTS lines for s6042_*; m6/g1_lvl1g1cdd{15,2,3}s/keys.log: `mission t=` present vs nomission; then crash site if any. Positive control: dd1 arm keys show mission t~87.
Then, if dd2s holds 240s: levels 5 and 10 at 2x, compare [g1b] frame time with the G1b baseline, distant-terrain fb fraction.
