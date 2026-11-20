# NEXT (s7725)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report.
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7724 closed the scorer-coverage thread for good (CURRENT-TRUTH item 32): of the 9 deferred-retainable scorers, 7 are now sweep
gates over retained captures (s7433/s7435/s7436/s7437/s7438 on scratch/s7435, s7467 on scratch/s7467r, s7624 on scratch/s7624 L1),
each with a planted RED mutant in tools/s7723_retained_controls.py (18/18 PASS). s7367/s7369/s7434 = H-no-control (no control in the
tool), s7589 = H-no-control (its own control FAILs on both retained captures; the ledger verdict came from hand plateau steps),
s7247 = H-gone (raw fb dumps deleted). Do NOT take more scorer/gate work.

Ladder: every engineering rung is closed or awaiting the owner's look (CURRENT-TRUTH Next steps 2-9, 20, 22). With no new crash
report and no owner report, take the M6 secondary from the strategic priority (item 3b), which has a real discriminator:
- Unit: the rare RT64 Present SIGTRAP family (FOLDED 2026-11-18-014353: objc_autoreleasePoolPush inside
  plume::MetalDescriptorSetLayout ctor on thread "RT64 Present"). Hypotheses: H-nopool (the Present thread creates Metal objects
  with no enclosing @autoreleasepool, so autoreleaseNoPage traps when OBJC_DEBUG_MISSING_POOLS / a debug env is set or the pool
  page is exhausted), H-race (descriptor-set layout created concurrently from two threads), H-teardown (trap at exit while the
  runtime is unwinding). Discriminator, offline first: read the .ips (all thread stacks + exit context) and grep lib/rt64 for
  where the Present thread is spawned and whether its loop body is wrapped in an autorelease pool (NS::AutoreleasePool /
  @autoreleasepool). Outcome: no pool on that thread's loop -> H-nopool selected, fix = wrap the loop in a pool (lib/rt64 edit
  -> ./submodule-patches/export.sh + commit); pool present -> check the .ips for a second thread inside the same ctor (H-race)
  or exit frames on thread 0 (H-teardown).
Owner defaults: never flip.
