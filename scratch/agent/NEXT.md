# NEXT: lvl1 ground darkness - decode TLUT/texels from s5991 RDRAM dump
HYPOTHESIS-ID: g3-lvl1-mesh-ground
Read new line in SOAK-RESULTS.md (s5991_lvl1_rdpbin_rdram); dumps in scratch/agent/s5991/rd/rdram_*.bin (word-swapped ^3 per 4 bytes; phys addr = file offset).
Write tools/rdram_decode_tlut.py: dump TLUT RGBA5551 entries at 0x563980 and 0x563260 (256 entries or 16), and CI8 texels of timg 0x469cb0, 0x4ad7a0; compute mean colour of texels->palette.
Outcomes: dark mean => H3'/H1 (asset/TLUT contents wrong; find TLUT writer); bright (~140-220) => H4 renderer-side darkening, inspect rt64 combine/blend path.
Positive control: decode a known-bright group (timg 0x4e1950 fmt=10 IA/RGBA) and match its mean to the analyzer's shade.
