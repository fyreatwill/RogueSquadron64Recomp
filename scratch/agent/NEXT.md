# Next work unit (s4323): explain the real-image filter-path divergence

HYPOTHESIS-ID: m5-step9-mort-output

State (s4322): the independent MORT reference passed four nonzero rows spanning
8000 and 16000 Hz. The oracle controls and both port arms reached hangar VI 512
at `0x006AB400` with no crash/abort. Silent audio (`ROGUESQ_AUDIO_UCODE=0`)
produced 256 filter rows at `0x8009D740`; real-image audio (`=1`) produced zero
filter rows despite 1,095 descriptor entries and PCM source/consumer rows. This
is a route-valid arm divergence, not a MORT null.

Competing hypotheses:

- H-real-eligibility: real-image descriptors fail an eligibility/status gate
  before the enumerated filter callsites.
- H-real-dispatch: real-image audio takes an alternate filter/decoder dispatch
  path not covered by the three enumerated callsites.
- H-silent-fallback: the silent arm's rows are a synthetic/host fallback and do
  not represent the real MORT path.

Discriminator: first audit the exact branch/callsite chain around the three
enumerated sites, then run one batched silent/real matrix with one branch-level
eligibility witness and the existing MORT reference, oracle whole-RDRAM, VI
title/hangar, filter, and PCM controls. A real-arm eligibility failure selects
H-real-eligibility; a real-arm branch to a named alternate selects
H-real-dispatch; identical eligibility with rows only in silent selects
H-silent-fallback. A run without both VI 512 markers is invalid.

Before any build, inspect the relevant source and preserve the positive controls:

`rg -n '8009C540|8009C88C|8009D740|filter-voice-audit|init-desc|ROGUESQ_AUDIO_UCODE' src/main RecompiledFuncs scratch/agent/run_s4321_m5_mort_output.sh`

Then add only the branch-level witness needed by that audit, build once with:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

and run the same matrix recipe:

`zsh scratch/agent/run_s4321_m5_mort_output.sh`

Keep `M4_Y8000_WIDTH=512`, reference selection `--indices 0,1,59,90`, and all
existing controls. No decoder, AI bridge, RSP dispatch, or game-path guard
change is authorized.
