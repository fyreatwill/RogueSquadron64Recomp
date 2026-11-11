# NEXT: G3 title / SELECT GAME / level select / available craft at 16:9 vs angrylion (CURRENT-TRUTH item 35)
HYPOTHESIS-ID: g3-menus-169
State (s7154): OPTIONS/PASSCODES/MISSION FAILED/results are H-equal at 16:9 (fit 0.0000-0.0044, RT64 pillars pure black, RECT_ASPECT
inert). Title + SELECT GAME (s7152) and level select + available craft (s7144) were scored at 21:9 only. 16:9 is the owner's TV (fb 796
wide, crop 0,9,369,216, 4:3 band x 66..303).
Hypotheses: H-equal (fit <= ~0.005 per box, pillars black); H-strip (RT64 pillar strips / slide trail at 16:9 that angrylion lacks: scissor
clamp misses at this fb width); H-rect (RT64 rect scale fires on a 16:9 menu: text k != triangle/3D k by >1%, or the 1.333x pattern).
Commands (one game at a time; tools/s7146_arm.zsh, CW=384 CH=216 ASP=16:9):
 T (title + SELECT GAME): env RDIR=s7155 ASP=16:9 SECS=45 FROM=200 EVERY=3 DL=8 DU=32 CW=384 CH=216 zsh tools/s7146_arm.zsh T1 ""
   (default boot AP; s7152 M1 hit the 12 GB cap at swap 2406 from FROM=200: use EVERY=4 if disk is short; ~34 GB free at s7154)
 M (level select + craft): env RDIR=s7155 ASP=16:9 SECS=42 FROM=1300 EVERY=3 DL=23 DU=17 CW=384 CH=216 zsh tools/s7146_arm.zsh M1 ""
 plus ROGUESQ_RECT_ASPECT=0 arms of both (rule 13). Delete each .cap after post, before the next run.
Post: zsh tools/s7152_post.zsh scratch/s7155 <N> 0,9,369,216 46,322. Title/profile are memory-blended 512-band screens: score them on the
 <N>n (NOPREFILL) dir, because at 16:9 the <N>c combine kept magenta pre-fill for every swap (s7154). Level select/craft are 336-row fbs: use
 the <N>r (pre-fill) dir. Control: s7122_fidelity.py control on the dir you score. Join tools/s7148_pfsearch.py ... 20 <N>J.csv, split phases
 by swap (check a sheet first), fit tools/s7143_affine.py fit box 66:4:303:200 (AFF_SX 0..3 AFF_SY -4..2 AFF_E 1..0.984). Width term
 tools/s7154_kmd.py and 1.333x control tools/s7154_kgrid.py with env CROP=0,9,369,216 ALSUF=n|r BOXES=... (run from scratch/s7155).
 Pillars: presented columns 0-58 / 311-369 mean+max per phase (s7154 inline probe; positive control = band columns in the same frames).
Discriminating outcomes: fitted boxes at floor + text k == 3D/tri k + pillars 0 -> H-equal; RT64-only pillar pixels -> H-strip (find the
scissor/clear); text k off by >1% or 1.33x -> H-rect.
Owner save rule: no SAVE_FROM; NO_SAVE_WRITE stays. Keep CURRENT-TRUTH < 60000 B (59.0 KB now: the NEXT iteration after this one
will likely trip maintenance; prune closed items 27-34 into one line if you add text).
