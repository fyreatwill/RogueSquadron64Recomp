# Next work unit: sample guest route identity at family entry

HYPOTHESIS-ID: m5-family-route-object-join

The s3780 image-only capture was qualified: the retail whole-RDRAM control,
six family-store controls, title VI, and hangar VI all passed. S/I/L entry
hooks produced 257 target-phase rows (S=128, I=1, L=128), all with
`target_arg=0`; stores remained outside the clear object. The host audio-route
snapshot was inactive on every row, so alternate-object legitimacy versus
wrong-route state remains open.

Competing hypotheses and discriminator:

- H1: the alternate object is legitimate; direct guest route/overlay state will
  be active and match the family edge.
- H2: the family calls are on the wrong route/overlay state; direct guest state
  will be mismatched or inactive while the alternate object remains stable.
- H3 is refuted by s3780: no family entry argument was target-relevant.

The discriminating measurement is one same-build image/oracle capture with the
existing positive controls and a new direct guest route/overlay-state sample at
each S/I/L entry, joined by phase/ordinal to clear object, entry arguments,
route key, destination addresses, and both target VIs. Active matching state
selects H1; mismatched or inactive state selects H2. Missing controls or target
phases are unevaluable.

Exact commands:

    rg -n "rs64_m5_family_entry|rs64_m5_family_store|route_state|clear_obj" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs tools src/main
    sed -n '478,610p' src/main/main.cpp
    sed -n '4870,4990p' /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3780_m5_guest_route_join.sh

Use the existing macOS image/oracle recipe as the base, with paths corrected to
`build/`. Do not suppress or replace the clear, inject values, or change an
audio gate.
