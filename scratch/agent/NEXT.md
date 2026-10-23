# NEXT: lvl1 ground darkness - fold the raw RDP capture
HYPOTHESIS-ID: g3-lvl1-mesh-ground
H1 legit dark field; H2' ground tris get dark shade/prim/env; H3' wrong TLUT/palette.
Step: read SOAK-RESULTS s5989_lvl1_rdpbin; `ls -la scratch/agent/s5989/lvl1_rdp.bin` (if ~600MB it was truncated: lower HOLD or find ord range of flight via log [tricnt]).
Run: python3 -I tools/rdpbin_tri_colors.py scratch/agent/s5989/lvl1_rdp.bin <flight ord> | sort by n; compare meanRGB/prim/env of the big textured-shade groups (ground) with the hill/sky groups.
Outcomes: ground groups meanRGB<~30 with bright env/prim => dark vertex shade (H2'); normal shade, different timg/tlut => H3'; all bright => H1 or renderer-side tint (then G1 (c)/(d)).
