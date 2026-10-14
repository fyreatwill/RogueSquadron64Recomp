# Resume next work unit

HYPOTHESIS-ID: m3-branch-likely-delay-slots

WORK UNIT: perform one complete census of generated branch-likely delay-slot
idioms. Do not chase a single crash and do not add a guard before the whole
class is enumerated.

Competing hypotheses:

* H-blikely-valid: every branch-likely delay slot is represented correctly by
  the generated C control flow, and no runtime change is needed.
* H-blikely-unreachable: any suspicious branch-likely site is dead on the
  qualified title/hangar route, so it needs documentation only.
* H-blikely-unsafe: at least one reachable site has a missing/incorrect
  annulled delay-slot effect and requires a named fix or guard.
* H-blikely-route-gap: the static class cannot be qualified because the
  existing positive-control route does not execute the candidate sites; retain
  the census as single-source and do not infer a runtime defect.

DISCRIMINATING MEASUREMENT: enumerate all branch-likely instructions and their
delay-slot translations from the generated files, map each site to its guest
PC/function and reachable route evidence, and compare the generated control
flow against the MIPS annulled-delay-slot rule. Outcomes prove H-blikely-valid
if all sites are faithful; H-blikely-unreachable if all suspicious sites lack
route execution; H-blikely-unsafe if one reachable site demonstrably executes
the delay slot when the branch is not taken or omits it when taken; and
H-blikely-route-gap if no runtime join can be made. A positive control is the
existing title/hangar phase/SP/PCM route evidence, not merely a nonempty grep.

Exact commands:

    rg -n -i -C 4 'branch[- ]likely|beqzl|bnezl|bc1[tf]l|bltzl|bgezl|blezl|bgtzl' ../N64Recomp/RecompiledFuncs tools docs
    rg -n -C 3 'likely|annul|delay slot' tools docs/M3-* 2>/dev/null
    grep -n '^## Session ' PORTING-STATE.md | tail -15

Write the bounded census table to a new `docs/M3-S4837-BLIKELY-CENSUS.md` only
if the class is found and classified. If a real runtime defect is proven, land
the smallest durable fix through the appropriate fixup script; otherwise the
census itself is the work result. Append the session to PORTING-STATE.md and
update CURRENT-TRUTH before committing.
