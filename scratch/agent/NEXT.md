# NEXT (s7437)
HYPOTHESIS-ID: rt64-tmem-hash

Class CT (CURRENT-TRUTH Next steps item 1): RT64 TMEM hashing cost. s7434 split the Gfx thread at 8.97 ms/frame; the largest
RT64 term is TMEMHasher::hash + XXH3 0.57 ms/frame (owner recipe FPS60 dd4 16:9, lvl1 flight).
Step 1 (offline, no build): extend tools/s7436_alloc_cost.py's parse() into tools/s7437_tmem_hash.py over scratch/s7435 and
scratch/s7433: hash self+inclusive share per thread and the owned caller chain (which RT64 path asks for the hash: texture
cache lookup per tile load vs per draw call). Reuse the ctrl column as the in-capture control (expect +0.0345 again).
Step 2 (one build, one run, only if step 1 shows >= 0.3 ms/frame): counter in lib/rt64 TMEMHasher (calls/frame, bytes/frame,
distinct (address,size,tlut) keys/frame, repeat-hash fraction), dumped at exit; planted control ROGUESQ_S7437_REHASH=1 hashes
every call twice (calls/frame must double). lib/ edit -> submodule-patches/export.sh + commit in the same session.
Hypotheses: H-needed (repeat fraction < 20%: each hash is new data, close), H-redundant (>= 50% of hashes repeat a key whose
TMEM bytes did not change this frame -> cache by load generation behind ROGUESQ_TMEM_HASH_CACHE, same-run toggle, compare
ms/frame + framebuffer hash identity), H-small (total < 0.3 ms/frame on both captures, close without a build).
