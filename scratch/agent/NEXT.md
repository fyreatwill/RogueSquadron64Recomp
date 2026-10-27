# NEXT: position-matched dd sheet for s6418 farclip fix + dd2 holds (G1c phase 2)
HYPOTHESIS-ID: g1c-dd-phase2
Hypotheses: H-fixworks (DEB4*dd^2 returns far terrain at matched poses), H-lod-coarse (far cells now drawn but too coarse: scale LOD table DE98..A0), H-ucode (cells in chain but clipped/dropped downstream).
Do: build a pose-matched sheet from scratch/agent/m6/g1_lvl1s6418_{d1b,d2,u3,u3nofc} (flight frames only, fbn >= ~1500; map fb_ n to a camera pose via the [poselock]/meshlog order or VI, pick the same pose in all arms) with tools/g1c_posesheet.py; view it. If far terrain visible at u3 not u3nofc => H-fixworks, then queue 300 s dd2 holds on lvls 1/5/10 with the fix. If chain bigger but picture unchanged => count terrain RDP tris per arm (H-ucode).
Control: u3nofc (ROGUESQ_DD_NOFARCLIP=1) is the same-run negative control.
