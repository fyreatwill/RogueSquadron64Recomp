# NEXT: name the NULL node in the dd>1 pool crash (s6551 follow-up)
HYPOTHESIS-ID: g1c-dd-phase2
Known (s6551): px2/3/4 all fault at the same `sw ...,{0,2,4}(a0)` with a0=0x80000000; px1 clean. Not a cap threshold.
Hypotheses: H-uninit (extra pool entries beyond retail size are never initialised: next ptr 0 followed by the walker), H-fixedarr (a retail-sized parallel array/free-list in guest RAM indexed by the cell count is read past its end and yields 0), H-clamp (ddclamp window x[0,32) z[17,32) feeds renderFlatMeshFaceGroup an entry the game never built).
Work unit: with ROGUESQ_DD_POOLX=2, log in the existing ROGUESQ_DD_LOG path the pool base/stride/count and walk the list from head [0x80115 8-0x5824 -> 0x8011A7DC] at the frame before the crash, printing index of the first node whose next==0 vs the expected count. One build, one run (`zsh scratch/agent/s6549_run.sh 4 2`).
Outcomes: first-NULL index == retail count (400) -> H-uninit: initialise/link the extra entries in the pool carve (fix in the DD hook, not a guard). Index within retail range -> H-clamp/H-fixedarr: find the writer.
