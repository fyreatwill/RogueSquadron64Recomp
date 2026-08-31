# NEXT work unit — attribute the port callback-table writer

HYPOTHESIS-ID: m5-callback-writer-attribution-after-reachability

Session 3333 showed retail reaches `initMusyXVoiceTable`, dispatches
`0x8009B5A8`, and reaches `0x8009BD7C`, while the port reaches the same target
phase but installs/dispatches `0x8009123C` and has no initializer/service/child
rows. Attribute the port-side writer/caller before considering any behavior
change.

## Competing hypotheses

- `H-PortCallbackWriterIsInit`: the port reaches `initMusyXVoiceTable`, but a
  wrong callback value is written at its registration site.
- `H-PortCallbackWriterIsOther`: another qualified caller writes
  `0x8009123C`, and the initializer is not the source of the mismatch.
- `H-PortCallbackWriterUnobserved`: callback-table polling misses a transient
  registration or the initializer/caller instrumentation is not on the live
  path.

## Discriminator

Ask the independent retail oracle first, retaining whole-RDRAM, callback-table
write, `0x80007910`, `0x80019B74`, `0x8009BBA0`, `0x8009B5A8`, and
`0x8009BD7C` controls. Then build one port instrument with entry/callsite marks
for `0x80066AA4 -> 0x8009BBA0`, the `0x8009BC50` registration call, and the
callback-table state poll, plus the existing slot/status controls. Phase-gate
at VI-512. Init plus registration-site rows with a wrong stored value select
`H-PortCallbackWriterIsInit`; callback-table writes without init rows select
`H-PortCallbackWriterIsOther`; no writer rows despite positive controls select
`H-PortCallbackWriterUnobserved`. Any missing positive control invalidates the
run and requires a fixed rerun in this iteration.

No Step 3 contract change or mitigation is authorized.
