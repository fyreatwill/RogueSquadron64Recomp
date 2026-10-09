# Next work unit (s4327): classify descriptor/source divergence in the M5 join

HYPOTHESIS-ID: m5-step9-mort-output

State (s4326): the clean seeded matrix passed oracle_gate=1, oracle whole-RDRAM,
VI-1024 and VI-512 route controls, the MORT reference, and both port VI
controls. Each port arm emitted 128 filter calls at 0x8009D740 before the
shared crash. The 17 common route-row keys all differed in source/output hash;
rate stayed 22047 Hz, while route ordinals differed and a0/a1 differed on
15/17 and 12/17 rows. H-output-join is rejected. Descriptor type/class is not
recorded, so the selection boundary is unresolved.

Competing hypotheses:

- H-same-descriptor-different-filter: descriptor identity/type matches, but
  source bytes differ before the filter; this is unlikely unless source_hash
  is not the descriptor payload.
- H-descriptor-class-divergence: descriptor type/class or identity differs
  before the filter, explaining the source and argument sequence.
- H-pre-filter-route-divergence: descriptor metadata matches, but an earlier
  producer/route selection changes the source span before the filter call.

Discriminator: extend the existing phase-scoped table in one batch with
descriptor identity/type/class and the descriptor-to-source pointer, while
retaining route ordinal/row, rate, a0/a1, table value, source/output spans and
hashes, plus PCM source/consumer joins. Matching descriptor metadata with
divergent source selects H-pre-filter-route-divergence; divergent descriptor
metadata selects H-descriptor-class-divergence; matching metadata and source
but a filter-only change supports H-same-descriptor-different-filter. A
missing row is invalid unless the oracle positive control, oracle VI-1024 and
VI-512, MORT verdict, both port VI controls, and both filter controls fire.

Before building, inspect the descriptor producer and existing join fields:

`rg -n -C 5 'rs64_m5_descriptor_start|descriptor_type|route_snapshot|m5-filter-join' src/main/main.cpp src/main`

Add the complete descriptor-to-filter fields in one batch, then build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the same clean seeded matrix:

`pgrep -fl RogueSquadron64Recomp || true; zsh scratch/agent/run_s4321_m5_mort_output.sh`

Keep the same oracle/MORT/VI/filter controls. Do not alter RSP dispatch,
decoder, AI bridge, or add a game-path guard.
