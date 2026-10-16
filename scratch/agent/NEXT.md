# Next work unit: heap-guard need census (no MIPS GCC required)
HYPOTHESIS-ID: heap-guard-need-census
Question: does the ORIGINAL allocateDisplayListBuffer (0x80007D74..0x80007E58) ever dequeue/insert a non-KSEG0 pointer (the condition patches/heap_guards.c guards) in title/hangar/mission soaks?
Method: add an env-gated counter via tools/fixup_*.py (not a hand-edit of generated code) logging free-list head/next values outside 0x80000000..0x807FFFFF; positive control = one run with a synthetic forced bad value (must log). One game at a time via the soak queue (nohup, not the 600 s cap); >=5 runs per scene, phase-gate on VI transitions.
Outcomes: 0 hits with control passing -> close the patch-pipeline thread (patch moot) and withdraw the toolchain dependency. Any hit -> toolchain request becomes load-bearing; escalate with the hit as evidence.
