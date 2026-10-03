# Next work unit: join family arguments to clear object and route

HYPOTHESIS-ID: m5-family-route-object-join

The s3779 image-only capture was qualified: the retail whole-RDRAM control,
six family-store controls, title VI, and hangar VI all passed. The installed
S/I/L entry hooks produced 257 target-phase rows (S=128, I=1, L=128), but no
row had a target-buffer argument; family stores remained on alternate
objects. The missing-hook explanation is refuted, while alternate-object
legitimacy and route identity remain open.

Competing hypotheses and discriminator:

- H1: the clear object and family route object are legitimately different
  assets; the same-run join will show stable alternate-object identity and a
  legitimate route key.
- H2: the family calls are on the wrong route/overlay state; the join will
  show a route-key mismatch or inactive route at the family edge.
- H3: the family entry arguments are transformed before the stores; the join
  will show target-relevant source arguments but alternate destinations.

The discriminating measurement is one same-build image/oracle capture with
the repaired clear-object row, six family-store controls, family-entry rows,
route ordinal/key, active route state, destination addresses, and both target
VIs. Stable alternate object plus active matching route selects H1; a route
mismatch selects H2; target-relevant entry arguments followed by alternate
stores selects H3. Missing controls or target phases are unevaluable.

Exact commands:

    rg -n "rs64_m5_family_entry|rs64_m5_family_store|clear_obj|route" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs tools src/main
    sed -n '4870,4930p' /Users/williambuckley/Documents/Tools/N64Recomp/fixup_game_funcs.py
    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/run_s3773_m5_image_only.sh

The existing macOS recipe may require its executable/ROM paths to be changed
from `build/Debug` to `build/`, as in s3779. Do not suppress or replace the
clear, inject values, or change an audio gate.
