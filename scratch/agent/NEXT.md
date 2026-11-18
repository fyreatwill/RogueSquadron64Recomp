# NEXT (s7587)
HYPOTHESIS-ID: metal-cpp-ownership-audit

Class LK closed s7586 (two plume_metal.cpp ownership bugs found by leak measurement: s7585 autoreleased wait buffers on a pool-less
thread, s7586 unreleased +1 dispatch_data_t). Both are one idiom: metal-cpp has no ARC, so every object's +1/+0 status must be
matched by hand. Class OW = audit the whole idiom offline, then check the survivors at runtime.
Hypotheses: H-clean (no other mismatches), H-leak (more unreleased +1 objects: bounded or per-frame), H-overrelease (a +0
autoreleased object released by us: latent use-after-free that only fires once a pool drains; lead: MetalShader::functionName =
NS::String::string(...) (+0) then functionName->release() in ~MetalShader, and setName's debugName the same way).
Method, one pass:
1. Enumerate in lib/rt64/src/contrib/plume/plume_metal.cpp every acquisition: alloc()/new*()/copy*()/*_create (+1) vs
   class factories like NS::String::string, MTL::*Descriptor::*Descriptor(), commandBuffer*, currentDrawable (+0), and every
   release()/retain()/autorelease()/dispatch_release. A short python pass printing site, kind, the owning member/local and the
   matching release (tools/s7587_ownership_census.py), each row classified OK / LEAK / OVERRELEASE / NEEDS-POOL.
2. For each OVERRELEASE: does the thread drain a pool (s7585 added one in executeCommandLists)? If so, Zombies run:
   `NSZombieEnabled=YES` + MallocScribble on the L4 owner recipe 300 s and the hangar route; a zombie message = confirmed.
   Positive control: a deliberate extra release behind an env plant (ROGUESQ_S7587_PLANT=1) that must log a zombie.
3. Fix each confirmed row (retain() at acquisition or drop the release), export submodule-patches, rebuild, rerun leaks:
   dispatch_data_t / NSArray counts and zombie count 0 with the plant firing.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
