# Next work unit (s4329): direct D740 caller witness

HYPOTHESIS-ID: m5-step9-mort-output

The s4328 matrix passed oracle whole-RDRAM/title/hangar, MORT reference, both
port VI controls, and both filter controls. Both arms emitted 256 filter rows,
but the retained `rs64_filter_voice_caller_probe` tuple joined zero rows; its
visible caller rows were only the `0x8009C88C` bucket. Do not interpret this as
descriptor equality.

Competing hypotheses:

- H-entry-bypassed: the generated D740 function-entry probe is not executed on
  the path that reaches the active filter callsite.
- H-cross-thread-or-overwritten: the entry probe runs, but its tuple is not
  visible at the filter call because execution crosses workers or another
  caller overwrites it.
- H-wrong-saved-source: the entry probe runs and the join is visible, but the
  original descriptor/source arguments were not retained from the actual
  D740 caller frame.

Discriminator: add one direct witness immediately before the generated
`filterVoiceSampleBlock` call at `0x8009D740`, carrying the original function
arguments from verified saved-register locations (`a0/a1/a2/a3`), and emit a
phase-scoped D740 store counter. One positive D740 store with a joinable tuple
selects H-wrong-saved-source or H-cross-thread-or-overwritten; zero stores with
the callsite active selects H-entry-bypassed; a matching tuple with divergent
source selects pre-filter route divergence, while differing descriptor fields
select descriptor-class divergence.

Before building, inspect the complete D740 prologue and saved-register flow:

`sed -n '1775,1865p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`
`sed -n '4740,4800p' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_27.c`

Patch the existing generated diagnostic through its fixup-compatible source,
build once, and run the same matrix:

`cmake --build build --config Debug --target RogueSquadron64Recomp`
`zsh scratch/agent/run_s4321_m5_mort_output.sh`

Keep all oracle/MORT/VI/filter controls. Do not change RSP dispatch, decoder,
AI bridge, or add a game-path guard.
