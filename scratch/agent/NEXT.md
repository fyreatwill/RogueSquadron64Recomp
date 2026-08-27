# NEXT work unit (s2500) — resolve generated kind=1 PCM-store callsites

HYPOTHESIS-ID: m5-generated-image-downstream-join

## Single work unit

Perform a bounded static census of the external/generated recompiled sources
for every callsite of `rs64_m5_pcm_writer_store`, using the candidate ranges
from s2498 and the AI ring root `0x801096B0` as the address set. Confirm each
store's guest PC, width, raw and physical destination, and whether it is in the
ring or candidate ranges. If the generated tree is unavailable, prove that
with an explicit path/status check and inspect the fixup source that would
generate it; do not add runtime fields or change behavior.

## Competing hypotheses and discriminator

- H-kind1-guest: generated `kind=1` stores identify a legitimate guest writer
  that reaches the AI ring or a candidate PCM range.
- H-kind1-absent: no generated callsite reaches those ranges, so the port
  writer remains absent at the static boundary.
- H-kind1-unresolved: callsites exist but their generated addresses or ring
  relation cannot be established from available sources.

The discriminator is one complete caller table with generated caller PC,
store width, raw and physical address, range class, ring slot, and the first
downstream AI-buffer consumer. A phase-independent guest-store chain selects
H-kind1-guest; a verified absence selects H-kind1-absent; incomplete or
ambiguous generated sources select H-kind1-unresolved.

## Exact commands

```sh
test -d RecompiledFuncs; printf 'RecompiledFuncs status=%s\n' "$?"
rg -n "rs64_m5_pcm_writer_store|0x167000|0x169B00|0x801096B0" . --glob '!build/**' --glob '!logs/**' --glob '!scratch/agent/soak_results/**'
rg -n "rs64_m5_pcm_writer_store|writer_store" tools patches src lib
```

Write the table and conclusion to
`scratch/agent/s2500_m5_kind1_writer_audit/audit.md`. No build is needed
unless the static census exposes a concrete missing caller or wrong kind.
