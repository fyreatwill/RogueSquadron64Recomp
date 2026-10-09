# Next work unit (s4320): trace the missing MORT/filter callsites

HYPOTHESIS-ID: m5-step9-mort-boundary

State (s4319): the independent retail oracle and both port arms passed all
route/title/hangar controls. Descriptor-start fired in both arms, but no
`init-desc` payload event or real `filter-voice-audit` row fired. The final
probe was restricted to descriptor task `0x800377C8` after the initial run
crashed on non-descriptor task `0x80149470`. No game-path behavior changed.

Competing hypotheses:

- H-callsite: the existing generated hooks are attached to stale or wrong
  callsites, so the active MORT payload/filter path is elsewhere.
- H-route: the descriptor task reaches the host boundary but the selected
  route never executes the payload/filter idioms.
- H-data: the callsites execute, but their event predicates suppress rows
  because the descriptor/voice fields are not in the expected shape.

Discriminator: enumerate every generated callsite and branch predicate for
`init-desc` and `filterVoiceSampleBlock`, then add one bounded entry witness at
each candidate callsite plus a host-positive control for each witness in one
build/run. Keep both `ROGUESQ_AUDIO_UCODE=0` and `=1` arms, the oracle controls,
and phase gates at VI 1024 (`0x00790400`) and VI 512 (`0x006AB400`). A control
and candidate entry at a different generated site selects H-callsite; entries
absent with descriptor-start and route controls selects H-route; entries with
valid arguments but no event rows selects H-data. Do not modify decoder, AI,
or game behavior.

Exact preparation/checks before building:

`rg -n 'init-desc|rs64_m5_audio_event|filterVoiceSampleBlock|filter-voice-audit|rs64_filter_voice' /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs src tools --glob '*.{c,h,cpp,py}'`

Read the matching generated windows, update the existing matrix driver with
all candidate entry flags, build once, and run both arms into
`scratch/agent/s4320_m5_callsite_trace`. Require positive controls for every
new entry witness before interpreting any null.
