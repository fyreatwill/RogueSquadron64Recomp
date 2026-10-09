# Next work unit (s4321): qualify MORT output for the witnessed descriptor class

HYPOTHESIS-ID: m5-step9-mort-output

State (s4320): the independent retail oracle and both port arms passed all
route/title/hangar controls. `init-desc` fired in both arms; the real image
reached `filterVoiceSampleBlock` through generated callsite `0x8009D740` with
128 call/entry rows. Static enumeration also found quiet callsites
`0x8009C540` and `0x8009C88C`. No game-path behavior changed.

Competing hypotheses:

- H-MORT: the witnessed descriptor class is consumed by the CPU MORT path and
  its decoded output reaches the voice/PCM joins.
- H-layout: descriptor fields or type/rate interpretation differ from the
  `tools/mort_probe.py` reference, so filter rows exist but output is invalid.
- H-AI: MORT/filter output is valid and nonzero, but the remaining mismatch is
  at the AI/host consumer boundary.

Discriminator: use the witnessed `init-desc` descriptor words and
`filter-voice-audit` source/output rows to run `tools/mort_probe.py` on the
same descriptor class, then join decoded nonzero bytes to the existing PCM
source/consumer rows in one phase-gated two-arm capture. Matching descriptor
type/rate and nonzero ordered PCM selects H-MORT; a mismatch with valid filter
entries selects H-layout; matching nonzero CPU output with a missing host join
selects H-AI. Keep the oracle whole-RDRAM/title/hangar controls and both audio
arms. No decoder, AI, or game-path guard change is authorized.

Exact preparation/checks before building:

`rg -n 'init-desc|filterVoiceSampleBlock|filter-voice-audit|mort_probe|PCM' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src tools docs/M5-AUDIO-PLAN.md --glob '*.{c,h,cpp,py,md}'`

Read the matching generated windows and `tools/mort_probe.py` contract, update
the existing matrix driver with the descriptor-class and PCM joins, build once,
and run both arms into `scratch/agent/s4321_m5_mort_output`. Require the oracle
and port route positive controls before interpreting any null.
