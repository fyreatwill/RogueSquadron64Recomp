# NEXT work unit (s2485) — decode the later scheduler task descriptor

HYPOTHESIS-ID: m5-generated-alternate-equivalence

## Single work unit

Perform one static/data-layout audit of the stable later-task pointer
`0x800377C8`, then prepare the next capture boundary only if the audit
identifies the guest-word offsets needed to decode it. Do not change scheduler
behavior, add a NULL guard, remap audio/output, or treat the prior host-struct
cast as valid.

## Competing hypotheses

- H-DescriptorIsOSTask: `0x800377C8` is a normal guest `OSTask` descriptor and
  its correctly endian-decoded fields identify the later consumer.
- H-DescriptorIsWrapper: it is a scheduler-owned wrapper/message object whose
  fields must be interpreted by generated consumers rather than `OSTask` layout.
- H-UnresolvedDescriptor: the static tree does not expose enough reads/writes
  to distinguish the two layouts.

## Discriminator

The complete static census of reads/writes around `0x800377C8` and the
scheduler call arguments must show either a consistent OSTask field pattern,
wrapper-specific accesses, or no attributable field pattern. Those outcomes
select the three hypotheses respectively. The prior run's positive controls
and identity result are recorded in
`scratch/agent/s2484_m5_scheduler_identity/audit.md`.

## Exact command

```sh
rg -n '0x800377C8|0x80128C70|0x80128D38|osSpTaskLoad|osSpTaskStartGo' \
  ../N64Recomp/RecompiledFuncs src lib/N64ModernRuntime | head -260
```
