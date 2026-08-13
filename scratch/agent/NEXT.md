# NEXT work unit (independent parser-consumer evidence)

HYPOTHESIS-ID: m3-e9-consumer-ordering

Add one independent producer/consumer identity or queue-order trace for the
aligned-task population. Keep game logic, RDP behavior, and mitigation code
unchanged. Batch the trace into one Debug build and run the existing
phase-gated `s790_postsec2_reachability.sh` recipe once with its positive
controls. Do not treat a repeat of the s830 runtime event sequence as a second
line of evidence.

Competing hypotheses and the discriminating measurement:

- H-parser-filter-remains: an independent queue/identity join still shows
  lower authoritative parser advancement for the same aligned tasks.
- H-parser-join-population: the previous mismatch joined different task
  populations; independent task identity aligns the counts or exposes the
  mismatch.
- H-parser-writer-path: bridge E9 bytes are submitted in ranges that do not
  reach the RT64 consumer because of deferred or dropped queue work.

Discriminator: keyed producer task, submitted range, consumer epoch, and join
row with positive controls (`emit/raw/dispatch/match`). A result is
inconclusive if it lacks the positive controls or only repeats the s830
reset/fetch/join counter.

Expected commands: edit the telemetry source; run
`./submodule-patches/export.sh`; build with
`cmake --build build --config Debug --target RogueSquadron64Recomp`; run
`zsh scratch/agent/s790_postsec2_reachability.sh` once; inspect bounded marker
slices; update the ledger. Use SIGKILL behavior from the recipe and do not run
repeat soaks manually.
