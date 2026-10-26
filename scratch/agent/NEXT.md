# G3 craft-shade pair: same mission, same tick, retail vs port
HYPOTHESIS-ID: g3-inflight-diff
Read docs/G3-INFLIGHT-DIFF.md. Open question: retail X-wing is dark grey, port X-wing light grey/orange.
Hypotheses: H-livery (different craft/level, no defect), H-shade (port lighting/combiner delta), H-capture (frame timing).
Discriminator: retail first mission (s5978_retail_flight.sh with a tick-matched --fb-dump) vs port forced to the same mission
(ROGUESQ_FB_DUMP_EVERY=10), crop craft bbox, compare mean luminance; radar ring is the positive control (must match).
If craft matches -> close G3; if darker/lighter by >15% -> trace the craft combiner/lighting. No aim/steer work.
