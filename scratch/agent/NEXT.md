# NEXT: replicate the s7115 NEARLIFT tog1 arm to >= 30 eye-cell losses (2 more runs), then owner sheet
HYPOTHESIS-ID: fps60-wall-probe
Context: s7115 selected H-probe (terrain inside the render near pyramid; retail ray test blind from inside). ROGUESQ_S7115_NEARLIFT=tog1
run d: control passes (on pierce 0.002 vs 0.150), losses off/on 10/4, episodes 8/1, shifted 5/9 and 9/5 -> not yet significant.
Do: two more runs, one at a time, same recipe with the name changed (e, f):
  sed 's/ 6 4 d / 6 4 e /; s/_d\./_e./g' scratch/s7115/cmd_d.txt > scratch/s7115/cmd_e.txt; zsh scratch/s7115/cmd_e.txt  (then f)
  consider DL/DU 120 300 (args 5/6 of arm.zsh) for more hug time.
Per run: python3 tools/s7107_losscan.py tris_X.bin X.csv > losscan_X.txt; tools/s7114_parity.py tris_X.bin losscan_X.txt push_X.txt 0.5 -0.5;
tools/s7115_neargap.py push_X.txt tris_X.bin losscan_X.txt (control: on-second flight pierce ~0).
Outcomes: pooled d+e+f off >> on with shifted controls near even -> H-probe fix confirmed: make owner sheet of presented frames
(g5b_capture raw, on vs off wall hugs), add NEARLIFT=1 to docs/OWNER-OPT-INS.md as opt-in, owner judges; also check it does not lift
the camera visibly in normal flight (nl lift p99, presented-frame camera height). Pooled even -> H-probe is not the lever; take the
H-frame class (losses whose joined tick does not pierce: check tick join +1/-1 and the render projection frame).
