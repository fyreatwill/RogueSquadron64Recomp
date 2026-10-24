# NEXT: G1c - fold s6064_heap_px25d2 + s6065 px2 dd2 300 s holds (L1/5/10)
HYPOTHESIS-ID: g1c-heap-exhaustion
Fold SOAK-RESULTS lines for s6064_heap_px25d2 and s6065_px2_dd2_hold300_l{1,5,10}; logs in scratch/agent/m6/g1_lvl1g1c6425d2, g1_lvl*g1c6065px2l*.
Check: rc, crashlines, vi_stalls30s, post-poolx '[heaplog].*-> 00000000' (awk after the 'cap 2048' line), then `python3 tools/g1c_ddtog_fold.py <m6dir> 4500 --hud` for terrain fraction/HUD.
Outcomes: all 3 holds clean -> done-criterion crash part met; then judge whether terrain fraction rose vs dd1 (if flat, H-hidden: find far-clip/frustum/fog in terrain submit). Any crash -> backtrace it.
