# NEXT work unit (s2378) — M5 A1 flag-contract provenance

HYPOTHESIS-ID: m5-a1-flag-contract-provenance

## Work unit

Perform one bounded source/ABI audit of the `osRecvMesg` call at
`0x80001CB8`. Establish whether port `$a2=1` comes from the generated
delay-slot instruction, is changed by the recomp binding/host wrapper, or is a
call-site label mismatch. Do not change the flag or any game behavior.

## Competing hypotheses and discriminating measurement

- H-GeneratedFlag: generated `rs_free` emits `$a2=1` at the call and the port
  runtime preserves it.
- H-HostTranslation: generated code supplies `$a2=0`, but a recomp binding or
  wrapper changes it to `1` before `osRecvMesg`.
- H-LabelArtifact: the watched port runtime receive is not the same call as
  retail `0x80001CB8`.

The discriminator is one source-to-runtime table for the same call ordinal:
generated instruction/delay-slot operands at `0x80001CB4..0x80001CBC`, the
recomp binding argument values, the actual `osRecvMesg` implementation flag,
and the guest PC marker. H-GeneratedFlag is selected if source, binding, and
runtime all show `1`; H-HostTranslation if source/binding show `0` but runtime
shows `1`; H-LabelArtifact if the guest PC/ordinal cannot join the runtime row.

## Ground truth and exact commands

    read docs/F5-UCODE-REFERENCE.md and tools/oracle/README.md
    grep the generated `rs_free` body and binding definitions around `0x80001CB4..0x80001CBC`
    use the already qualified oracle watch at `0x80001CB8` as the independent `$a2` control
    build one source/runtime probe only if the static table cannot close the join
    run both port arms together; SIGKILL after the phase-4 marker

Expected result: the table must either prove the generated delay-slot flag is
the source of the port difference or identify an ABI translation boundary. A
null control or the unqualified retail queue-write watch must not be used as
evidence.
