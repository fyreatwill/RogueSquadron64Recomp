# NEXT (s7588)
HYPOTHESIS-ID: apple-tu-ownership-audit

Class OW closed s7587 for plume_metal.cpp (census tools/s7587_ownership_census.py, gauge ROGUESQ_S7587_POOLGAUGE=1). Same idiom
may live in the other Apple TUs: lib/rt64/src/apple/rt64_apple.mm, lib/rt64/src/contrib/plume/plume_apple.mm,
lib/rt64/src/contrib/imgui/backends/imgui_impl_metal.mm (+ imgui_impl_osx.mm, any src/*.mm).
Hypotheses: H-arc (built with -fobjc-arc: ownership is compiler-managed, only pool placement matters), H-clean (manual RR but
balanced), H-mismatch (+0/+1 mismatches like s7587), H-pool (autoreleases on pool-less threads, e.g. per-frame window/layer
queries on the present thread).
Method, one pass:
1. `grep -n 'fobjc-arc' lib/rt64/CMakeLists.txt CMakeLists.txt` and the compile commands
   (build/compile_commands.json if present) for each TU -> ARC yes/no.
2. Non-ARC TUs: classify every alloc/new/copy (+1) vs factory (+0) and every release/retain/autorelease, by hand or by extending
   s7587_ownership_census.py with an ObjC-message regex ([X alloc], [x release], ...). ARC TUs: list calls on non-main threads
   with no @autoreleasepool.
3. Runtime: the gauge only samples in MetalCommandList::begin; add a sample site in the present path (threadPresent / swap chain
   present) if step 2 names a per-frame +0 there. Arms OWN=1 with and without any new fix, PLANT=1 in both, L4 dd4 150 s + the
   s7469 hangar route; growth per begin must equal the plant rate (0.0039).
Outcomes: H-arc/H-clean -> class OW-2 closed with the table; H-mismatch/H-pool -> fix (env-gated, =0 restores) + gauge proof.
OWNER SAVE RULE: never clear ROGUESQ_NO_SAVE_WRITE; never touch build/saves.
