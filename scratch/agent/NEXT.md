# NEXT: G1c - fold s6037_dd15c/dd2c/dd3c
HYPOTHESIS-ID: g1c-draw-distance
Read scratch/agent/m6/g1_lvl1g1cdd{15,2,3}/run.log. Outcomes: (a) no SIGBUS and gridlog gx<=terr-1 => clamp fixes dd2; then compare distant-terrain fraction in fbd/ captures vs dd1 (same phase), frame time (G1b instrument), and run 1.5x/2x 300 s on levels 5 and 10. (b) still crashes => get new gridlog tail and backtrace; the clamp is not the only OOB source (check 64-wide window bitmaps 0x80132DB0/0x80133DB0 when w>64).
