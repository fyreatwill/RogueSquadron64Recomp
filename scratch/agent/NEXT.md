# NEXT: G3 OPTIONS / PASSCODES / MISSION FAILED / results screens at 16:9 vs angrylion (CURRENT-TRUTH item 34)
HYPOTHESIS-ID: g3-2d-screens-169
State (s7153): these four screens are H-equal at 21:9 (fit 0.0000-0.0050), RECT_ASPECT inert. 16:9 is the owner's TV and has a
different fb width (796/652 class): s6924 saw hatched pillar strips on OPTIONS at 16:9 (scissor lrx 649, fixed s6926 by
ROGUESQ_G1D_SCISSOR_TOL=8), never scored against angrylion. The debrief draws only cols 256..768 under a full scissor at 21:9:
check what the 16:9 fb does (does the medal fit, are pillars black in RT64).
Hypotheses: H-equal (fit <= ~0.005, pillars black); H-strip (pillar strips / slide trail in RT64 at 16:9 that angrylion lacks, i.e.
our scissor clamp misses again); H-rect (16:9 fb ratio makes RT64's rect scale fire on the debrief full scissor: text 1.33x or
width term on text but not on the medal triangles).
Commands (one game at a time; 16:9 window 1360x796, capture size + rect from tools/s7125_arm.zsh, rect 0,9,369,216, split 46,322):
 O: env RDIR=s7154 ASP=16:9 SECS=45 FROM=1000 EVERY=3 DL=8 DU=32 CW=384 CH=216 AP=10:start,17:down,19:a,25:down,27:down,29:a,35:b,38:b zsh tools/s7146_arm.zsh O1 ""
 D: env RDIR=s7154 ASP=16:9 SECS=125 FROM=5400 EVERY=4 DL=86 DU=38 CW=384 CH=216 AP=6:start,11:start,16:start,21:start,25:left,27:start,33:start,40:right,46:left,52:right,58:left,64:a,70:start,76:start,82:start,88:start,92:down,96:a,100:left,103:a,110:a,116:a zsh tools/s7146_arm.zsh D1 ""
 plus the RECT_ASPECT=0 arm of D (rule 13). Post: tools/s7152_post.zsh; control on the *c dir; phases by tools/s7153_phsheet.py (env D=dir);
 join pfsearch -> affine (fit box = 4:3 centre band of the 16:9 crop), width sweep tools/s7153_kmd.py (tri ring vs text) and
 tools/s7153_kgrid.py 1.333 synthetic control. Pillar check: side frac + view RT64 pillars.
Discriminating outcomes: fit floor + k text == k tri -> H-equal; RT64-only pillar strips -> H-strip (find the scissor/clear);
text k != tri k by >1% or 1.33x -> H-rect.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Delete .cap after scoring. Keep CURRENT-TRUTH < 60000 B (58.6 KB).
Note: tools/s7153_{phsheet,kmd,kgrid}.py hardcode the 21:9 crop (R=0,11,469,216) and box coords: set R/W,H and boxes for the 16:9 crop (0,9,369,216) first.
