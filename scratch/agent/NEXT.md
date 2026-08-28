# NEXT work unit (s2877) — m5-new-route-state-discriminator

HYPOTHESIS-ID: m5-new-route-state-discriminator

## Work unit

The s2876 port pair was route-invalid, so its zero state rows are not evidence.
Select one new port-side consumer of the `0x8006E4B4`-updated structure. First
qualify its retail writer/consumer ordering with the whole-RDRAM positive
control, then add all consumer/store counters in one regeneration-safe probe,
rebuild once, and run image/silent arms concurrently. Do not change behavior
or interpret downstream audio unless both arms reach title and hangar.

## Competing hypotheses and discriminator

- H-consumer-missing: retail shows the consumer ordering but the matching port
  consumer/store path is absent after route qualification.
- H-consumer-equivalent: retail and port show the same consumer ordering and
  state-span sequence in matching target phases.
- H-route-invalid: either positive control or the matching port pair fails to
  reach title and hangar, making consumer rows unevaluable.

The discriminator is one retail-vs-port phase table containing positive-control
count, title/hangar reachability, consumer rows, and state-span rows. Each
outcome selects one hypothesis above.

## Exact command

    sed -n '1,220p' tools/oracle/README.md
    # Run the retail preflight with --watch-write 0x0:0x800000,
    # --pc-phase-log-width title/hangar buckets, and the selected consumer PC;
    # only then add matching port probes and run both arms from build/.

Record the phase table under `scratch/agent/s2877_m5_route_state/`; use SIGKILL,
run from `build/`, and run `git diff --check` before committing.
