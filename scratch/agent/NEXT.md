# NEXT work unit (repair E9 callback/task join ordering)

HYPOTHESIS-ID: m3-e9-callback-task-ownership

Make one telemetry-only change: ensure the inline-data-aware walker’s
`rs64_e9prov_aligned(task_serial, dl_ptr, e9_aligned)` result is recorded after
the callback, or defer the `[e9-task-join]` report until after that callback.
Keep bridge/parser counters and game logic unchanged.

Competing hypotheses:

- H-post-callback-join: after reordering, the same task has
  `passed==current` and `aligned>0`; this confirms the join repair.
- H-serial-mismatch: the repaired row has differing callback/current serials;
  this reopens task ownership rather than parser accounting.
- H-callback-absent: no repaired row appears despite positive controls; this
  means the walker callback path is still not the observed producer.

Discriminating measurement: build once with the normal pipeline, then run:

    cmake --build build --config Debug --target RogueSquadron64Recomp
    zsh scratch/agent/s790_postsec2_reachability.sh

Use the existing VI-1024 phase gate and positive controls. A post-callback row
with matching serial and nonzero aligned count is the required result; do not
run a parser-loss experiment until it exists.
