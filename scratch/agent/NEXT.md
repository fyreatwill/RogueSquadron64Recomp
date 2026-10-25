# NEXT: G1d step 40 - cover the HUD elements the x-class mark missed, then implement ROGUESQ_HUD_ANCHOR
HYPOTHESIS-ID: g1d-widescreen
s6147: x-class (addr&0xF==4,|v|>=8) moves ally icon + a ring right; y-class moves ring/ally/missile counter down. Radar disc and missile counter did not move in x arm.
Hypotheses: H-other-pc (disc/counter x stored with |v|<8, other nibble, or by code outside initHudStruct e.g. per-frame updater), H-int (counter x is an s16/int stored not float), H-parent (disc positioned relative to the ring/another node).
Discriminator (one build, one run): in the w census log (scratch/agent/m6/g1_lvl1s6146b_w/run.log) list every float store with |v| in [8,400] regardless of nibble, grouped by block (0x30); then arms per block-set via MARKPC:lo-hi (+ MARKCLS=x) and read which block is the disc / counter. Also census stores to 0x80340240..0x80340430 outside pc 0x800C0084..0x800C1B60 (per-frame writers).
Then implement ROGUESQ_HUD_ANCHOR in the fixup: x<160 shifted by -(virtW-320)/2, x>=160 by +, x-class only, under ROGUESQ_ASPECT != 4:3.
Recipe template: scratch/agent/s6147_run.sh (kill-after-10-dumps, fb VI 6500 contact sheet via PIL).
