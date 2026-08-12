# NEXT work unit (after s695 unqualified paired-frame reroll)

HYPOTHESIS-ID: m3-e9-provenance-cap

Consume the two queued, bounded phase-gated rerolls
`scratch/agent/soak_queue/s695_e9prov_frame_pairs_a.sh` and
`scratch/agent/soak_queue/s695_e9prov_frame_pairs_b.sh`. Do not rebuild or
alter the tracer unless the boot positive control fails.

## Competing hypotheses

- **H-extra-push:** a valid `0x06` takes a push path where Factor 5 semantics
  require a tail branch, accumulating the observed open frames.
- **H-missing-return:** valid `0x06` pushes occur, but EndDL/root return never
  completes their paired pop/resume.
- **H-game-open-chain:** the captured valid chain is still legitimately open
  when the synthetic cap ends the task.

## Discriminating measurement

For a section-2-latched cap task, first require the same-run boot controls:
task 1--4 must include at least one `w0=0x06000000` P→O→R triplet with one ID
and `dl06 ... open:0`. Then score target rows: excess P IDs or `open>0`
supports H-extra-push; P→O without R supports H-missing-return; complete
paired IDs with `open=0` supports H-game-open-chain. A run with no section-2
latch is unqualified and must remain a null result.

## Commands

    tail -20 scratch/agent/SOAK-RESULTS.md
    rg -n '\[e9-prov\]|\[e9-prov-frame\]|\[e9-prov-latch\]' scratch/agent/soak_results/*s695* | tail -240
    rg -n 'dl06=|scope=sec2|w0=0x06000000|\[CRASH\]' scratch/s73_post_a_scene/s670_postsec2_pulse_*20260812*/run.log | tail -240
