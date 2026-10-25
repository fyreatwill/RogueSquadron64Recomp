# Title-art x-origin: name the guest writer of the 64*scale extra offset
HYPOTHESIS-ID: g1d-widescreen
s6225: origin = (W-512)/2 + 64*W/512 on 4 widths (683/796/900/1024); 4:3 gives 0. So guest centres by (W-512)/2 then adds one scaled 64px tile (or centres a grid of width 512-64*... ). Test: the leftmost scaled column (x=(W-512)/2) is missing or is a non-64 rect — dump all texrects of one phase-4 submit at w900 (x0..x1, tmem tile) and see whether a rect starts at 194 with a different width, i.e. the "shift" may be a metric artifact of my 64-width filter.
Hypotheses: H-artifact (a wider/narrower rect at (W-512)/2 hidden by the ==64 filter -> grid is actually centred, defect is elsewhere, e.g. missing column); H-writer (guest adds 64*scale to origin: find the DL/vertex operand via lldb write-watch).
Discriminator: print all phase-4 texrect x0,x1 for one submit at w900 from scratch/agent/m6/g1_lvl1s6225_w900/run.log (offline, no run), and compare with a screenshot w900_05.png.
