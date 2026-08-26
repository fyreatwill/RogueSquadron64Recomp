# NEXT work unit (s2449) — audit generated `rs_memset` call lowering

HYPOTHESIS-ID: m5-port-static-rsmemset-callsite

## Work unit

Perform a bounded static audit of all 88 generated `jal 0x800078E0` sites.
For each site, record the callsite, preceding instruction, delay-slot
instruction, and whether any generated statement writes `ctx->r31` between the
function entry and the direct `rs_memset` call. Compare the result with the
s2448 live caller table; do not change runtime behavior.

## Competing hypotheses and discriminator

- H-GeneratedJalWritesRA: generated lowering writes `ctx->r31` for the direct
  call, so s2448's zero is caused by a later overwrite.
- H-GeneratedDirectCallOmitsRA: none of the 88 direct call lowerings writes
  `ctx->r31`, explaining the live zero at both caller and entry.
- H-SiteSubsetWritesRA: only a subset writes `ctx->r31`; the static table
  identifies whether target-phase rows use that subset.

The discriminator is the complete 88-site static table, cross-checked against
s2448's positive-controlled live rows. Any site with a generated `ctx->r31`
write selects H-GeneratedJalWritesRA or H-SiteSubsetWritesRA; no writes at all
selects H-GeneratedDirectCallOmitsRA. No new run is needed unless the static
enumeration and live table disagree.

## Exact command

`python3 scratch/agent/audit_s2449_static_rsmemset_lowering.py`
