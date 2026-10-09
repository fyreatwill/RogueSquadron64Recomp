# Next work unit (s4328): carry the CPU caller object into the M5 descriptor join

HYPOTHESIS-ID: m5-step9-mort-output

State (s4327): two seeded matrix runs passed oracle_gate=1, oracle whole-RDRAM,
VI-1024 and VI-512 route controls, the MORT reference, and both port VI
controls. Each port arm emitted 256 filter rows at 0x8009D740 before the shared
crash. The RSP task and sp+0x114 descriptor candidates were invalid witnesses,
not null descriptor results. The CPU caller probe already sees the original
caller a0/a1/a2/a3; that object must be joined to the filter rows.

Competing hypotheses:

- H-same-descriptor-different-filter: CPU caller-object descriptor metadata
  matches, but source bytes differ before the filter.
- H-descriptor-class-divergence: CPU caller-object descriptor type/class or
  identity differs before the filter.
- H-pre-filter-route-divergence: caller-object metadata matches, but an earlier
  producer/route selection changes the source span.

Discriminator: make rs64_filter_voice_caller_probe retain the original CPU
caller object for the current thread, then extend the existing phase-scoped
table in one batch with caller object, its descriptor candidate/type/class,
and descriptor-to-source pointer. Retain route ordinal/row, rate, a0/a1, table
value, source/output spans and hashes, plus PCM joins. Matching caller metadata
with divergent source selects H-pre-filter-route-divergence; divergent metadata
selects H-descriptor-class-divergence; matching metadata and source but a
filter-only change supports H-same-descriptor-different-filter.

Before building, inspect the descriptor producer and existing join fields:

`rg -n -C 5 'rs64_filter_voice_caller_probe|rs64_filter_voice_audit_row|m5-filter-join' src/main/main.cpp src/main`

Add the complete descriptor-to-filter fields in one batch, then build once:

`cmake --build build --config Debug --target RogueSquadron64Recomp`

Run the same clean seeded matrix:

`pgrep -fl RogueSquadron64Recomp || true; zsh scratch/agent/run_s4321_m5_mort_output.sh`

Keep the same oracle/MORT/VI/filter controls. Do not alter RSP dispatch,
decoder, AI bridge, or add a game-path guard.
