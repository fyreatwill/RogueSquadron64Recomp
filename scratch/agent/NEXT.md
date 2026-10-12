# NEXT: audit the attached-mesh overlay NPC NULL/free idiom
HYPOTHESIS-ID: m3-attached-mesh-null-free-audit

The regeneration/fixup harness is qualified in a fresh copy. Do not rerun it
or mutate the live generated tree. M5 is conditionally closed in CURRENT-TRUTH;
the remaining bounded M3 item is the `attachedMeshOverlayNpcHandler` gap at
`0x80054344`.

Competing hypotheses and discriminator:

- H1: the handler's NULL/free path is already proven safe by an earlier guard
  or by a caller invariant; every reachable dereference/free has a proof.
- H2: one or more reachable paths use the pointer without a proof, requiring
  a regeneration-safe patch with an explicit writer/legitimacy analysis.
- H3: the address/function attribution is stale or the site is not present in
  the current generated source, so this item is not actionable.

The discriminating measurement is one whole-idiom census: locate the current
generated function and every load, field dereference, `rs_free`, and caller
edge around `0x80054344`; classify each site as guarded, caller-proven, dead,
or unproven. H1 requires proof for all sites, H2 requires at least one
reachable unproven site and a named writer, and H3 requires the function/site
to be absent or misattributed.

Exact read-only commands before any edit:

    rg -n "80054344|attachedMeshOverlayNpcHandler|rs_free" ../N64Recomp/RecompiledFuncs funcs* src lib tools
    grep -n "0x80054344" PORTING-STATE.md | tail -20

If H2 is selected, write the origin/writer and legitimacy into the audit,
then use the existing patches workflow; never hand-edit generated functions.
