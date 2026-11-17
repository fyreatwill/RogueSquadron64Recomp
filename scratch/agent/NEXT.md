# NEXT (s7553)
HYPOTHESIS-ID: class-gm-premission-out-of-rect-writeback

GL CLOSED s7552 (mission rtOut = NOISE re-dither of undrawn pixels, benign). GM: in pre-mission phases RT64's writeback changes
pixels OUTSIDE the pair's drawColorRect with real content. scratch/s7552_gl log_l1/l4/l12 (identical on all 3, shared boot route):
ph=3 fb 640x316 rect 62-639 (pat NOISE): cols 41-56 row ~151 go 0x294B->0x2109, 0x2109->0x18C7 (all channels darker, |d| 1-2, F-rejected);
ph=5 w=796 rows=339 rect 0-795, ph=6 w=640 rect 0-639 also log [s7552-unm]; depth rtOut ph=3 6.5 MB/150 wb, ph=4 28 kB.

Hypotheses:
- H-unmerged-draw: a draw reaches those columns but is not merged into drawColorRect (texrect/fillrect path rt64_rsp.cpp:1194 or a
  rdp.cpp path without merge, or a draw whose rect is clipped by a different scissor) -> hardware draws them too, instrument boundary.
- H-stale-native: the native/render target holds content that never matched RAM there (e.g. a previous fb at the same address with a
  different width, or a fade drawn on a different pair aliasing the address) -> real host write of foreign content.
- H-depth-req: depth rtOut = FbWriteDepthCS requantisation of undrawn depth (float -> 16-bit round trip not exact), benign like GL.
Discriminating measurement, ONE build: in RT64 record per pair the union rect of EVERY draw call (tri, texrect, fillrect; before
scissor) alongside drawColorRect and scissorRect, pass it with rs64_s7551_gk_rect; in s7551::post classify rtPx vs that union rect
and log for kind Z the depth-value delta histogram (|d| small = requant). Also log the fb's previous registered width at that address.
Run 3 arms as s7552 (HOLD 90 is enough, ph=3-6 is the boot/menu route):
  env R=$PWD/scratch/s7553_gm HOLD=90 ARMS="4:l12:ROGUESQ_FORCE_SAVE_MISSION=12+$E 1:l1:ROGUESQ_FORCE_SAVE_MISSION=1+$E"
  zsh tools/g1e_owner_quiet_arms.zsh   (E="ROGUESQ_S7551_GK=1+ROGUESQ_S7551_GK_PLANT=1"; mkdir -p the R dir first; ONE launch only)
Score: python3 tools/s7552_gl_score.py <log> --from 0 (pre-mission). Outcomes: out-of-rect px inside the union draw rect -> H-unmerged-draw
(close, or fix the merge if RT64 uses drawColorRect for anything else); outside every draw -> H-stale-native, name the aliasing fb.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves. Never flip a default without the owner.
