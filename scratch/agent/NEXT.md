# NEXT work unit — ground-truth the reapplyDisplayMode route edge

HYPOTHESIS-ID: m5-port-route-boundary

Session 3226 rejected the first watched fields: retail writes to
`0x80141AD0/1` and `0x8013B038` are early display/audio configuration stores
owned by `setDisplayMode`/`reapplyDisplayMode`, not the missing route
publication. See `scratch/agent/s3226_m5_route_writer_oracle/RESULTS.md`.

## Competing hypotheses

- `H-StateWriterAbsent`: retail's route transition has no corresponding live
  writer/call edge in the port.
- `H-StateWriterWrongValue`: the port reaches the route edge but supplies a
  different legitimate argument/state value.
- `H-StateOrdering`: the values match, but the port's consumer observes the
  publication on the wrong side of the `reapplyAudioConfig` return branch.

## Discriminator

Run the retail oracle first with `--watch-write 0x0:0x800000` as the positive
control and `--watch-pc 0x8008EB5C --watch-pc 0x8008EBC0`, plus
`--pc-phase-log-width 0x0066A500:640` and the validated route. Require the
whole-RDRAM threshold and retail title 1024. Compare the bounded execution
rows (`$a0..$a2`, `$v0`, VI phase) with the existing port route-state entry,
route, and audio-return rows. A retail edge absent in the port selects
`H-StateWriterAbsent`; matching edge with different args selects
`H-StateWriterWrongValue`; matching args with a differing return/branch edge
selects `H-StateOrdering`.

No build or new port instrumentation is authorized until the oracle positive
control and title gate pass.

## Exact start

Use the same core/ROM/Rice paths as Session 3226, `--secs 45`,
`--watch-write 0x0:0x800000 --hit-cap 10000`, the two `--watch-pc` options,
`--vi-trace`, and `--press 3:start,7:start,11:start,15:a,30:start,45:start`.
