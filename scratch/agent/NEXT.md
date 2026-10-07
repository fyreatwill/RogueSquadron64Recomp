# Next work unit: audit the A9 voice-array-base guard idiom class

Session 4119 closed A10 at its measured scope. Execute exactly one complete
A9 census/capture next; do not alter the guards.

HYPOTHESIS-ID: m5-step8-voice-array-base-guard-class

Competing hypotheses and discriminator:

- H-A9-legitimate: every A9 guard protects an invalid voice-array base and no
  valid audio work is suppressed.
- H-A9-suppresses-valid: a guarded base has an independently attributed retail
  allocator writer and a valid phase-scoped port range, so the guard can
  explain lost voice work.
- H-A9-route-invalid: the paired capture misses a required control or target
  phase, so A9 nulls are unevaluable.

The single discriminating measurement is one complete A9 source census plus
one same-build retail/port phase-gated capture. The source census must include
all `funcs_24.c` A9 entry/loop sites, the `allocateSongChannelArray` writer at
`0x8008F0EC`, both A9 reader exceptions, and downstream voice/slot traversal.
The positive control must fire; retail must reach title and hangar; port must
reach both phases. A guarded pointer with independent retail writer evidence
and a valid port range selects H-A9-suppresses-valid; all guards invalid or
unfired with valid controls selects H-A9-legitimate; missing controls/phases
selects H-A9-route-invalid. Do not remove or bypass any guard.

Before building, enumerate every A9 site and writer with bounded `rg` searches
in the generated tree, fixup script, and oracle watch configuration. Ask the
retail oracle first with whole-RDRAM and target-range controls. Then build once
and run one qualified real-audio/LLE/ungated/solo/spin-yield port capture with
all A9 fields and phase-gated positive controls.

Required build:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Do not land a behavior change unless the measurement selects
H-A9-suppresses-valid and the changed guard has an `ORIGIN:` naming the
allocator writer and explaining why the value is legitimate.
