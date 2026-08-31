# NEXT work unit — M5 dynamic consumer-pointer source census

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3353's static census found no direct or literal indirect generated edge
to `serviceVoicePoolFrame` or `accumulateVoiceSampleOffset`; only generic
register-loaded `jalr` sites remain. The companion symbol map independently
confirms the target identities. Keep `H-PortConsumerIndirectGap` selected for
the qualified route; do not add a status workaround.

Competing hypotheses for the next unit:

- `H-PortConsumerIndirectGap`: retail executes the five bodies, but the port
  does not reach the corresponding generated entries.
- `H-PortConsumerGate`: the port reaches the entries, but its slot/status
  predicate prevents the downstream consumer work.
- `H-PortProbeMismatch`: the exact-site probe still misses the actual
  generated indirect consumer entries.

Discriminator: first use the independent retail oracle to identify the source
slot/table and dynamic call-site target for the service and accumulator PCs,
with its whole-RDRAM control and hangar `512 @ 0x006AB400` control. Then, in
one build, capture the corresponding port source-slot value and dynamic
target at the same phase while retaining host/task/PCM and title/hangar
controls. A retail source/target pair absent in the port selects a missing
publication/dispatch edge; a matching pair with no consumer entry selects a
port gate; a matching entry with zero exact markers selects probe mismatch.
If retail cannot identify a source slot after its positive controls, stop and
record the edge as unresolved rather than instrumenting the port.

Ground-truth preparation:

    sed -n '1,220p' tools/oracle/README.md
    rg -n "80094648|8009B5A8|8009B600|8009B85C|8009BDE8|jalr|LOOKUP_FUNC|registerSiCallback" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c

Do not build until the retail source-slot measurement passes its whole-RDRAM
positive control and names the exact dynamic source/target relation.
