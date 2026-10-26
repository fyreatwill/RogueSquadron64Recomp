# Next: fold s6317 calibration soak, pick fade centre + cell size, compute fade per cell
HYPOTHESIS-ID: g3c-owner-visual
Soak s6317_g3c_cal2 writes scratch/agent/m6/g1_lvl1s6317_cal2/run.log with [edgefade5] lines (cell=col,row cam=32 floats @0x80138D20 pl=12 floats @0x80137DBC).
1. Offline: windowed mean(col),mean(row) vs each candidate float (cam[i], pl[i]) as the flight moves; the linear fit with r>0.95 gives centre source and cells-per-unit. Positive control: cell col/row must vary (>1 distinct value).
2. Hook: in A6C0 epilogue use rs64_ef_col/row with that centre to compute f and blend toward haze (apply10c f formula, distance in cells). 
3. Rerun dd3_log vs dd3_fade, score with tools/g3c_edge_score.py, send PNGs to owner.
