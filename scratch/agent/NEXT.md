# NEXT work unit (s1168)

HYPOTHESIS-ID: musyx-synth-call-idiom

Perform one complete static idiom-class audit of every generated callsite of
`musyxSynthFrame` (and any generated wrapper it directly calls) to determine
whether the pre-1024 `0x8000B650` failures share a malformed caller contract.
Do not add a guard, skip, restore, or runtime counter.

Competing hypotheses and discriminator:

- H1: at least one reachable generated caller has an unbalanced stack/return
  contract or a wrong direct-call boundary; that site is a concrete next probe.
- H2: all generated callers have balanced contracts and agree with companion
  symbol boundaries; the fault is outside this generated call idiom.
- H3: no generated callsite exists in the active tree, so the `musyxSynthFrame`
  frame is reached through a runtime-side or indirect path and this class is
  the wrong audit target.

The discriminating measurement is the complete callsite table: every textual
and generated `musyxSynthFrame` edge, companion entry address, stack delta/
restore pair, saved-return idiom, and direct-versus-indirect dispatch form.
One malformed reachable site selects H1; a complete balanced table selects
H2; an empty generated inventory selects H3. A partial grep is not a result.

Exact commands:

    rg -n "musyxSynthFrame|8000B650" RecompiledFuncs src lib docs tools
    rg -n "musyxSynthFrame" ../N64Recomp/RecompiledFuncs 2>/dev/null
    sed -n 'START,ENDp' RecompiledFuncs/funcs_*.c

Record the full site inventory and companion-symbol comparison in the session
entry and use it to choose the next phase-gated runtime unit. No build is
needed unless the census finds a source-boundary correction.
