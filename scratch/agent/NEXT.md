# NEXT: what does record byte3 mean, and is the spawn ys legitimate?

s5782: sampler ret=1 iff scaled player y (ys) > cell record b3; player flies ys -130..-80 over b3 -126..-82 cells; deaths follow sustained ret=1 bands. Instrument: tools/apply_s5781_terrain_sample.py ([terr] lines, ROGUESQ_LOG_MTM=1).

Work unit: (1) static: read sampler branches from 0x800692D8 onward (funcs_16.c:~4300+) to see which later tests turn a b3<ys hit into ret=1 vs 0 and whether record bytes 4+ matter. (2) One run of s5777_althold.sh with the [terr] cap raised to 2000 and the player's y at the FIRST sample after each respawn logged; compare with the s5738 snapshots' spawn y and with other missions' spawn ys (Mos Eisley hangar spawn).
- H-spawn-below: spawn ys is lower than retail's (port places player at wrong y / wrong grid origin 0x80136DF0 area) -> compare grid origin fields vs the level file.
- H-grid-origin-wrong: records are fine but oy/ox/oz (struct +0x18/+0x20/+0x2C) loaded wrong, so cells map to the wrong b3.
- H-b3-ceiling-by-design: the region is a legit ceiling and the player is meant to be pushed back (ret=1 -> deflect), and our deflect fails.
Control: ret flips 0->1 in-run (already seen).
HYPOTHESIS-ID: g1-record-byte0
