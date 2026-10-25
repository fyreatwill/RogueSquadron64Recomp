# NEXT: G1d step 43 - label remaining HUD x store ranges, then ROGUESQ_HUD_ANCHOR
HYPOTHESIS-ID: g1d-widescreen
s6150: 0b58-0d5c = counter shield icon (digit text separate); 0738-083c and 098c-0ac4 move nothing visible. Ally icon + disc x not yet found.
Run 4 arms from scratch/agent/s6150_run.sh (edit case list) with MARKPC=60 ranges: 800c0568-800c0738, 800c0ac4-800c0b58, 800c0d5c-800c1000, 800c1000-800c1b60. Eyeball HUD vs scratch/agent/m6/s6149b baseline. Then implement the anchor in a fixup script using the second-store values.
Fallback if sites stay scattered: anchor at the consumer (the code reading 0x80340240 table) instead of the stores.
