# NEXT: fold s6470_dd3_break_ab (d2ctl/d3nf/d3free/d3pin) and decide pin vs farclip vs real
HYPOTHESIS-ID: g1c-dd8-limit
Dirs: scratch/agent/m6/g1_lvl1s6470_{d2ctl,d3nf,d3free,d3pin}. Metric: median tri over tricnt lines with tri>300 (see s6470 entry; dd2 961, dd3 pinned 575).
Outcomes: d3pin~575 & d3free~960+ -> pin artifact, dd3 fine, redo dd4/6/8 unpinned. d3pin~575 & d3free~575 & d3nf~575 -> real dd3 break, test farclip gate (0x80136DC0)
and scale overflow. d3nf differs from d3pin -> farclip fix is the lever. d2ctl must reproduce ~960 (control) or the run is invalid.
Also view a frame from each arm (fbd/fb_*_w512.ppm) rather than trusting the ground score.
