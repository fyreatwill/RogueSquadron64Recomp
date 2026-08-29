# Session 3228 — retail route return-branch audit

## Work unit and discriminator

The competing hypotheses were `H-StateWriterAbsent` (the port has no
corresponding live route-edge writer/call), `H-StateWriterWrongValue` (the
edge runs with a different legitimate argument/state), and `H-StateOrdering`
(the values match but the consumer observes them on the wrong return/branch
side). The discriminator was a retail execution watch on
`reapplyDisplayMode` entry (`0x8008EB5C`), its `reapplyAudioConfig` call
(`0x8008EBC0`), and the return-branch instruction (`0x8008EBC8`), phase-gated
at the corrected 640 origins from Session 3227.

## Retail oracle

The run used Rice, the validated route `3:start,7:start,11:start,15:a,30:start,45:start`,
the whole-RDRAM positive-control watch, and both 640 buckets
`0x00696100` and `0x00790500`. The control reached 10,000 callbacks at 0.9
seconds. Retail reached the watched pre-title 640 phase at
`0x00790500`, then title VI 1024 at `0x00790400`; the run completed 45 seconds
cleanly with 2,649 VI callbacks.

Each watched PC fired once in the corrected bucket. The entry had
`$a0=0x5622`, `$a1/$a2=0x0F/0x0F`, `$v0=0`, and the call had
`$a0=0x80165ED0`, `$a1/$a2=0x0F/0x0F`, `$v0=0x20`. The return-branch watch
had `$a0=0x8014090E`, `$a1=0x8003DE1C`, `$a2=0`, `$v0=0`, with previous PC
`0x80091D38`. No watched execution was observed in the older
`0x00696100` bucket during this run.

## Result

The port’s independent route-state row at `0x0066A500` has the same return
arguments (`a0=0x8014090E`, `a1=0x8003DE1C`, `a2=0`) and `target=0`, so this
measurement does not select writer-absent, wrong-value, or ordering. It does
rule out treating the return branch itself as absent or as a differing-value
edge: the branch is live in retail and its observed result matches the port
row. The remaining mismatch is where the edge occurs, not its local return
behavior. No guest value, guard, ordering change, or mitigation was made.

Evidence: this run’s `s3228_m5_route_return_oracle.log` and the port captures
`scratch/agent/unblock-m5-route-20260829/{silent,image}.log`.

ORIGIN: no guest value was changed; the only conclusion is a phase-boundary
correction from an independent retail execution watch with a same-run
positive control.
