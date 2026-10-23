# NEXT: lvl1 ground darkness - identify the ground timg and check TLUT/texels vs rendered pixels
HYPOTHESIS-ID: g3-lvl1-mesh-ground
s5990: raw RDP shows bright vertex shade for ord=7 tris (H2' dead). Remaining: H3' wrong TLUT/palette/texels; H1 legit; H4 renderer-side darkening.
Step: pick top ord-7 timg groups (python3 -I tools/rdpbin_top_groups.py /tmp/s5989_all.txt 7 20; regenerate with rdpbin_tri_colors.py on scratch/agent/s5989/lvl1_rdp.bin). Extend the analyzer to track tlut load (op 0x30/0x35 loadtlut) addresses and dump TLUT entries for the fmt=18 (CI) timgs; decode a few texels and compare mean to the observed ground framebuffer colour.
Outcomes: decoded texel colours dark => H3'/H1 (asset or TLUT load); bright => H4 (renderer tint/blend, inspect rt64 combine path).
