# NEXT: name the NULL node in the dd>1 pool crash (carried over from s6551; s6552 was maintenance only)
HYPOTHESIS-ID: g1c-dd-phase2
Read docs/CURRENT-TRUTH.md first (compacted s6552; old body archived in docs/PROJECT-OVERVIEW.md "Migrated from CURRENT-TRUTH").
Known (s6551): ROGUESQ_DD_POOLX=2/3/4 all fault at the same `sw ...,{0,2,4}(a0)` with a0=0x80000000 in renderFlatMeshFaceGroup; px1 is clean. Not a cap threshold.
Hypotheses:
- H-uninit: the extra pool entries beyond the retail size are never initialised, so a next pointer of 0 is followed by the walker.
- H-fixedarr: a retail-sized parallel array or free list in guest RAM, indexed by cell count, is read past its end and yields 0.
- H-clamp: the ddclamp window x[0,32) z[17,32) feeds renderFlatMeshFaceGroup an entry the game never built.
Work unit: with ROGUESQ_DD_POOLX=2, log (in the existing ROGUESQ_DD_LOG path) the pool base/stride/count, and walk the list from the head (0x8011A7DC) on the frame before the crash. Print the index of the first node whose next==0 against the expected count. One build, one run: `zsh scratch/agent/s6549_run.sh 4 2`. Run it from build/ with the ROM present, SIGKILL on timeout.
Outcomes:
- first-NULL index == retail count (400) -> H-uninit: initialise/link the extra entries in the pool carve (fix in the DD hook, not a guard).
- index within the retail range -> H-clamp / H-fixedarr: find the writer of that node.
- Positive control: the same walk on px1 must report the full retail count with no NULL.
