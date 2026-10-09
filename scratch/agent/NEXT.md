# Next work unit (s4330): D740 transfer-boundary census

HYPOTHESIS-ID: m5-step9-mort-output

The s4329 matrix passed oracle whole-RDRAM/title/hangar, MORT reference, both
port VI controls, and both filter controls. The direct witness immediately
before the generated D740 filter call fired 256 times in each arm and its
`d740_store_n` reached 256, but every row had `caller_join=0`; the caller probe
had only the `0x8009C88C` bucket. Do not interpret this as descriptor equality.

Competing hypotheses:

- H-entry-bypassed: a transfer targets the D740 body/callsite without entering
  the generated function wrapper where the caller probe was inserted.
- H-probe-placement: the generated wrapper is entered, but the active body is
  reached through a label/overlay mapping whose instrumentation boundary is
  not the real guest entry.
- H-cross-thread-or-overwritten: a real D740 entry occurs, but its tuple is
  lost before the direct call through a worker or overwrite.

Discriminator: perform a bounded static transfer census before changing runtime
behavior. Enumerate every generated reference to the D740 body/callsite and
the `updateVoiceChannelParamsLarge` symbol, then inspect the complete enclosing
labels and overlay map around each reference. A reference that targets the
body/callsite without the wrapper selects H-entry-bypassed; a normal wrapper
entry whose label map skips the probe selects H-probe-placement; a real entry
plus a later overwrite requires one targeted witness at that transfer and
selects H-cross-thread-or-overwritten.

Commands:

`rg -n "8009D740|updateVoiceChannelParamsLarge|8009C5BC" ../N64Recomp/RecompiledFuncs ../N64Recomp/fixup_game_funcs.py`

`sed -n '1768,1810p;4768,4805p' ../N64Recomp/RecompiledFuncs/funcs_27.c`

Do not build or alter RSP, decoder, AI, or game-path behavior until the census
names the transfer boundary. If the census is insufficient, add only one
targeted transfer witness in the next unit.
