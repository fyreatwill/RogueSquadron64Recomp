# NEXT work unit — bounded ProducerMark call-chain audit

HYPOTHESIS-ID: m5-route-producer-mark-boundary

Perform one bounded static audit of the retail-grounded ProducerMark handoff
before adding or changing runtime behavior. Audit generated bodies, callers,
headers, overlay registration, and host route-prepare acceptance for
`0x8001BCE4`, callers `0x8000C628` and `0x8000BFE8`, and the already observed
port boundary at VI 640 / origin `0x0066A500`.

Competing hypotheses and the discriminator:

- H-PortProbeWrongEdge: the port has the ProducerMark code, but the existing
  candidate probe is attached to a different/generated fragment or never
  observes the real call boundary.
- H-PortCallerMissing: the port's generated call chain omits or misdispatches
  one of the retail predecessor classes before route acceptance.
- H-PortAcceptanceWrong: the call chain exists, but host route preparation
  rejects the valid producer handoff (`accepted=0`) at the 640 boundary.
- H-StaticInsufficient: generated/host sources do not expose a defensible
  correspondence; no behavior change is justified.

The single discriminator is a complete table for all three addresses: exact
generated symbol/body range, every direct caller and call target, overlay/TOML
registration, probe hook location, and route-prepare acceptance predicate.
H-ProbeWrongEdge selects only a corrected observational hook; H-CallerMissing
selects a caller/dispatch repair candidate; H-AcceptanceWrong selects the
acceptance edge for a later ground-truth-backed probe; H-StaticInsufficient
preserves the route-failure boundary and pivots to a new source. Do not build
or run unless the audit identifies a concrete, non-mitigation change; if it
does, ground truth is already established by s3041 and the change must carry
all A/B arms in one build.

Exact audit commands from the repo root:

    rg -n -C 35 '0x8001BCE4|0x8000C628|0x8000BFE8|func_8001BCE4|func_8000C628|func_8000BFE8' RecompiledFuncs src lib tools syms docs
    rg -n -C 20 '8001BCE4|8000C628|8000BFE8' /Users/williambuckley/Documents/Tools/rogue_squadron64
    git diff -- src lib RecompiledFuncs syms tools

Record the table and decision in `scratch/agent/s3042_m5_producer_mark_audit/`.
