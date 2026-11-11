# NEXT: 21:9 / 16:9 sky-corner and horizon fixes on levels other than L6 (G3 ladder, after item 29 closed s7138)
HYPOTHESIS-ID: g3-wide-holes-levels
State (s7138): item 29 CLOSED as retail. The sky top-fade "bins" are a skirt the loader (0x8005AB34) builds from each band rim
edge: v0/v1 (alpha 0) = rim copies, v2/v3 (alpha FF) = rim + fadeH in y, where fadeH = getLevelConfigHalfword (0x8006B604) =
level table 0x800A05D0 + 0x30*level + 0x2C. L6 is the only level 0-20 with fadeH 0 (all others 8, RAM == ROM 0xA11D0), so on L6
every skirt quad has zero area and the ucode emits 0 tris although the frame DL calls all visible bins.
All hole classes (XFIX, GATEFIX, SKYFILL) were measured on L6 only. On fadeH-8 levels the skirt DOES draw, under the SKYFILL corner.
Hypotheses:
- H-clean: L1/L4/L15 at 21:9 dd4 show 0 hole swaps with the three fixes on, and the skirt blends into the full-viewport clear.
- H-seam: the skirt (alpha 0 -> FF over 8 units) leaves a visible seam/stripe against the SKYFILL clear colour (clear colour vs
  level fog colour differ: table +0x24 vs +0x28 colours differ on most levels, e.g. L1 82B6D3 / 80B8D0).
- H-newclass: a level-specific hole class (different sky HOB or band layout) that L6 did not have.
Discriminator: one run per level, tools/s7138_arm.zsh <lvl> <name> "ROGUESQ_ASPECT=21:9" 120 180 with CW=?? as s7136 Y1, then
tools/s7136_post.zsh scratch/s7138 <name> (hole score + angrylion replay), tools/s7138_bindegen.py (skirt non-degenerate) and
tools/s7138_streamseq.py on a corner-above-band swap (skirt tris present, their colour vs clear colour). Same-run control: a
HORIZON_SKYFILL=0 arm on the same level must show holes (>0) or the 0 is not a result.
Owner save rule applies. CURRENT-TRUTH ~59 KB: keep edits net-zero.
