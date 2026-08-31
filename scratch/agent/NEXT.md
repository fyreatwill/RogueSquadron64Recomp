# NEXT work unit — M5 indirect consumer edge census

HYPOTHESIS-ID: m5-consumer-reachability-audit

Session 3352's same-run port controls were live through hangar, while all five
exact consumer-site markers were zero. This selects `H-PortConsumerIndirectGap`
for the qualified route; do not add a status workaround.

Competing hypotheses for the next unit:

- `H-PortConsumerIndirectGap`: retail executes the five bodies, but the port
  does not reach the corresponding generated entries.
- `H-PortConsumerGate`: the port reaches the entries, but its slot/status
  predicate prevents the downstream consumer work.
- `H-PortProbeMismatch`: the exact-site probe still misses the actual
  generated indirect consumer entries.

Discriminator: perform a bounded static census of every indirect call/table
edge into the five target bodies, using generated `jalr` sites and callback
registration data. A complete resolved edge to a target that is never reached
in the qualified port route selects a missing runtime edge; a complete edge
whose source is itself absent selects the upstream gate; unresolved generated
targets leave the probe-label hypothesis open. Do not build until the census
lists all candidate edges and the single discriminator for each outcome.

Exact preparation:

    rg -n "80094648|8009B5A8|8009B600|8009B85C|8009BDE8|jalr|LOOKUP_FUNC|registerSiCallback" /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs_*.c /Users/williambuckley/Documents/Tools/N64Recomp/RecompiledFuncs/funcs.h
    sed -n '1,220p' scratch/agent/s3352_m5_port_consumer_entry.md

Ground truth already passed in Session 3352; no new instrument is authorized
until the static census is complete.
