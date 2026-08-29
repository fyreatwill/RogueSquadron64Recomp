# NEXT work unit — ground-truth the route return caller at the corrected phase

HYPOTHESIS-ID: m5-port-route-boundary

Session 3228 watched entry, call, and return branch in one retail run. The
whole-RDRAM control passed; all three fired at 640 origin `0x00790500`, and
the return row (`a0=0x8014090E`, `a1=0x8003DE1C`, `a2=0`, `v0=0`) matched the
port’s `audio-return` row at `0x0066A500`. The branch is not the discriminator;
the remaining issue is the caller/phase boundary. See
`scratch/agent/s3228_m5_route_return_oracle.md` and `.log`.

## Competing hypotheses

- `H-StateWriterAbsent`: retail's route transition has no corresponding live
  caller/publication sequence in the port.
- `H-StateWriterWrongValue`: the port reaches the caller sequence with a
  different legitimate state or argument.
- `H-StateOrdering`: state matches, but caller-to-return ordering differs.

## Discriminator

Run the retail oracle with the same whole-RDRAM positive control and
`--watch-pc 0x80091D38,0x8008EB5C,0x8008EBC0,0x8008EBC8`, plus explicit phase
buckets `0x00696100:640` and `0x00790500:640`. Require 10,000 control
callbacks and title 1024. Compare the caller/entry/call/return sequence,
`$a0..$a3`, `$v0`, previous PCs, and VI origin against the port's existing
route-state and `audio-return` rows. A missing caller sequence selects
`H-StateWriterAbsent`; matching sequence with different legitimate state
selects `H-StateWriterWrongValue`; matching state with changed caller-to-return
order selects `H-StateOrdering`. Do not add port instrumentation until this
caller boundary is aligned.

## Exact start

Use the same core/ROM/Rice paths as Session 3228, `--secs 45`,
`--watch-write 0x0:0x800000 --hit-cap 10000`,
`--watch-pc 0x80091D38,0x8008EB5C,0x8008EBC0,0x8008EBC8`, both corrected
`--pc-phase-log-width` buckets, `--vi-trace`, and
`--press 3:start,7:start,11:start,15:a,30:start,45:start`.
