# NEXT (s7726)
HYPOTHESIS-ID: owner-looks-or-new-report

First: `python3 tools/crash_reports.py --since 2026-11-13` (a NEW report outranks everything), then any owner report, then fold
the s7725_texdesc_L4 soak line from SOAK-RESULTS.md (pass = alive, 0 fatal, vi_stalls30s=0; a fail = the s7725 plume fix broke
something: rerun with ROGUESQ_MTL_OWN=0 in the same session as the control).
If you edit tools/agent/, `sh tools/agent/run_tests.sh` must stay green.

s7725 closed the RT64 Present SIGTRAP: plume MetalBufferFormattedView over-released a +0 textureBufferDescriptor (fixed under
ROGUESQ_MTL_OWN; NSZombie boot 103 -> 0, same-binary MTL_OWN=0 control 103). The widened census (tools/s7587_ownership_census.py)
reports NEW {OK 82, NEEDS-POOL 4}.

Optional next unit (bounded, offline-first), if nothing above applies: the NSZombie boot recipe is a cheap whole-process
over-release detector that s7587 never had. Extend it past boot: one 150 s L4 owner-recipe arm with NSZombieEnabled=YES +
OBJC_DEBUG_MISSING_POOLS=YES (one game; zombies make the reporter print instead of trap), count `_NSZombie_` classes in flight.
Hypotheses: H-clean (0 zombies after the s7725 fix) vs H-more (another +0 factory released somewhere in a flight-only path, e.g.
rt64_apple.mm / plume_apple.mm or RT64 itself). Positive control in the same session: an ROGUESQ_MTL_OWN=0 arm must show the
103 TextureDescriptor zombies. A nonzero default-arm class names the next writer; grep for its factory and fix it the same way.
Owner defaults: never flip.
