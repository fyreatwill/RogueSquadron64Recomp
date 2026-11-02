# NEXT: G3 C-button description screens (LEVEL DESCRIPTION, CRAFT DESCRIPTION) retail match, native 4:3
HYPOTHESIS-ID: g3-description-rdp

State: s6801 closed SELECT YOUR CRAFT (settled + pan) at RDP level. The two "PRESS (C) FOR ... DESCRIPTION" screens have
never been compared to retail.
Hypotheses: H-match (same texrect/tri multisets within same-run controls); H-diff-text (a port-only/retail-only text block,
named by rect coords + PRIM; equal-length text swaps are invisible to the RDP signature, so also crop port window captures
and the retail angrylion dump of one settled frame); H-diff-model (3D craft/hologram tri counts differ beyond phase).
Discriminator, ONE pair run (tools/g3_menu_pair.sh, lvl1.eep, VIDEO=rdplog as s6801 pan2 RENV/XE with RS64_RDP_BIN_MAX_MB=1500):
  first find the C key name the port AP accepts (grep tools/g3_port_capture.sh / AP parser for cup/cdown) and add the
  port->oracle mapping to g3_menu_pair.sh if it differs (oracle names: cup cdown cleft cright).
  PP 17:start,23:start,38:<C>,50:<C or b to close>,56:start,64:start,80:<C>  (SELECT LEVEL desc at 38, back, AVAILABLE CRAFT,
  craft select, craft desc at 80; retail +7.3 s and ~20 s slower by craft select -> move the last C so retail sees it
  after its craft-select fly-in, e.g. port 92, PSECS 110 RSECS 125). Check retail [press] sym != 0 for every key.
Score: python3 tools/g3_rdp_segments.py <bin> retail|port; tools/g3_rdp_segcmp.py per segment. Positive control: SELECT
LEVEL / craft select segments of the same run match (s6785/s6801 numbers); cross-screen control description vs its parent
screen must not match.
