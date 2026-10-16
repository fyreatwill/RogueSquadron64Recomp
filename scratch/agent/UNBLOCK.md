# UNBLOCK (s5032) — route 3 (re-scope), with route-1 partial refutation

Block as written (s5031): owner must (a) install a MIPS GCC or (b) declare the patch thread dead and name a new objective for "parked M4 accumulator and movz/movn threads".

Route 1 (refute):
- The question's premise (b) is stale: movz/movn is DONE (s4970, 0/179 do_break; CURRENT-TRUTH ~line 475) and M4 accumulator is CLOSED (s5005/s5006). Neither is a parked thread needing an objective.
- Apple clang `--print-targets` lists no MIPS target; no llc; only `mips-linux-gnu-as/ld` and `ld.lld` present. So the compiler dependency is real; an assembly-only substitute is explicitly forbidden by s5023 as a qualification of the normal path.

Route 2: obtaining a compiler = installing software from the internet -> human-only boundary. Not done.

Route 3 (taken): the toolchain gates qualification of ONE disabled patch (heap-guard override of allocateDisplayListBuffer, runtime override off) aimed at crash families (VI-640) that are not reproducible (0/9, s4974). Whether the patch is needed at all is answerable without a compiler: census how often the original allocator sees a non-KSEG0 pointer. New NEXT.md does that. Toolchain recorded as an open, non-gating dependency in CURRENT-TRUTH.

Refuting experiment for this conclusion: any soak line showing guard-condition hits (non-KSEG0 free-list pointer) would make the toolchain request load-bearing again.
