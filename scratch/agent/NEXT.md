# NEXT: G1d step 42 - label every HUD x block, then implement ROGUESQ_HUD_ANCHOR
HYPOTHESIS-ID: g1d-widescreen
s6149: blocks 6/7 (0x80340384/3B4, pcs 0354..0568) = ring only. Disc/counter/ally x live in blocks at 0x80340264/294/2C4/2F4/324/354 (pcs 0738-0d5c).
Discriminator: build arms from scratch/agent/s6149_run.sh with MARKPC=60:<lo>-<hi> for ranges 0738-083c, 098c-0ac4, 0b58-0d5c (3 arms, MARKCLS=x), compare to base at frame 6500 (baseline: ally 197, counter 200, ring+disc 565). Whichever element moves labels the block. Then implement HUD anchor in fixup: x<160 shifted left, x>=160 right by (virtW-320)/2 under ROGUESQ_ASPECT != 4:3, using the SECOND store values.
