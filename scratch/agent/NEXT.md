# NEXT work unit (s1162)

HYPOTHESIS-ID: slot-dispatcher-frame-idiom-audit

Perform one bounded M3 idiom-class audit of the recurring
`slotDispatcherIter+872` SIGBUS. Enumerate all generated direct/indirect
`slotDispatcherIter` callsites, join each to its companion symbol/function
boundary, and classify the caller's stack adjustment, saved-register use, and
return path. Use the existing static inventory plus one phase-gated runtime
marker table only if the census leaves multiple live classes; do not add a skip
or guard.

Competing hypotheses and discriminator:

- H1: all live callers share one balanced generated frame idiom; the SIGBUS is
  caused by a runtime-side frame/value writer outside this call class.
- H2: one generated caller class has a distinct stack/return contract that can
  explain the `+872` spill.
- H3: the `0x80078894` boundary family is coalesced or mis-split and is the
  unique unbalanced generated caller.

The discriminating measurement is a complete callsite classification table:
for every reachable caller, the generated prologue/epilogue contract and the
companion symbol boundary must agree. H1 is selected if every live class is
balanced; H2 if one distinct balanced/unbalanced idiom remains; H3 if the
`0x80078894` family alone has a boundary mismatch. A runtime null is invalid
unless its independent phase and slot-dispatch controls fire.

Commands:

    rg -n "slotDispatcherIter|0x80078894|jal.*800788" ../N64Recomp/RecompiledFuncs/funcs_*.c ../rogue_squadron64
    rg -n "slotDispatcherIter|80078894" syms tools docs ../rogue_squadron64

Expected outcomes: the census must produce one table covering all sites, with
no conclusion from a partial grep. Do not infer parser or renderer causality
from this frame-contract audit.
