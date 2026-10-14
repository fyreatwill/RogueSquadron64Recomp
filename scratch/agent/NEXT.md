# Locate retail mission frames and compare to m0's extra splice sprites

HYPOTHESIS-ID: ovl2c-splice-mission-effect

Done s4803: m0 (splice) phase-6 texrects strictly superset m1 (drop); extras ~6x8px glyphs at y~288/~411, up to +119/frame. Tool: scratch/agent/s4807_align.py (pickle /tmp/s4807.pkl).
Hypotheses: H-splice-correct (extras match retail HUD/text sprite geometry), H-splice-garbage (extras do not appear in retail at any frame), H-other-writer (retail has a large sprite set neither arm reproduces).
Discriminating measurement: in retail rdp.bin find frames with tri>1500 and texrect>=100 (mission-like); compare multiset of (w,h,tile) and y-band of m0-only extras against them. Offline only.
