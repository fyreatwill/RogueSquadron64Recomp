# NEXT: why does rs_malloc(size=24, flags=0x4) return NULL at vi=1024 just before the crash?
HYPOTHESIS-ID: m5-audio-destub
H-A: heap genuinely exhausted (blocks retail frees stay live in the port). H-B: flags=0x4 is a constrained request (aligned/from-top/pool) failing on fragmentation despite ample total free. H-C: free list corrupted so the walk ends early.
Discriminator (one run, both arms): at the NULL return log sum of free blocks, largest free block, heap end, and walk the header chain verifying sizes chain to heap end; read the flags semantics in the guest allocator (0x80001C00..0x80002300). Control: s4457-control; recipe scratch/agent/s4559_node_watch.sh. Then oracle-check retail free total at the same stage.
