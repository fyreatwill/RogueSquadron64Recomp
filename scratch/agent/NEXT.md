# NEXT: measure DL-node supply at dd3 (G1c phase 2)
HYPOTHESIS-ID: g1c-phase2-drawdist
Facts (s6089): dd3 reaches findAndUnlinkSmallestEntry first time, call 59 returns 0 -> NULL node -> SIGBUS beginFrameDLChunk+12168, 5/5. dd1 never calls it. Bucket dump read nbuckets=0 (post-call, layout suspect).
Hypotheses: H-bucket supply exhausted (pool sized for retail) -> raise supply/second arena for DL nodes; H-reclaim reclaimDisplayListChunk 0x80007CDC not returning nodes at dd3; H-layout my table decode wrong.
Discriminator, ONE build: dump PRE-call (entry) table by disassembling funcs_6.c findAndUnlinkSmallestEntry (lhu 0x8012EEF0 count, base lw 0x8012F000, node +0 next/+8 cnt) and count reclaimDisplayListChunk calls/nodes returned per frame at dd1 vs dd3 in the same build (env toggle). Positive control: dd1 must show reclaim counts >0.
Soak recipes: scratch/agent/soak_queue/running_manual/s6088_bucket_dd{1,3}.sh; run with perl -e 'alarm 700; exec @ARGV' (no `timeout` on this Mac) or enqueue in soak_queue/.
