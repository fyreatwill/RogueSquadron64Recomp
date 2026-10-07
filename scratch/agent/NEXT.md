# Next work unit: ground the eight key-on early-return sites

HYPOTHESIS-ID: m5-keyon-early-return-idiom

Do one diagnostic-only, regeneration-safe audit of the complete eight-site
key-on early-return class before changing any return. The port selector-writer
boundary is now qualified; the next question is whether these returns suppress
legitimate key-on work.

Competing hypotheses:

- Hguard-legitimate: target-phase inputs fail the divisor/descriptor contract,
  so the early returns are valid fallbacks and the normal key-on tail is not
  expected.
- Hguard-port-only: retail reaches the normal key-on tail for the same class,
  but the port hits one or more guards with valid inputs; this authorizes a
  later single-class behavior change.
- Hguard-unwired: the port route reaches the sites, but the regenerated guard
  witness/control is absent or phase-gated incorrectly, so a null is
  unevaluable.

Discriminating measurement: one build and one retail-gated capture with all
eight PCs instrumented together. The retail oracle must pass its whole-RDRAM
positive control and both title/hangar phase gates. The port must reach both
target phases. For each PC, record guard entry, divisor/descriptor inputs,
normal-tail entry, and slot status `02`/`00`; emit a first target-phase control
from the shared helper. A retail normal-tail row paired with a port guard row
on valid inputs selects Hguard-port-only; matching invalid-input rows select
Hguard-legitimate; missing control despite both phases selects Hguard-unwired.

Do not remove or bypass any return in this unit. Any later mitigation needs an
ORIGIN naming the guest writer and stating why its value is legitimate.

Commands:

`python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Create/run one bounded retail-gated script from `build/`, using
`PROBE_PHASE_WIDTH`/`PROBE_KEYS_FROM_PHASE=1`, the whole-RDRAM oracle control,
and SIGKILL cleanup. Do not interpret any null unless both route controls and
the shared positive control are present.
