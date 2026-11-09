# NEXT: G1c — qualify the off-map cull image with a frozen pose (s7031 census + cost selected H-offmap; image unqualified)
HYPOTHESIS-ID: g1c-offmap-cells
Context (s7031): ROGUESQ_DD_OFFMAPCULL=2 (cull off-map cells > 2 rings outside the map edge) removes 5919 (L1) / 4265 (L4) of ~7400 cells/f,
rsp -9.75 / -3.71 ms (-> 60 fps). Census: 82% / 62% of dd6 cells off-map, mostly 17+ rings out. The image check FAILED its control in both runs:
s7030_fogcull_image.py A/A floor 8.7 / 10.3 > k=0.3 control 6.1 / 3.5 (autopilot banking; adjacent seconds differ more than the arms).
G5i/owner items: nothing to run (CURRENT-TRUTH items 1-14); check first.
Hypotheses:
 H-invisible: off-map cells beyond R rings are never seen (behind the edge wall face / under the MELT sea slab) -> R=2 frames equal R=off at the
   same pose (|d| at the A/A floor), k=0.3 control visibly differs.
 H-plateau: seen from above the wall top (L1) or across the sea (L4), the off-map plateau / sea floor IS visible -> R=2 ends it 2 cells out
   (sky gap or hard edge); then R must grow (R=8, or a depth-gated R) or the cull stays opt-in.
 H-retail-edge: what R=off draws out there is itself the clamp artefact (endless edge plateau); the owner may prefer the cut. Owner's call.
Discriminator, ONE build (no code change expected beyond the harness): freeze the pose so every phase renders the same camera.
 ROGUESQ_POSE_FREEZE=<x1,x2,...>:<ms> (s6872, src/main/rt64_render_context.cpp:54, needs ROGUESQ_RAND_TRACE; recipe tools/g3_optin_pose_arms.sh).
 FIRST check the boring thing: does streamTerrainGridCellsByDistance keep running (cells/f > 0 in [s7030] lines) while the tick is frozen? If not,
 the freeze cannot carry a tog3 A/B: instead run 3 separate deterministic same-pose runs (no-input flight is deterministic) R=off / R=2 / k=0.3.
 Freeze windows >= 4 s each (spans all 3 phases at 1 s/phase), 4-6 poses per level incl. one at altitude looking over the L1 wall.
 Score per pose: per-phase mean |P_i - P_0| over frames inside the freeze, A/A = P0 frames of different cycles inside the same freeze (floor should be ~0).
Arms: L1 and L4, dd6 21:9 WIDEWIN cap 10240 MELT OWNER_TIMING, FOGCULL=tog3 K=0,0,0.3 + OFFMAPCULL=tog3 R=-1,2,-1 (copy scratch/s7031/run_A.zsh).
Outcome map: R=2 |d| near the A/A floor and k=0.3 well above it on every pose -> H-invisible: offer OFFMAPCULL=2 in docs/OWNER-OPT-INS.md
(default stays the owner's call). Any pose with R=2 visibly cutting terrain -> H-plateau: repeat with R=8 in the same freeze run.
