# NEXT: G1d step 44 - anchor HUD at the consumer of the element table
HYPOTHESIS-ID: g1d-widescreen
s6151: store-range bisect exhausted (ally icon + radar disc never move; digit = 800c1000-1b60, counter icon = 0b58-0d5c, ring = blocks 6/7).
Work unit: find the function(s) that READ the 0x80340240 element table (x at +0x24, y at +0x28) to build draw commands (grep recompiled funcs for loads from that table / lwc1 off +0x24), then add a fixup-script hook adding (aspect_shift * side) to x at read time, side = left/right by x<centre. Positive control: ring+disc+ally+counter all shift in one 16:9 lvl1 frame. Compare against scratch/agent/m6/s6149b baseline.
