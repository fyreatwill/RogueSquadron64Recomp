# NEXT: does the F5 ucode drop whole near-crossing eye-cell triangles? (s7111: camera-side levers refuted)
HYPOTHESIS-ID: fps60-wall-reject
Context: s7111 showed the eye cell is lost even when all 4 push-out corner rays are clear (no terrain within 60 render units) and a
margin re-push (CAMFIX=tog1 PUSHK=1.5, residual 0.000) leaves eye-cell near-z losses at 29/22 (ctl 23/28). Render eye == pushed eye.
Hypotheses:
 H-reject   the LLE F5 ucode rejects a TRI_GEN triangle outright when a vertex is past the near plane (beside/behind the eye) instead of
            clipping it, so a large wall tri whose visible part is far beyond near vanishes -> retail hardware behaviour; fix would be a
            host-side or ucode-side near clip (opt-in) or keeping eye-cell vertices out of the near distance.
 H-raymiss  the eye cell's wall really is within near in view, and sampleTerrainAtNpcPosition does not see it (other geometry / LOD /
            ridge between rays) -> fix in the probe (extra rays vs the rendered cell triangles).
Unit: ONE instrument in the ucode census (src/rsp/s7106_rsptri.cpp, ROGUESQ_S7106_RSPTRI): for each TRI_GEN of the eye cell (s7107 keys),
dump the DMEM transformed vertices (x,y,z,w + clip flags) the triangle stage reads, and the RDP tris emitted per source triangle.
Read the F5 TRI_GEN vertex/clip layout first (docs/F5-UCODE-REFERENCE.md, reference/gliden64/F5Rogue.cpp TriGen*), then the recompiled
ucode for where it tests clip flags. Run scratch/s7111/arm.zsh 6 4 b with the s7111 env minus CAMFIX/PUSHK.
Outcome: on losscan eye-cell losses, a source tri with >=1 vertex w<near and >=1 in-view vertex beyond near that emits 0 RDP tris ->
H-reject; every lost tri has its in-view part within near (clipped polygon emitted) -> H-raymiss.
Positive control: ordinary far tris must show 1:1 source -> RDP tris; a tri fully in view must never be dropped.
