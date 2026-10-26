# Next: fold the s6278 dd3 two-arm run, establish whether the finder patch ever fires
HYPOTHESIS-ID: cpatch-pipeline-qualification
1. Read scratch/agent/m6/g1_lvl1s6278_dd3_{norm,ctl}/{summary,run.log}: grep `[patch-live] findAndUnlink` and `[find-null]` (norm expects bad=0, ctl expects bad>0; NULL dumps name the pool state). alive_at_end matters, rc=0 is not a pass.
2. If no finder line in either arm: H-uncalled (callers fixup-inlined or exhaustion path never reaches it) vs H-notlive (patch shadowed). Discriminator: temporarily make the wrapper print on every call to the first 8 calls with ROGUESQ_FIND_CTL-independent unconditional log; or lldb breakpoint on _findAndUnlinkSmallestEntry during a dd3 boot. Control: sibling patch lines in same log.
3. Only then use [find-null] dumps to name the dd>=3 exhaustion writer.
