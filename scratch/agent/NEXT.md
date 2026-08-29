# NEXT work unit — ground-truth the route return branch at the corrected phase

HYPOTHESIS-ID: m5-port-route-boundary

Session 3227 showed the watched `reapplyDisplayMode` edge is live in retail,
but not at the port's `0x0066A500` phase: retail hits occur at 640 origins
`0x00696100` and `0x00790500`, then title 1024. The requested phase bucket was
therefore unevaluable, despite a valid positive control. See
`scratch/agent/s3227_m5_route_oracle.md` and `.log`.

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

Run the retail oracle first with the same whole-RDRAM positive control,
`--watch-pc 0x8008EB5C,0x8008EBC0,0x8008EBC8`, and explicit phase buckets for
`0x00696100:640` and `0x00790500:640`. Require the control threshold and title
1024. Compare bounded entry/call/return rows (`$a0..$a2`, `$v0`, VI origin)
with the port's phase-3 route call and phase-4 audio-return rows. A missing
corresponding port edge selects `H-StateWriterAbsent`; matching edge with
different legitimate args selects `H-StateWriterWrongValue`; matching args
with a differing return/branch edge selects `H-StateOrdering`. If alignment
remains impossible, stop and redesign the boundary rather than add fields.

No build or new port instrumentation is authorized until the oracle positive
control and title gate pass.

## Exact start

Use the same core/ROM/Rice paths as Session 3227, `--secs 45`,
`--watch-write 0x0:0x800000 --hit-cap 10000`, the two `--watch-pc` options,
`--watch-pc 0x8008EB5C,0x8008EBC0,0x8008EBC8`, both corrected
`--pc-phase-log-width` buckets, `--vi-trace`, and
`--press 3:start,7:start,11:start,15:a,30:start,45:start`.
