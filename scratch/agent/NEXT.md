# Next work unit: requalify the legacy M5 route

HYPOTHESIS-ID: m5-route-requalification-4022

Competing hypotheses:

- H1: the legacy 640-wide stop is a repeatable route failure independent of
  candidate watches, so another source-writer census is blocked.
- H2: the route failure is schedule-sensitive; a same-build route table again
  reaches legacy target phase and permits the next writer census.
- H3: declared/real also fails or retail controls fail, so the route recipe or
  environment is invalid and no port conclusion is allowed.

Discriminator: one same-build concurrent retail/declared-real/declared-silent/
legacy-real capture using the established route controls, phase-gated title and
hangar markers, RSP/audio-stage controls, and no candidate-PC watches or audio
behavior changes. H1 requires retail controls plus declared target phase and
legacy stop before target; H2 requires retail controls plus both real-audio
arms reaching target phases; H3 is any missing retail positive/title/hangar/
completion control or declared-arm failure. The result selects whether the
next unit may return to a retail-grounded writer census.

Commands: build once with
`cmake --build build --config Debug --target RogueSquadron64Recomp`, then run
`zsh scratch/agent/run_s4019_m5_route_qualification.sh` from the repository
root. The recipe launches all arms concurrently and kills them with SIGKILL.
