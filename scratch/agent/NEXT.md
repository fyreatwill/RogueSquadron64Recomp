# Next work unit

HYPOTHESIS-ID: m5-audio-route-retail-parity

Run one bounded retail/port publication join to test whether the selected
Factor5 route reprepare has the same first post-handoff task/source cadence in
retail. Keep the existing port capture controls and add no mitigation.

Competing hypotheses and discriminator:

1. H-retail-parity: retail shows a corresponding post-handoff audio task/source
   publication and comparable cadence.
2. H-port-only-cadence: retail reaches the handoff but lacks the corresponding
   publication or has a materially different first-publication boundary.
3. H-unresolved: the oracle route is not qualified or the whole-RDRAM control
   fails; select no behavior change.

Positive controls: oracle whole-RDRAM watch must fire, the port must reach
`0x00690400` and the following `0x00620400`, `update_screen` must advance, and
both sides must provide bounded task/source rows. The first post-handoff
publication and cadence table is the discriminator.

Exact baseline/source commands:

`tools/oracle/run_oracle.sh ... --watch-write 0x0:0x800000 ...` (use the
existing oracle recipe and a whole-RDRAM positive control), plus the current
port recipe below.

`cmake --build build --config Debug --target RogueSquadron64Recomp && zsh scratch/agent/s4923_mission_longevity.sh`

Inspect only bounded source windows plus
`scratch/agent/s4923_mission_longevity/summary.txt` and bounded `grep -a`
matches from `run.log`; kill any manual process with SIGKILL.
