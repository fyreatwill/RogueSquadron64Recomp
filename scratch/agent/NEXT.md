# NEXT: audit load_full_header_image rs_free idiom
HYPOTHESIS-ID: m3-load-full-header-rs-free-audit

The attached-mesh gap is statically confirmed but runtime occupancy is
unproven; do not add a guard. The next bounded M3 idiom unit is the remaining
`funcs_11.c` `load_full_header_image` free at `0x800544D8`.

Competing hypotheses and discriminator:

- H1: the free receives only the matching `get_asset_size_extra`/`rs_malloc`
  result, with all NULL and early-return paths safe.
- H2: a reachable path aliases another object, frees after a second release,
  or passes an uninitialized/non-allocator value; if so, name its writer and
  legitimacy before considering a regeneration-safe patch.
- H3: the address/function attribution is stale or the site is absent from the
  current fresh generated copy.

The discriminating measurement is one complete static census of the function's
pointer loads/stores, allocator calls, all caller edges, and every nearby
`rs_free` target. H1 requires a complete matching proof; H2 requires one
reachable unproven source and a named writer; H3 requires absence or
misattribution.

Read-only commands:

    rg -n -C 8 "load_full_header_image|0x800544D8|800544D8|rs_malloc|rs_free" ../N64Recomp/RecompiledFuncs.s4204-fresh/funcs_11.c
    rg -n -C 3 "load_full_header_image\(" ../N64Recomp/RecompiledFuncs.s4204-fresh --glob '*.c'
    rg -n "load_full_header_image|800544D8" ../rogue_squadron64/symbol_files ../rogue_squadron64/build
    grep -n "0x800544D8\|800544D8\|load_full_header_image" PORTING-STATE.md | tail -20

No build or runtime run is needed unless the census selects H2 and a patch
design can identify a legitimate writer.
