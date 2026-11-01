# NEXT: G3 -- mission 4 flight vs retail with dt pinned (state + framebuffer)
HYPOTHESIS-ID: g3-lvl4-pinned

s6753: with runInMissionFrame dt pinned to 1/30 s (oracle RS64_XTRACE_POKE / port ROGUESQ_XTRACE_POKE
800FA730:29:30:3d088889) the lvl3 sim is identical for 283 frames (NPC gates, rand stream). Missions 1-3 are H-match
(s6744-s6753). Extend G3 coverage to mission 4 using the pinned method, which now gives a frame-exact state witness.
Hypotheses:
- H-match: pinned arms identical in rand stream + NPC gates; framebuffers H-match (g3_oracle_match.py d << median).
- H-sim: a pinned state divergence at tick k -> name the field/caller (g3_frame_snap.py, g3_rand_align.py).
- H-render: state identical but frames differ (biome-specific texture/combiner) -> crop + name the material.
Work:
1. python3 tools/g3_eep_patch.py scratch/s6750/lvl3.eep scratch/s6754/lvl4.eep --set 0x31=3 (check lvl3.eep's +0x31 = 2
   first; use mission index+1 accordingly).
2. Retail: EEP=scratch/s6754/lvl4.eep RD=... zsh scratch/s6753/retail.sh (copy to scratch/s6754, add FB dumps per the
   s6748 recipe if window frames are wanted; check the 640->512 poke vi in oracle.log).
3. Port: copy scratch/s6753/port.sh, SAVE_FROM=lvl4.eep, ARM below the 512 switch time (s6753: flight at 60-67 s),
   CAP0 at flight for window captures.
4. g3_frame_snap.py + g3_rand_align.py (state), g3_oracle_match.py (frames).
Positive control: pin= fields present in both arms' tick rows; unpinned contrast = s6752.
