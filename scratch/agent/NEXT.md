# Next work unit: wire a positive-controlled port selector-writer witness

HYPOTHESIS-ID: m5-port-descriptor-selector-writer

The declared-real route is now qualified through title and hangar, but the
existing port selector witness did not emit its own control marker. Its zero
rows therefore cannot distinguish a missing writer from an unwired witness.

Competing hypotheses:

- Hport-writer-live: exact port stores at `0x80090AAC` or `0x80090BA4` run in
  the target phases and carry selector/source values comparable to retail.
- Hport-writer-gap: the exact witness control fires on the qualified route, but
  neither candidate store runs in title or hangar.
- Hwitness-unwired: the route reaches both phases, but the candidate hook or
  its positive-control path is absent from the regenerated host code.

Discriminating measurement: add a regeneration-safe `fixup_game_funcs.py`
block for `funcs_24.c` that declares and calls one host witness immediately
before each existing `sh $v0, 0x22($s1)` at PCs `0x80090AAC` and
`0x80090BA4`. The host witness must emit one control line on the first target
phase, then phase-gated rows with PC, address, selector value, source word,
and VI origin/width. Build the ordinary Debug target and run one
retail-gated declared-real capture using
`scratch/agent/run_s4099_m5_port_selector_writers.sh` with the new env var.

Expected outcomes: control plus matching port rows selects Hport-writer-live;
control plus zero candidate rows selects Hport-writer-gap; missing control
despite both target phases selects Hwitness-unwired and requires fixing the
regeneration anchor before another null interpretation. Retail's whole-RDRAM
control and both target phases remain mandatory. No guest behavior changes.

Commands:

`python3 /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py`

`cmake --build build --config Debug --target RogueSquadron64Recomp`

`zsh scratch/agent/run_s4099_m5_port_selector_writers.sh`
